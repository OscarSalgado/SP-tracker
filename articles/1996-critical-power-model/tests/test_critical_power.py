"""
Tests for critical power models.
"""

import numpy as np
import pytest
from src.critical_power import (
    ThreeParameterCPModel,
    fit_cp_model,
    hyperbolic_model_2param,
    hyperbolic_model_3param,
    power_from_pmax,
)


class TestHyperbolicModel2Param:
    """Tests for 2-parameter hyperbolic model."""

    def test_basic_calculation(self):
        """Test basic calculation: t = AWC / (P - CP)."""
        awc = 20000
        cp = 250
        power = 300

        t = hyperbolic_model_2param(power, awc, cp)
        expected = 20000 / (300 - 250)
        assert t == pytest.approx(expected)

    def test_array_input(self):
        """Test with array input."""
        awc = 20000
        cp = 250
        power = np.array([300, 350, 400])

        t = hyperbolic_model_2param(power, awc, cp)
        expected = awc / (power - cp)

        np.testing.assert_array_almost_equal(t, expected)

    def test_scalar_output_for_scalar_input(self):
        """Test that scalar input produces scalar output."""
        result = hyperbolic_model_2param(300, 20000, 250)
        assert isinstance(result, (float, np.floating))


class TestHyperbolicModel3Param:
    """Tests for 3-parameter hyperbolic model."""

    def test_basic_calculation(self):
        """Test basic calculation: t = AWC / (P - CP) + k."""
        awc = 20000
        cp = 250
        k = -50
        power = 300

        t = hyperbolic_model_3param(power, awc, cp, k)
        expected = 20000 / (300 - 250) + (-50)
        assert t == pytest.approx(expected)

    def test_3param_vs_2param_with_k_zero(self):
        """When k=0, 3-param should equal 2-param."""
        awc = 20000
        cp = 250
        power = 300

        t_2param = hyperbolic_model_2param(power, awc, cp)
        t_3param = hyperbolic_model_3param(power, awc, cp, k=0)

        assert t_2param == pytest.approx(t_3param)

    def test_negative_k_reduces_time(self):
        """Negative k reduces time to exhaustion."""
        awc = 20000
        cp = 250
        power = 300

        t_k0 = hyperbolic_model_3param(power, awc, cp, k=0)
        t_k_neg = hyperbolic_model_3param(power, awc, cp, k=-50)

        assert t_k_neg < t_k0

    def test_array_input(self):
        """Test with array input."""
        awc = 20000
        cp = 250
        k = -50
        power = np.array([300, 350, 400])

        t = hyperbolic_model_3param(power, awc, cp, k)
        expected = awc / (power - cp) + k

        np.testing.assert_array_almost_equal(t, expected)


class TestPowerFromPmax:
    """Tests for P_max parameterization."""

    def test_pmax_calculation(self):
        """Test power calculation from P_max parameterization."""
        awc = 20000
        cp = 250
        pmax = 600
        time = 400

        power = power_from_pmax(time, awc, cp, pmax)
        assert power > 0
        assert power < pmax

    def test_pmax_relationship(self):
        """Test relationship between k and P_max."""
        awc = 20000
        cp = 250
        k = -50

        pmax_expected = cp + awc / (-k)
        assert pmax_expected == pytest.approx(250 + 20000 / 50)


class TestThreeParameterCPModel:
    """Tests for ThreeParameterCPModel class."""

    def test_initialization(self):
        """Test model initialization."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50)
        assert model.awc == 20000
        assert model.cp == 250
        assert model.k == -50

    def test_initialization_with_errors(self):
        """Test initialization with standard errors."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50, awc_se=500, cp_se=10, k_se=5)
        assert model.awc_se == 500
        assert model.cp_se == 10
        assert model.k_se == 5

    def test_pmax_property(self):
        """Test P_max property calculation."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50)
        pmax = model.pmax
        expected = 250 + 20000 / 50
        assert pmax == pytest.approx(expected)

    def test_pmax_property_positive_k(self):
        """P_max is None for positive k."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=50)
        assert model.pmax is None

    def test_predict_single_value(self):
        """Test prediction for single power value."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50)
        t = model.predict(300)
        expected = hyperbolic_model_3param(300, 20000, 250, -50)
        assert t == pytest.approx(expected)

    def test_predict_array(self):
        """Test prediction for array of power values."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50)
        power = np.array([300, 350, 400])
        t = model.predict(power)
        expected = hyperbolic_model_3param(power, 20000, 250, -50)
        np.testing.assert_array_almost_equal(t, expected)

    def test_residuals(self):
        """Test residual calculation."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50)
        power = np.array([300, 350, 400])
        time_obs = np.array([410, 284, 214])

        residuals = model.residuals(power, time_obs)
        predicted = model.predict(power)

        np.testing.assert_array_almost_equal(residuals, time_obs - predicted)

    def test_rss(self):
        """Test residual sum of squares."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50)
        power = np.array([300, 350, 400])
        time_obs = np.array([410, 284, 214])

        rss = model.rss(power, time_obs)
        residuals = model.residuals(power, time_obs)

        assert rss == pytest.approx(np.sum(residuals**2))

    def test_rms(self):
        """Test residual mean square."""
        model = ThreeParameterCPModel(awc=20000, cp=250, k=-50)
        power = np.array([300, 350, 400])
        time_obs = np.array([410, 284, 214])

        rms = model.rms(power, time_obs)
        rss = model.rss(power, time_obs)

        assert rms == pytest.approx(rss / len(power))


class TestFitCPModel2Param:
    """Tests for 2-parameter model fitting."""

    def test_fit_2param_basic(self):
        """Test fitting 2-parameter model to synthetic data."""
        true_awc = 20000
        true_cp = 250

        power = np.array([280, 300, 320, 350])
        time = hyperbolic_model_2param(power, true_awc, true_cp)
        time += np.random.RandomState(42).normal(0, 5, len(time))

        result = fit_cp_model(power, time, model="2param")

        assert "model" in result
        assert "popt" in result
        assert "pcov" in result
        assert "residuals" in result
        assert "rss" in result
        assert "rms" in result

        model_dict = result["model"]
        assert model_dict["awc"] == pytest.approx(true_awc, rel=0.1)
        assert model_dict["cp"] == pytest.approx(true_cp, rel=0.1)

    def test_fit_2param_with_p0(self):
        """Test 2-parameter fit with initial guess."""
        power = np.array([280, 300, 320])
        time = np.array([410, 334, 286])

        result = fit_cp_model(power, time, model="2param", p0=[20000, 250])

        assert result["model"]["awc"] > 0
        assert result["model"]["cp"] > 0


class TestFitCPModel3Param:
    """Tests for 3-parameter model fitting."""

    def test_fit_3param_basic(self):
        """Test fitting 3-parameter model to synthetic data."""
        true_awc = 20000
        true_cp = 250
        true_k = -50

        power = np.array([270, 280, 300, 320, 350])
        time = hyperbolic_model_3param(power, true_awc, true_cp, true_k)
        time += np.random.RandomState(42).normal(0, 5, len(time))

        result = fit_cp_model(power, time, model="3param")

        assert isinstance(result["model"], ThreeParameterCPModel)
        assert result["model"].awc == pytest.approx(true_awc, rel=0.3)
        assert result["model"].cp == pytest.approx(true_cp, rel=0.3)
        assert result["model"].k < 0

    def test_fit_3param_with_weights(self):
        """Test 3-parameter fit with weighted least squares."""
        power = np.array([270, 280, 300, 320, 350])
        time = np.array([725, 580, 410, 307, 225])

        weights = time**2

        result = fit_cp_model(power, time, model="3param", weights=weights)

        model = result["model"]
        assert model.awc > 0
        assert model.cp > 0
        assert model.k < 0

    def test_fit_3param_with_p0(self):
        """Test 3-parameter fit with initial guess."""
        power = np.array([280, 300, 320, 350])
        time = np.array([410, 334, 286, 215])

        result = fit_cp_model(power, time, model="3param", p0=[20000, 250, -50])

        model = result["model"]
        assert model.awc > 0
        assert model.cp > 0

    def test_fit_3param_standard_errors(self):
        """Test that standard errors are computed."""
        power = np.array([280, 300, 320, 350])
        time = np.array([410, 334, 286, 215])

        result = fit_cp_model(power, time, model="3param")

        model = result["model"]
        assert model.awc_se is not None
        assert model.cp_se is not None
        assert model.k_se is not None
        assert model.awc_se > 0
        assert model.cp_se > 0


class TestFitCPModelErrors:
    """Tests for error handling in fit_cp_model."""

    def test_invalid_model_name(self):
        """Test error on invalid model name."""
        power = np.array([300, 350])
        time = np.array([410, 284])

        with pytest.raises(ValueError, match="Unknown model"):
            fit_cp_model(power, time, model="invalid")

    def test_fit_produces_residuals(self):
        """Test that fit produces residuals."""
        power = np.array([280, 300, 320])
        time = np.array([410, 334, 286])

        result = fit_cp_model(power, time, model="3param")

        assert result["residuals"] is not None
        assert len(result["residuals"]) == len(power)


class TestIntegration:
    """Integration tests comparing 2-param and 3-param models."""

    def test_3param_completes_fitting(self):
        """3-param model completes fitting without errors."""
        power = np.array([280, 290, 300, 320, 350])
        time = np.array([700, 600, 450, 320, 220])

        fit_3p = fit_cp_model(power, time, model="3param")

        assert fit_3p["rms"] >= 0
        assert fit_3p["rss"] >= 0
        assert len(fit_3p["residuals"]) == len(power)

    def test_3param_with_high_weights_triggers_fallback(self):
        """3-param with high weights and low maxfev triggers fallback path."""
        power = np.array([280, 290, 300, 320])
        time = np.array([700, 600, 450, 320])
        weights = time**3

        result = fit_cp_model(power, time, model="3param", weights=weights, maxfev=50)
        assert isinstance(result["model"], ThreeParameterCPModel)

    def test_fitted_model_can_predict(self):
        """Fitted model can be used for predictions."""
        power = np.array([270, 280, 300, 320])
        time = np.array([725, 580, 410, 307])

        result = fit_cp_model(power, time, model="3param")
        model = result["model"]

        new_power = 310
        predicted_time = model.predict(new_power)

        assert predicted_time > 0
        assert isinstance(predicted_time, (float, np.floating))

"""Tests para módulos de separación de vibración."""

import numpy as np
import torch
from src import DilatedCNN, VibrationSeparator, WhiteningBasedDeconvolution


class TestDilatedCNN:
    """Tests para CNN dilated."""

    def test_init_default(self):
        """Test inicialización con parámetros por defecto."""
        model = DilatedCNN()
        assert model.input_channels == 1
        assert model.output_channels == 1
        assert model.num_layers == 4

    def test_init_custom(self):
        """Test inicialización con parámetros personalizados."""
        model = DilatedCNN(input_channels=2, output_channels=3, num_layers=5)
        assert model.input_channels == 2
        assert model.output_channels == 3
        assert model.num_layers == 5

    def test_forward_shape(self):
        """Test que forward mantiene shape correcto."""
        model = DilatedCNN()
        batch_size, seq_len = 2, 256
        x = torch.randn(batch_size, 1, seq_len)
        out = model(x)
        assert out.shape == (batch_size, 1, seq_len)

    def test_forward_deterministic(self):
        """Test que forward es determinístico (dados mismos inputs)."""
        torch.manual_seed(42)
        model = DilatedCNN()
        x = torch.randn(1, 1, 256)
        out1 = model(x)
        out2 = model(x)
        assert torch.allclose(out1, out2)

    def test_predict_interface(self):
        """Test método predict (interfaz compatible)."""
        model = DilatedCNN()
        signal = [1.0, 2.0, 3.0, 4.0, 5.0] * 50
        output = model.predict(signal)
        assert len(output) == len(signal)
        assert isinstance(output, list)

    def test_layers_count(self):
        """Test número correcto de capas dilated."""
        model = DilatedCNN(num_layers=3)
        assert len(model.layers) == 3
        assert model.output_layer is not None


class TestWhiteningBasedDeconvolution:
    """Tests para WBD."""

    def test_init(self):
        """Test inicialización."""
        wbd = WhiteningBasedDeconvolution(fft_size=512, num_iterations=5)
        assert wbd.fft_size == 512
        assert wbd.num_iterations == 5

    def test_whiten_spectrum_output_shape(self):
        """Test que whiten_spectrum retorna shape correcto."""
        wbd = WhiteningBasedDeconvolution()
        signal = np.sin(2 * np.pi * np.arange(1000) / 100)
        whitened = wbd.whiten_spectrum(signal)
        assert len(whitened) == len(signal)

    def test_whiten_spectrum_values(self):
        """Test que whiten_spectrum produce valores válidos (sin NaN/Inf)."""
        wbd = WhiteningBasedDeconvolution()
        signal = np.random.randn(1000)
        whitened = wbd.whiten_spectrum(signal)
        assert not np.any(np.isnan(whitened))
        assert not np.any(np.isinf(whitened))

    def test_deconvolve_output_shape(self):
        """Test que deconvolve retorna shape correcto."""
        wbd = WhiteningBasedDeconvolution()
        signal = np.random.randn(1000)
        deconvolved = wbd.deconvolve(signal)
        assert len(deconvolved) == len(signal)

    def test_deconvolve_values(self):
        """Test que deconvolve produce valores válidos."""
        wbd = WhiteningBasedDeconvolution()
        signal = np.sin(2 * np.pi * np.arange(1000) / 100)
        deconvolved = wbd.deconvolve(signal)
        assert not np.any(np.isnan(deconvolved))
        assert not np.any(np.isinf(deconvolved))

    def test_estimate_transfer_function(self):
        """Test estimación de función de transferencia."""
        wbd = WhiteningBasedDeconvolution()
        signal = np.random.randn(1000)
        transfer_func = wbd.estimate_transfer_function(signal)
        assert len(transfer_func) == wbd.fft_size
        assert not np.any(np.isnan(transfer_func))

    def test_estimate_transfer_function_no_inf(self):
        """Test que estimate_transfer_function maneja divisiones por cero."""
        wbd = WhiteningBasedDeconvolution()
        signal = np.zeros(1000)
        signal[500:600] = 1.0
        transfer_func = wbd.estimate_transfer_function(signal)
        assert not np.any(np.isinf(transfer_func))


class TestVibrationSeparator:
    """Tests para pipeline de separación."""

    def test_init(self):
        """Test inicialización."""
        sep = VibrationSeparator(fft_size=512, num_cnn_layers=3)
        assert sep.fft_size == 512
        assert isinstance(sep.cnn, DilatedCNN)
        assert isinstance(sep.wbd, WhiteningBasedDeconvolution)

    def test_compute_envelope(self):
        """Test cálculo de envolvente."""
        sep = VibrationSeparator()
        signal = np.sin(2 * np.pi * np.arange(1000) / 100)
        envelope = sep.compute_envelope(signal)
        assert len(envelope) == len(signal)
        assert np.all(envelope >= 0)

    def test_compute_log_envelope(self):
        """Test cálculo de log-envolvente."""
        sep = VibrationSeparator()
        signal = np.sin(2 * np.pi * np.arange(1000) / 100) + 0.5
        log_env = sep.compute_log_envelope(signal)
        assert len(log_env) == len(signal)
        assert not np.any(np.isnan(log_env))

    def test_separate_sources_with_cnn(self):
        """Test separación usando CNN."""
        sep = VibrationSeparator()
        mixed = np.sin(2 * np.pi * np.arange(1000) / 50) + 0.3 * np.sin(
            2 * np.pi * np.arange(1000) / 200
        )
        result = sep.separate_sources(mixed, use_cnn_for_gear=True)

        assert "gear" in result
        assert "bearing" in result
        assert "residue" in result
        assert len(result["gear"]) == len(mixed)
        assert len(result["bearing"]) == len(mixed)
        assert len(result["residue"]) == len(mixed)

    def test_separate_sources_without_cnn(self):
        """Test separación sin CNN (usando envolvente)."""
        sep = VibrationSeparator()
        mixed = np.random.randn(500)
        result = sep.separate_sources(mixed, use_cnn_for_gear=False)

        assert "gear" in result
        assert "bearing" in result
        assert "residue" in result

    def test_separate_sources_values_valid(self):
        """Test que separación produce valores válidos."""
        sep = VibrationSeparator()
        mixed = np.sin(2 * np.pi * np.arange(1000) / 100)
        result = sep.separate_sources(mixed)

        for key in ["gear", "bearing", "residue"]:
            assert not np.any(np.isnan(result[key]))

    def test_get_cnn(self):
        """Test getter para CNN."""
        sep = VibrationSeparator()
        cnn = sep.get_cnn()
        assert isinstance(cnn, DilatedCNN)
        assert cnn is sep.cnn

    def test_get_deconvolution_model(self):
        """Test getter para WBD."""
        sep = VibrationSeparator()
        wbd = sep.get_deconvolution_model()
        assert isinstance(wbd, WhiteningBasedDeconvolution)
        assert wbd is sep.wbd

    def test_separate_sources_residue_consistency(self):
        """Test que residuo = mixed - gear."""
        sep = VibrationSeparator()
        mixed = np.random.randn(500)
        result = sep.separate_sources(mixed, use_cnn_for_gear=False)

        expected_residue = mixed - result["gear"]
        np.testing.assert_array_almost_equal(result["residue"], expected_residue)

    def test_separate_sources_with_cnn_large_signal(self):
        """Test separación con CNN en señal grande que requiere interpolación."""
        sep = VibrationSeparator(fft_size=512, num_cnn_layers=2)
        mixed = np.random.randn(5000)
        result = sep.separate_sources(mixed, use_cnn_for_gear=True)

        assert len(result["gear"]) == 5000
        assert len(result["bearing"]) == 5000
        assert len(result["residue"]) == 5000

    def test_separate_sources_bearing_interpolation(self):
        """Test que bearing interpola correctamente cuando FFT size es diferente."""
        sep = VibrationSeparator(fft_size=256)
        mixed = np.sin(2 * np.pi * np.arange(3000) / 100)
        result = sep.separate_sources(mixed, use_cnn_for_gear=False)

        assert len(result["bearing"]) == len(mixed)
        assert not np.any(np.isnan(result["bearing"]))

    def test_separate_sources_no_interpolation_needed(self):
        """Test cuando gear CNN retorna mismo tamaño (sin interpolación)."""
        sep = VibrationSeparator(fft_size=512, num_cnn_layers=2)
        small_mixed = np.sin(2 * np.pi * np.arange(512) / 100)
        result = sep.separate_sources(small_mixed, use_cnn_for_gear=True)

        assert len(result["gear"]) == len(small_mixed)
        assert len(result["bearing"]) == len(small_mixed)
        assert len(result["residue"]) == len(small_mixed)

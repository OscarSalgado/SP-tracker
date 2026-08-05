"""Tests para KAN-based bearing fault diagnosis."""

import numpy as np
import torch
from src import BearingFaultDiagnoser, KANFaultClassifier, KANLayer


class TestKANLayer:
    """Tests para KAN Layer."""

    def test_init(self):
        """Test inicialización."""
        layer = KANLayer(input_dim=32, output_dim=16, grid_size=5)
        assert layer.input_dim == 32
        assert layer.output_dim == 16

    def test_forward_shape(self):
        """Test shape de forward."""
        layer = KANLayer(input_dim=32, output_dim=16)
        x = torch.randn(4, 32)
        out = layer(x)
        assert out.shape == (4, 16)

    def test_parameter_count(self):
        """Test que existen parámetros."""
        layer = KANLayer(input_dim=32, output_dim=16)
        params = list(layer.parameters())
        assert len(params) > 0


class TestKANFaultClassifier:
    """Tests para KAN Fault Classifier."""

    def test_init(self):
        """Test inicialización."""
        clf = KANFaultClassifier(input_size=64, num_classes=5)
        assert clf.input_size == 64
        assert clf.num_classes == 5

    def test_forward_shape(self):
        """Test shape de forward."""
        clf = KANFaultClassifier(input_size=64, num_classes=5)
        x = torch.randn(2, 64)
        out = clf(x)
        assert out.shape == (2, 5)

    def test_forward_output_logits(self):
        """Test que output son logits sin softmax."""
        clf = KANFaultClassifier(input_size=64, num_classes=5)
        x = torch.randn(2, 64)
        out = clf(x)
        assert not torch.allclose(out.sum(dim=1), torch.ones(2))

    def test_predict(self):
        """Test predict."""
        clf = KANFaultClassifier(input_size=64, num_classes=5)
        features = np.random.randn(64)
        fault_class = clf.predict(features)
        assert 0 <= fault_class < 5

    def test_predict_different_seeds(self):
        """Test predict con diferentes características."""
        clf = KANFaultClassifier(input_size=64, num_classes=5)
        for _ in range(5):
            features = np.random.randn(64)
            fault_class = clf.predict(features)
            assert isinstance(fault_class, (int, np.integer))


class TestBearingFaultDiagnoser:
    """Tests para BearingFaultDiagnoser."""

    def test_init(self):
        """Test inicialización."""
        diagnoser = BearingFaultDiagnoser(input_size=64)
        assert diagnoser.input_size == 64

    def test_extract_features(self):
        """Test extracción de características."""
        diagnoser = BearingFaultDiagnoser(input_size=64)
        signal = np.random.randn(2000)
        features = diagnoser.extract_features(signal)
        assert len(features) == 64
        assert not np.any(np.isnan(features))

    def test_extract_features_short_signal(self):
        """Test características con señal corta."""
        diagnoser = BearingFaultDiagnoser(input_size=64)
        signal = np.random.randn(512)
        features = diagnoser.extract_features(signal)
        assert len(features) <= 64

    def test_diagnose(self):
        """Test diagnóstico completo."""
        diagnoser = BearingFaultDiagnoser(input_size=64)
        signal = np.sin(2 * np.pi * np.arange(2000) / 100) + 0.1 * np.random.randn(2000)
        result = diagnoser.diagnose(signal)

        assert "features" in result
        assert "fault_class" in result
        assert "fault_name" in result
        assert 0 <= result["fault_class"] < 5

    def test_diagnose_fault_names(self):
        """Test que nombres de fallo son válidos."""
        diagnoser = BearingFaultDiagnoser(input_size=64)
        signal = np.random.randn(1000)
        result = diagnoser.diagnose(signal)

        valid_names = ["Healthy", "Inner Race", "Outer Race", "Ball", "Combination"]
        assert result["fault_name"] in valid_names

    def test_diagnose_different_lengths(self):
        """Test con señales de diferente longitud."""
        diagnoser = BearingFaultDiagnoser(input_size=64)
        for length in [512, 1000, 3000, 5000]:
            signal = np.random.randn(length)
            result = diagnoser.diagnose(signal)
            assert len(result["features"]) <= 64
            assert result["fault_class"] >= 0

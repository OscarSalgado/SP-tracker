"""Tests para ClassifierGuidedBD."""

import numpy as np
import torch
from src import (
    ClassifierGuidedBD,
    FaultClassifier,
    NeuralBlindDeconvolution,
    QuadraticCNN,
)


class TestQuadraticCNN:
    """Tests para Quadratic CNN."""

    def test_init(self):
        """Test inicialización."""
        model = QuadraticCNN(num_layers=3, kernel_size=5)
        assert model.num_layers == 3
        assert model.kernel_size == 5

    def test_forward_shape(self):
        """Test shape de forward."""
        model = QuadraticCNN()
        x = torch.randn(2, 1, 512)
        out = model(x)
        assert out.shape == (2, 1, 512)

    def test_predict(self):
        """Test método predict."""
        model = QuadraticCNN()
        signal = [1.0, 2.0, 3.0] * 50
        out = model.predict(signal)
        assert len(out) == len(signal)


class TestNeuralBlindDeconvolution:
    """Tests para Neural BD."""

    def test_init(self):
        """Test inicialización."""
        nbd = NeuralBlindDeconvolution(temporal_length=64, fft_size=256)
        assert nbd.fft_size == 256

    def test_deconvolve(self):
        """Test deconvolución."""
        nbd = NeuralBlindDeconvolution()
        signal = np.random.randn(1000)
        result = nbd.deconvolve(signal)
        assert len(result) <= len(signal)
        assert not np.any(np.isnan(result))


class TestFaultClassifier:
    """Tests para clasificador."""

    def test_init(self):
        """Test inicialización."""
        clf = FaultClassifier(input_size=64, num_classes=4)
        assert len(list(clf.parameters())) > 0

    def test_forward(self):
        """Test forward."""
        clf = FaultClassifier()
        x = torch.randn(2, 64)
        out = clf(x)
        assert out.shape == (2, 4)

    def test_predict(self):
        """Test predict."""
        clf = FaultClassifier()
        features = np.random.randn(64)
        fault_class = clf.predict(features)
        assert 0 <= fault_class < 4


class TestClassifierGuidedBD:
    """Tests para ClassBD."""

    def test_init(self):
        """Test inicialización."""
        cbd = ClassifierGuidedBD()
        assert isinstance(cbd.quadratic_cnn, QuadraticCNN)
        assert isinstance(cbd.classifier, FaultClassifier)

    def test_extract_features(self):
        """Test extracción de características."""
        cbd = ClassifierGuidedBD()
        signal = np.random.randn(2000)
        features = cbd.extract_features(signal)
        assert len(features) == 64
        assert not np.any(np.isnan(features))

    def test_diagnose(self):
        """Test diagnóstico completo."""
        cbd = ClassifierGuidedBD()
        signal = np.sin(2 * np.pi * np.arange(2000) / 100) + 0.1 * np.random.randn(2000)
        result = cbd.diagnose(signal)

        assert "deconvolved_signal" in result
        assert "features" in result
        assert "fault_class" in result
        assert "fault_name" in result
        assert 0 <= result["fault_class"] < 4

    def test_diagnose_different_lengths(self):
        """Test con señales de diferente longitud."""
        cbd = ClassifierGuidedBD()
        for length in [512, 1000, 3000]:
            signal = np.random.randn(length)
            result = cbd.diagnose(signal)
            assert len(result["features"]) == 64

    def test_getters(self):
        """Test getters."""
        cbd = ClassifierGuidedBD()
        assert cbd.get_quadratic_cnn() is cbd.quadratic_cnn
        assert cbd.get_classifier() is cbd.classifier

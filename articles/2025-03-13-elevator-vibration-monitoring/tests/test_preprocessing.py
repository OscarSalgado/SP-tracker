"""Tests para preprocesamiento de señales de vibración."""

import numpy as np
import pytest
import torch
from src.preprocessing import CWTTransform, ElevatorDataPreprocessor


class TestCWTTransform:
    def test_initialization(self):
        cwt = CWTTransform(frequencies=(0, 100), num_scales=32, wavelet="morl")
        assert cwt.num_scales == 32
        assert cwt.frequencies == (0, 100)

    def test_cwt_transform_shape(self):
        cwt = CWTTransform(num_scales=32)
        signal_data = np.random.randn(4096)
        result = cwt(signal_data)
        assert result.shape == (32, 4096)

    def test_cwt_transform_output_type(self):
        cwt = CWTTransform(num_scales=32)
        signal_data = np.random.randn(4096)
        result = cwt(signal_data)
        assert isinstance(result, np.ndarray)

    def test_cwt_normalize(self):
        cwt = CWTTransform(num_scales=32)
        spectrogram = np.random.randn(32, 256)
        normalized = cwt.normalize(spectrogram)
        assert normalized.min() >= 0
        assert normalized.max() <= 1

    def test_cwt_normalize_uniform_spectrum(self):
        cwt = CWTTransform(num_scales=32)
        spectrogram = np.ones((32, 256))
        normalized = cwt.normalize(spectrogram)
        assert np.allclose(normalized, spectrogram)

    def test_cwt_with_different_scales(self):
        for num_scales in [16, 32, 64]:
            cwt = CWTTransform(num_scales=num_scales)
            signal_data = np.random.randn(1024)
            result = cwt(signal_data)
            assert result.shape[0] == num_scales


class TestElevatorDataPreprocessor:
    def test_initialization(self):
        prep = ElevatorDataPreprocessor(
            sampling_rate=12000,
            window_size=4096,
            overlap=0.5,
        )
        assert prep.sampling_rate == 12000
        assert prep.window_size == 4096
        assert prep.overlap == 0.5

    def test_segment_signal(self):
        prep = ElevatorDataPreprocessor(window_size=1024, overlap=0.5)
        signal = np.random.randn(8192)
        segments = prep.segment_signal(signal)
        assert len(segments) > 0
        assert all(len(seg) == 1024 for seg in segments)

    def test_segment_signal_short_signal(self):
        prep = ElevatorDataPreprocessor(window_size=2048, overlap=0.5)
        signal = np.random.randn(1000)
        segments = prep.segment_signal(signal)
        assert len(segments) == 0

    def test_process_signal(self):
        prep = ElevatorDataPreprocessor(window_size=2048, overlap=0.5)
        signal = np.random.randn(16384)
        result = prep.process(signal)
        assert isinstance(result, torch.Tensor)
        assert result.dtype == torch.float32
        assert len(result.shape) == 3
        assert result.shape[0] > 0

    def test_process_signal_shape(self):
        prep = ElevatorDataPreprocessor(window_size=2048, overlap=0.5)
        signal = np.random.randn(16384)
        result = prep.process(signal)
        assert result.shape[1] == 32
        assert result.shape[2] == 2048

    def test_create_rgb_image(self):
        spectrogram = np.random.rand(32, 256)
        rgb = ElevatorDataPreprocessor.create_rgb_image(spectrogram)
        assert rgb.shape == (3, 32, 256)
        assert rgb.dtype == np.float32

    def test_create_rgb_image_invalid_input(self):
        with pytest.raises(ValueError):
            ElevatorDataPreprocessor.create_rgb_image(np.random.randn(32, 256, 3))

    def test_create_rgb_image_values_match(self):
        spectrogram = np.ones((16, 128))
        rgb = ElevatorDataPreprocessor.create_rgb_image(spectrogram)
        assert np.allclose(rgb[0], spectrogram)
        assert np.allclose(rgb[1], spectrogram)
        assert np.allclose(rgb[2], spectrogram)

    def test_preprocess_pipeline(self):
        prep = ElevatorDataPreprocessor(window_size=2048, overlap=0.5)
        signal = np.random.randn(16384)
        spectrograms = prep.process(signal)
        first_spec = spectrograms[0].numpy()
        rgb = ElevatorDataPreprocessor.create_rgb_image(first_spec)
        assert rgb.shape == (3, 32, 2048)

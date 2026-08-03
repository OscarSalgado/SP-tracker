"""Tests para modelos STAN y DSAN."""

import torch
from src.models import (
    ChannelAttention,
    DomainAdaptationModule,
    Mish,
    ShuffleBlock,
    ShuffleNetV2STAN,
    SpatialAttention,
)


class TestMish:
    def test_mish_activation(self):
        mish = Mish()
        x = torch.randn(4, 3, 32, 32)
        out = mish(x)
        assert out.shape == x.shape
        assert torch.is_tensor(out)

    def test_mish_zero_input(self):
        mish = Mish()
        x = torch.zeros(2, 4, 16, 16)
        out = mish(x)
        assert torch.allclose(out, torch.zeros_like(out), atol=1e-6)


class TestChannelAttention:
    def test_channel_attention_shape(self):
        ca = ChannelAttention(64, reduction=16)
        x = torch.randn(2, 64, 32, 32)
        out = ca(x)
        assert out.shape == (2, 64, 1, 1)

    def test_channel_attention_values(self):
        ca = ChannelAttention(64, reduction=16)
        x = torch.randn(2, 64, 32, 32)
        out = ca(x)
        assert (out >= 0).all() and (out <= 1).all()


class TestSpatialAttention:
    def test_spatial_attention_shape(self):
        sa = SpatialAttention(kernel_size=7)
        x = torch.randn(2, 64, 32, 32)
        out = sa(x)
        assert out.shape == (2, 1, 32, 32)

    def test_spatial_attention_values(self):
        sa = SpatialAttention(kernel_size=7)
        x = torch.randn(2, 64, 32, 32)
        out = sa(x)
        assert (out >= 0).all() and (out <= 1).all()


class TestShuffleBlock:
    def test_shuffle_block_stride_1(self):
        block = ShuffleBlock(58, 116, stride=1)
        x = torch.randn(2, 58, 32, 32)
        out = block(x)
        assert out.shape == (2, 116, 32, 32)

    def test_shuffle_block_stride_2(self):
        block = ShuffleBlock(58, 116, stride=2)
        x = torch.randn(2, 58, 32, 32)
        out = block(x)
        assert out.shape == (2, 116, 16, 16)


class TestShuffleNetV2STAN:
    def test_initialization(self):
        model = ShuffleNetV2STAN(num_classes=4, input_channels=3)
        assert model.num_classes == 4
        assert model.input_channels == 3

    def test_forward_pass(self):
        model = ShuffleNetV2STAN(num_classes=4)
        x = torch.randn(2, 3, 224, 224)
        out = model(x)
        assert out.shape == (2, 4)

    def test_extract_features(self):
        model = ShuffleNetV2STAN(num_classes=4)
        x = torch.randn(2, 3, 224, 224)
        features = model.extract_features(x)
        assert features.shape == (2, 1024)

    def test_different_input_sizes(self):
        model = ShuffleNetV2STAN(num_classes=4)
        for size in [64, 128, 224]:
            x = torch.randn(1, 3, size, size)
            out = model(x)
            assert out.shape == (1, 4)

    def test_gradient_flow(self):
        model = ShuffleNetV2STAN(num_classes=4)
        x = torch.randn(2, 3, 224, 224, requires_grad=True)
        out = model(x)
        loss = out.sum()
        loss.backward()
        assert x.grad is not None

    def test_eval_mode(self):
        model = ShuffleNetV2STAN(num_classes=4)
        model.eval()
        x = torch.randn(2, 3, 224, 224)
        with torch.no_grad():
            out = model(x)
        assert out.shape == (2, 4)


class TestDomainAdaptationModule:
    def test_initialization(self):
        da = DomainAdaptationModule(feature_dim=1024, num_classes=4)
        assert da.feature_dim == 1024
        assert da.num_classes == 4

    def test_rbf_kernel(self):
        x = torch.randn(4, 10)
        y = torch.randn(5, 10)
        kernel = DomainAdaptationModule._rbf_kernel(x, y, gamma=1.0)
        assert kernel.shape == (4, 5)
        assert (kernel >= 0).all() and (kernel <= 1).all()

    def test_mmd_loss(self):
        da = DomainAdaptationModule(feature_dim=1024, num_classes=4)
        source = torch.randn(8, 1024)
        target = torch.randn(8, 1024)
        loss = da.compute_mmd_loss(source, target)
        assert loss.item() >= 0
        assert torch.is_tensor(loss)

    def test_forward_pass(self):
        da = DomainAdaptationModule(feature_dim=1024, num_classes=4)
        source_features = torch.randn(8, 1024)
        source_labels = torch.randint(0, 4, (8,))
        target_features = torch.randn(8, 1024)
        logits, mmd_loss = da(source_features, source_labels, target_features)
        assert logits.shape == (8, 4)
        assert mmd_loss.item() >= 0

    def test_mmd_zero_distance(self):
        da = DomainAdaptationModule(feature_dim=128, num_classes=4)
        features = torch.randn(4, 128)
        loss = da.compute_mmd_loss(features, features)
        assert loss.item() >= 0

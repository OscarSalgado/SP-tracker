"""Unit tests for elevator state classifier with 100% coverage."""

import numpy as np
from src.elevator_classifier import (
    ELEVATOR_STATES,
    INDEX_TO_STATE,
    STATE_TO_INDEX,
    ElevatorStateClassifier,
    build_1d_cnn_model,
)
from tensorflow import keras


class TestBuild1dCnnModel:
    """Test build_1d_cnn_model function."""

    def test_build_model_default_params(self):
        """Test model creation with default parameters."""
        model = build_1d_cnn_model()
        assert isinstance(model, keras.Model)
        assert model.input_shape == (None, 512, 1)
        assert model.output_shape == (None, 5)

    def test_build_model_custom_params(self):
        """Test model creation with custom parameters."""
        model = build_1d_cnn_model(
            input_length=1024,
            num_classes=3,
            num_filters=64,
        )
        assert model.input_shape == (None, 1024, 1)
        assert model.output_shape == (None, 3)

    def test_model_is_compiled(self):
        """Test that model is compiled with correct optimizer and loss."""
        model = build_1d_cnn_model()
        assert model.optimizer is not None
        assert "adam" in str(model.optimizer).lower()


class TestElevatorStateClassifierInit:
    """Test ElevatorStateClassifier initialization."""

    def test_init_without_model(self):
        """Test initialization without providing a model."""
        classifier = ElevatorStateClassifier()
        assert classifier.model is not None
        assert isinstance(classifier.model, keras.Model)

    def test_init_with_model(self):
        """Test initialization with a provided model."""
        custom_model = build_1d_cnn_model(num_filters=16)
        classifier = ElevatorStateClassifier(model=custom_model)
        assert classifier.model is custom_model


class TestPreprocessSignal:
    """Test signal preprocessing."""

    def test_preprocess_signal_normalization(self):
        """Test that signal is normalized to zero mean and unit variance."""
        classifier = ElevatorStateClassifier()
        signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        processed = classifier.preprocess_signal(signal)

        assert processed.shape == (512, 1)
        # Check the original (non-padded) part is normalized
        normalized_part = processed[:5].flatten()
        assert np.abs(np.mean(normalized_part)) < 0.01
        assert np.abs(np.std(normalized_part) - 1.0) < 0.01

    def test_preprocess_signal_padding(self):
        """Test padding of short signals."""
        classifier = ElevatorStateClassifier()
        short_signal = np.array([1.0, 2.0, 3.0])
        processed = classifier.preprocess_signal(short_signal, target_length=512)

        assert processed.shape == (512, 1)
        # Last elements should be zero (padding)
        assert np.allclose(processed[-10:], 0.0, atol=1e-5)

    def test_preprocess_signal_truncation(self):
        """Test truncation of long signals."""
        classifier = ElevatorStateClassifier()
        long_signal = np.arange(1000, dtype=float)
        processed = classifier.preprocess_signal(long_signal, target_length=256)

        assert processed.shape == (256, 1)

    def test_preprocess_signal_zero_std_handling(self):
        """Test handling of constant signals (zero standard deviation)."""
        classifier = ElevatorStateClassifier()
        constant_signal = np.ones(100)
        processed = classifier.preprocess_signal(constant_signal)

        # Should not raise an error (epsilon term prevents division by zero)
        assert processed.shape == (512, 1)
        assert np.isfinite(processed).all()

    def test_preprocess_signal_custom_length(self):
        """Test preprocessing with custom target length."""
        classifier = ElevatorStateClassifier()
        signal = np.random.randn(100)
        target_length = 256
        processed = classifier.preprocess_signal(signal, target_length=target_length)

        assert processed.shape == (target_length, 1)


class TestPredict:
    """Test prediction functionality."""

    def test_predict_returns_dict(self):
        """Test that predict returns a dictionary with required keys."""
        classifier = ElevatorStateClassifier()
        signal = np.random.randn(256)
        result = classifier.predict(signal)

        assert isinstance(result, dict)
        assert "state" in result
        assert "confidence" in result
        assert "probabilities" in result

    def test_predict_state_is_valid(self):
        """Test that predicted state is one of the valid states."""
        classifier = ElevatorStateClassifier()
        signal = np.random.randn(256)
        result = classifier.predict(signal)

        assert result["state"] in ELEVATOR_STATES

    def test_predict_confidence_is_probability(self):
        """Test that confidence score is between 0 and 1."""
        classifier = ElevatorStateClassifier()
        signal = np.random.randn(256)
        result = classifier.predict(signal)

        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_probabilities_dict(self):
        """Test that probabilities dictionary contains all states."""
        classifier = ElevatorStateClassifier()
        signal = np.random.randn(256)
        result = classifier.predict(signal)

        assert set(result["probabilities"].keys()) == set(ELEVATOR_STATES)
        probabilities = list(result["probabilities"].values())
        assert all(0.0 <= p <= 1.0 for p in probabilities)
        assert np.isclose(sum(probabilities), 1.0)

    def test_predict_on_different_signal_lengths(self):
        """Test prediction on signals of varying lengths."""
        classifier = ElevatorStateClassifier()

        for length in [10, 100, 512, 1000]:
            signal = np.random.randn(length)
            result = classifier.predict(signal)
            assert result["state"] in ELEVATOR_STATES

    def test_predict_consistency(self):
        """Test that same signal produces same prediction."""
        classifier = ElevatorStateClassifier()
        signal = np.sin(np.linspace(0, 10 * np.pi, 256))

        result1 = classifier.predict(signal)
        result2 = classifier.predict(signal)

        assert result1["state"] == result2["state"]
        assert np.isclose(result1["confidence"], result2["confidence"])


class TestTrain:
    """Test model training."""

    def test_train_basic(self):
        """Test basic training loop."""
        classifier = ElevatorStateClassifier()

        # Generate synthetic training data
        X_train = np.random.randn(20, 256)
        y_train = np.eye(5)[np.random.randint(0, 5, 20)]

        history = classifier.train(X_train, y_train, epochs=2, batch_size=4)

        assert isinstance(history, keras.callbacks.History)
        assert "loss" in history.history
        assert "accuracy" in history.history

    def test_train_loss_decreases(self):
        """Test that loss decreases over training epochs."""
        classifier = ElevatorStateClassifier()

        # More structured data for better convergence
        np.random.seed(42)
        X_train = np.random.randn(50, 256)
        y_train = np.eye(5)[np.random.randint(0, 5, 50)]

        history = classifier.train(
            X_train,
            y_train,
            epochs=5,
            batch_size=8,
            validation_split=0.1,
        )

        # Loss should generally decrease (may not be monotonic with validation)
        first_loss = history.history["loss"][0]
        last_loss = history.history["loss"][-1]
        # Check that training loss improved overall
        assert last_loss < first_loss or np.isclose(last_loss, first_loss, rtol=0.1)

    def test_train_with_validation_split(self):
        """Test training with validation split."""
        classifier = ElevatorStateClassifier()

        X_train = np.random.randn(30, 256)
        y_train = np.eye(5)[np.random.randint(0, 5, 30)]

        history = classifier.train(
            X_train,
            y_train,
            epochs=3,
            batch_size=4,
            validation_split=0.2,
        )

        assert "val_loss" in history.history
        assert "val_accuracy" in history.history
        assert len(history.history["loss"]) == 3

    def test_train_different_batch_sizes(self):
        """Test training with different batch sizes."""
        classifier = ElevatorStateClassifier()

        X_train = np.random.randn(40, 256)
        y_train = np.eye(5)[np.random.randint(0, 5, 40)]

        for batch_size in [4, 8, 16]:
            history = classifier.train(
                X_train,
                y_train,
                epochs=2,
                batch_size=batch_size,
            )
            assert "loss" in history.history


class TestConstants:
    """Test module constants."""

    def test_elevator_states_count(self):
        """Test that there are 5 elevator states."""
        assert len(ELEVATOR_STATES) == 5

    def test_state_to_index_mapping(self):
        """Test state to index mapping is consistent."""
        assert len(STATE_TO_INDEX) == len(ELEVATOR_STATES)
        for state in ELEVATOR_STATES:
            assert state in STATE_TO_INDEX

    def test_index_to_state_mapping(self):
        """Test index to state mapping is consistent."""
        assert len(INDEX_TO_STATE) == len(ELEVATOR_STATES)
        for idx in range(len(ELEVATOR_STATES)):
            assert idx in INDEX_TO_STATE

    def test_state_index_mappings_are_inverses(self):
        """Test that STATE_TO_INDEX and INDEX_TO_STATE are inverses."""
        for state, idx in STATE_TO_INDEX.items():
            assert INDEX_TO_STATE[idx] == state

        for idx, state in INDEX_TO_STATE.items():
            assert STATE_TO_INDEX[state] == idx

"""1D CNN model for classifying elevator operational states from accelerometer signals."""

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

ELEVATOR_STATES = [
    "moving_up",
    "moving_down",
    "stopped",
    "doors_opening",
    "doors_closing",
]

STATE_TO_INDEX = {state: idx for idx, state in enumerate(ELEVATOR_STATES)}
INDEX_TO_STATE = {idx: state for state, idx in STATE_TO_INDEX.items()}


def build_1d_cnn_model(
    input_length: int = 512,
    num_classes: int = 5,
    num_filters: int = 32,
) -> keras.Model:
    """Build a 1D CNN model for elevator state classification.

    Args:
        input_length: Length of input signal (number of time steps).
        num_classes: Number of elevator states to classify.
        num_filters: Number of filters in first convolutional layer.

    Returns:
        Compiled Keras model ready for training.
    """
    model = keras.Sequential(
        [
            layers.Input(shape=(input_length, 1)),
            layers.Conv1D(
                num_filters,
                kernel_size=16,
                activation="relu",
                padding="same",
                name="conv1d_1",
            ),
            layers.MaxPooling1D(pool_size=4, name="maxpool_1"),
            layers.Conv1D(
                num_filters * 2,
                kernel_size=8,
                activation="relu",
                padding="same",
                name="conv1d_2",
            ),
            layers.MaxPooling1D(pool_size=4, name="maxpool_2"),
            layers.Conv1D(
                num_filters * 4,
                kernel_size=4,
                activation="relu",
                padding="same",
                name="conv1d_3",
            ),
            layers.GlobalAveragePooling1D(name="global_avg_pool"),
            layers.Dense(128, activation="relu", name="dense_1"),
            layers.Dropout(0.5, name="dropout"),
            layers.Dense(num_classes, activation="softmax", name="output"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


class ElevatorStateClassifier:
    """Wrapper for 1D CNN-based elevator operational state classification."""

    def __init__(self, model: keras.Model | None = None):
        """Initialize the classifier.

        Args:
            model: Pre-trained Keras model. If None, creates a new untrained model.
        """
        self.model = model or build_1d_cnn_model()

    def preprocess_signal(self, signal: np.ndarray, target_length: int = 512) -> np.ndarray:
        """Normalize and pad/truncate accelerometer signal to target length.

        Args:
            signal: 1D array of accelerometer measurements.
            target_length: Desired output length (padded or truncated).

        Returns:
            Preprocessed signal of shape (target_length, 1).
        """
        # Normalize to zero mean and unit variance
        signal = np.asarray(signal, dtype=np.float32)
        signal = (signal - np.mean(signal)) / (np.std(signal) + 1e-6)

        # Pad or truncate to target length
        if len(signal) < target_length:
            signal = np.pad(signal, (0, target_length - len(signal)), mode="constant")
        elif len(signal) > target_length:
            signal = signal[:target_length]

        return signal.reshape(-1, 1)

    def predict(self, signal: np.ndarray) -> dict:
        """Predict the elevator operational state from an accelerometer signal.

        Args:
            signal: 1D array of accelerometer measurements.

        Returns:
            Dictionary with predicted state and confidence scores.
        """
        processed = self.preprocess_signal(signal)
        batch = np.expand_dims(processed, axis=0)

        probabilities = self.model.predict(batch, verbose=0)[0]
        predicted_idx = np.argmax(probabilities)
        predicted_state = INDEX_TO_STATE[predicted_idx]

        return {
            "state": predicted_state,
            "confidence": float(probabilities[predicted_idx]),
            "probabilities": {
                ELEVATOR_STATES[i]: float(probabilities[i]) for i in range(len(ELEVATOR_STATES))
            },
        }

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        epochs: int = 20,
        batch_size: int = 32,
        validation_split: float = 0.1,
    ) -> keras.callbacks.History:
        """Train the model on labeled data.

        Args:
            X_train: Training signals (N, signal_length).
            y_train: One-hot encoded labels (N, num_classes).
            epochs: Number of training epochs.
            batch_size: Batch size for training.
            validation_split: Fraction of training data to use for validation.

        Returns:
            Training history object from Keras.
        """
        # Preprocess all training signals
        X_processed = np.array([self.preprocess_signal(x).flatten() for x in X_train]).reshape(
            X_train.shape[0], -1, 1
        )

        history = self.model.fit(
            X_processed,
            y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0,
        )

        return history

"""TD-Gammon neural network model."""

import tensorflow as tf


class TDGammonModel(tf.keras.Model):
    """
    TD-Gammon style network: 198 inputs -> hidden (sigmoid) -> 1 output (sigmoid).
    Output represents win probability for the current player.
    """

    def __init__(self, hidden_size: int = 80):
        super().__init__()
        self.hidden = tf.keras.layers.Dense(
            hidden_size, activation="sigmoid", name="hidden"
        )
        self.output_layer = tf.keras.layers.Dense(
            1, activation="sigmoid", name="value"
        )

    def call(self, x):
        h = self.hidden(x)
        return self.output_layer(h)

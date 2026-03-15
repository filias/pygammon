import pytest

try:
    import tensorflow as tf

    HAS_TF = True
except ImportError:
    HAS_TF = False


@pytest.mark.skipif(not HAS_TF, reason="TensorFlow not installed")
class TestTDGammonModel:
    def test_model_output_shape(self):
        from pygammon.ai.model import TDGammonModel

        model = TDGammonModel(hidden_size=80)
        x = tf.zeros((1, 198))
        output = model(x)
        assert output.shape == (1, 1)

    def test_model_output_range(self):
        from pygammon.ai.model import TDGammonModel

        model = TDGammonModel(hidden_size=80)
        x = tf.random.uniform((10, 198))
        output = model(x)
        assert tf.reduce_all(output >= 0.0).numpy()
        assert tf.reduce_all(output <= 1.0).numpy()

    def test_model_batch_processing(self):
        from pygammon.ai.model import TDGammonModel

        model = TDGammonModel(hidden_size=80)
        x = tf.random.uniform((32, 198))
        output = model(x)
        assert output.shape == (32, 1)

    def test_model_custom_hidden_size(self):
        from pygammon.ai.model import TDGammonModel

        model = TDGammonModel(hidden_size=40)
        x = tf.zeros((1, 198))
        output = model(x)
        assert output.shape == (1, 1)

    def test_model_trainable_variables(self):
        from pygammon.ai.model import TDGammonModel

        model = TDGammonModel(hidden_size=80)
        model(tf.zeros((1, 198)))  # Build
        assert len(model.trainable_variables) == 4

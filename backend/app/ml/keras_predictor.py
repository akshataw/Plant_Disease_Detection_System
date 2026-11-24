import json
import os
import threading

from .base import Predictor
from .preprocess import to_model_input, top_k_from_probs


class KerasPredictor(Predictor):
    def __init__(self, model_path: str, class_names_path: str, version: str | None = None):
        # Imported lazily so the rest of the app (and tests) don't pay TensorFlow's import cost
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
        import keras

        self._model = keras.models.load_model(model_path, compile=False)
        with open(class_names_path, encoding="utf-8") as f:
            self._class_names = json.load(f)

        n_outputs = self._model.output_shape[-1]
        if n_outputs != len(self._class_names):
            raise ValueError(f"Model has {n_outputs} outputs but {len(self._class_names)} class names were given")

        _, h, w, _ = self._model.input_shape
        self._input_size = (w, h)
        self._version = version or os.path.splitext(os.path.basename(model_path))[0]
        self._lock = threading.Lock()

    @property
    def version(self):
        return self._version

    @property
    def class_names(self):
        return self._class_names

    def predict(self, image, top_k=3):
        batch = to_model_input(image, self._input_size)
        with self._lock:
            probs = self._model(batch, training=False).numpy()[0]
        return top_k_from_probs(probs, self._class_names, top_k)

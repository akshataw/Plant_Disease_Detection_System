"""Builds the configured Predictor. Add new model backends here (TFLite, ensembles, A/B...)."""
import logging
import os

log = logging.getLogger(__name__)


def build_predictor(config):
    model_type = config.get("MODEL_TYPE", "keras")
    if model_type == "none":
        return None
    if model_type == "keras":
        path, names = config["MODEL_PATH"], config["CLASS_NAMES_PATH"]
        if not (os.path.exists(path) and os.path.exists(names)):
            log.warning("Model not found (%s / %s); prediction endpoint disabled", path, names)
            return None
        from .keras_predictor import KerasPredictor

        predictor = KerasPredictor(path, names, version=config.get("MODEL_VERSION"))
        log.info("Loaded model %s (%d classes)", predictor.version, len(predictor.class_names))
        return predictor
    raise ValueError(f"Unknown MODEL_TYPE: {model_type}")

import numpy as np
from PIL import Image, ImageOps


def to_model_input(image: Image.Image, size: tuple[int, int]) -> np.ndarray:
    """Centre-crop to the model's aspect ratio, resize, and return a float32 batch of raw 0-255 RGB.

    The model was trained on square PlantVillage images, so non-square photos are centre-cropped
    rather than stretched (ADR 0016); square inputs are unaffected.
    Normalisation (e.g. MobileNetV2's [-1, 1] scaling) is embedded in the saved model (ADR 0003),
    so it is intentionally NOT applied here.
    """
    rgb = ImageOps.fit(image.convert("RGB"), size, Image.Resampling.BILINEAR)
    return np.expand_dims(np.asarray(rgb, dtype=np.float32), axis=0)


def top_k_from_probs(probs: np.ndarray, class_names: list[str], k: int) -> list[dict]:
    k = min(k, len(class_names))
    idx = np.argsort(probs)[::-1][:k]
    return [{"label": class_names[i], "confidence": round(float(probs[i]), 6)} for i in idx]

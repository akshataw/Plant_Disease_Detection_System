import os
import uuid

from flask import current_app
from PIL import Image


MAX_STORED_SIDE = 1280  # history views don't need full-resolution originals


def save_image(image) -> str:
    """Persist an RGB PIL image as JPEG under a random name and return the file name.

    Re-encoding drops EXIF metadata (e.g. GPS location from phone cameras) before storage, and the
    stored copy is downscaled so its longest side is at most MAX_STORED_SIDE.
    """
    filename = f"{uuid.uuid4().hex}.jpg"
    if max(image.size) > MAX_STORED_SIDE:
        image = image.copy()  # don't mutate the caller's image
        image.thumbnail((MAX_STORED_SIDE, MAX_STORED_SIDE), Image.Resampling.LANCZOS)
    image.save(os.path.join(current_app.config["UPLOAD_DIR"], filename), format="JPEG", quality=90)
    return filename


def delete_image(filename: str) -> None:
    path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    if os.path.isfile(path):
        os.remove(path)

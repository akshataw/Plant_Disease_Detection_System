import numpy as np
from PIL import Image

from app.ml.preprocess import to_model_input


def test_square_input_is_plain_resize():
    img = Image.new("RGB", (256, 256), (10, 200, 30))
    out = to_model_input(img, (224, 224))
    assert out.shape == (1, 224, 224, 3) and out.dtype == np.float32
    assert out.max() == 200.0  # raw 0-255 pixels, no normalisation (ADR 0003)


def test_non_square_input_is_centre_cropped_not_stretched():
    # 400x200: red outer quarters, green centre half -> centre crop must be all green
    img = Image.new("RGB", (400, 200), (255, 0, 0))
    img.paste((0, 255, 0), (100, 0, 300, 200))
    out = to_model_input(img, (224, 224))[0]
    assert out.shape == (224, 224, 3)
    # (ignore the outermost columns, where bilinear sampling blends in a little of the cropped edge;
    # a plain stretch would make the left and right quarters fully red)
    assert out[:, 2:-2, 0].max() == 0.0 and out[:, 2:-2, 1].min() == 255.0

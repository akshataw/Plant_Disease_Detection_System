import io
import os

from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
# Pillow reports JPEGs with a Multi-Picture block (iPhone HDR/Portrait, many Samsung/Fuji) as "MPO";
# only the first frame is used.
ALLOWED_FORMATS = {"JPEG", "MPO", "PNG", "WEBP"}
MIN_SIDE = 32
MAX_PIXELS = 40_000_000  # guards against decompression bombs (checked explicitly before decoding)
# The model only needs 224 px and stored copies are capped at 1280 px, so JPEGs are decoded at a
# reduced DCT scale no smaller than this (big memory saving for 12-48 MP phone photos).
JPEG_DRAFT_SIZE = (1280, 1280)

# Pillow only *raises* above 2x this value (it merely warns between 1x and 2x); the explicit
# width*height check below is the real limit, this is a backstop for Image.open itself.
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class ImageValidationError(ValueError):
    pass


def load_and_validate(file_storage, max_bytes: int) -> Image.Image:
    """Validate an uploaded file and return a decoded, orientation-corrected RGB PIL image."""
    if file_storage is None or not file_storage.filename:
        raise ImageValidationError("No image file provided (form field 'image')")

    ext = os.path.splitext(file_storage.filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise ImageValidationError("Unsupported file type. Use JPG, PNG or WEBP")

    data = file_storage.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ImageValidationError(f"File too large (max {max_bytes // (1024 * 1024)} MB)")
    if not data:
        raise ImageValidationError("Empty file")

    try:
        # verify() catches truncated/corrupt files but leaves the image unusable, so reopen afterwards
        with Image.open(io.BytesIO(data)) as probe:
            # Header-only checks first: never decode something we are going to reject
            if probe.format not in ALLOWED_FORMATS:
                raise ImageValidationError("Unsupported image format. Use JPG, PNG or WEBP")
            if probe.width * probe.height > MAX_PIXELS:
                raise ImageValidationError(
                    f"Image dimensions too large (max {MAX_PIXELS // 1_000_000} megapixels)")
            if min(probe.size) < MIN_SIDE:
                raise ImageValidationError(f"Image too small (min {MIN_SIDE}px per side)")
            probe.verify()
        image = Image.open(io.BytesIO(data))
        if image.format in ("JPEG", "MPO"):
            image.draft("RGB", JPEG_DRAFT_SIZE)
        image.load()
    except ImageValidationError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError):
        raise ImageValidationError("File is not a valid image")

    return ImageOps.exif_transpose(image).convert("RGB")

from io import BytesIO
from importlib.util import find_spec
from pathlib import Path

def is_module_available(module_name: str) -> bool:
    """Check if a module is available in the current environment."""
    return find_spec(module_name) is not None

def is_pillow_img(image):
    """Check if the provided image is a Pillow image."""
    return (
        hasattr(image, "thumbnail")
        and hasattr(image, "mode")
        and hasattr(image, "size")
        and hasattr(image, "info")
        and hasattr(image, "getbands")
    )

def get_bytes_from_image(image) -> bytes | None:
    buf: BytesIO = BytesIO()
    if is_pillow_img(image):
        if is_module_available("PIL"):
            image.save(buf, format=image.format)
    return buf.getvalue()


def get_img_ext(image_path: str) -> str:
    """Get the file extension of the image."""
    return Path(image_path).suffix.lower() if image_path else ""

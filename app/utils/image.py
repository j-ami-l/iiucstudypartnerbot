"""Image manipulation utilities: resize, compress, and reformat."""

import io
from typing import Tuple
from PIL import Image, ImageOps


def process_image(
    image_bytes: bytes, max_side: int = 1280, quality: int = 80
) -> Tuple[bytes, int, int, float]:
    """Resize image so its max dimension is within max_side, and compress as JPEG.

    Args:
        image_bytes: Raw bytes of the uploaded image.
        max_side: Maximum allowed width or height in pixels.
        quality: JPEG compression quality (1-100).

    Returns:
        Tuple of (compressed_jpeg_bytes, width, height, size_in_kb).
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        # Correct orientation based on EXIF metadata if present
        img = ImageOps.exif_transpose(img)

        # Convert palette/alpha modes to standard RGB for JPEG output
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        orig_w, orig_h = img.size

        # Compute aspect-ratio-preserving dimensions
        if max(orig_w, orig_h) > max_side:
            scale = max_side / max(orig_w, orig_h)
            new_w = max(1, int(orig_w * scale))
            new_h = max(1, int(orig_h * scale))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            new_w, new_h = orig_w, orig_h

        out_buffer = io.BytesIO()
        img.save(out_buffer, format="JPEG", quality=quality, optimize=True)
        compressed_bytes = out_buffer.getvalue()
        size_kb = len(compressed_bytes) / 1024.0

        return compressed_bytes, new_w, new_h, size_kb

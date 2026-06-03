"""Thumbnail rendering.

Reads a local image path (Pillow), resizes to max_width preserving aspect,
re-encodes to JPEG bytes, returns (bytes, b64_data_uri).
Also persists a debug copy to `_thumbs/<uuid>.jpg` for inspection.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path


def render_thumb(
    src_path: str,
    uuid: str,
    debug_dir: Path | None,
    max_width: int = 400,
    jpeg_quality: float = 0.85,
) -> tuple[bytes, str] | None:
    """Return (jpeg_bytes, data_uri) for src_path; None if rendering fails."""
    from PIL import Image, ImageOps

    try:
        with Image.open(src_path) as im:
            im = ImageOps.exif_transpose(im)
            im = im.convert("RGB")
            if im.width > max_width:
                ratio = max_width / im.width
                new_size = (max_width, int(im.height * ratio))
                im = im.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=int(jpeg_quality * 100), optimize=True)
            data = buf.getvalue()
    except Exception:
        return None

    if debug_dir is not None:
        debug_dir.mkdir(parents=True, exist_ok=True)
        (debug_dir / f"{uuid}.jpg").write_bytes(data)

    b64 = base64.b64encode(data).decode("ascii")
    return data, f"data:image/jpeg;base64,{b64}"

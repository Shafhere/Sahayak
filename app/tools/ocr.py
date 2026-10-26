"""Local OCR for printed English images. Images are not sent to an AI provider."""
from functools import lru_cache
from io import BytesIO
import numpy as np
from PIL import Image, UnidentifiedImageError

@lru_cache(maxsize=1)
def _engine():
    from rapidocr_onnxruntime import RapidOCR
    return RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)

def extract_text_from_image(image_bytes: bytes) -> str:
    if not image_bytes or len(image_bytes) > 10 * 1024 * 1024:
        return "OCR Error: Choose an image smaller than 10 MB."
    try:
        with Image.open(BytesIO(image_bytes)) as source:
            if source.width * source.height > 20_000_000:
                return "OCR Error: Choose an image below 20 megapixels."
            image = source.convert("RGB")
            image.thumbnail((2400, 2400))
            result, _ = _engine()(np.array(image))
        lines = [row[1] for row in (result or []) if row[2] >= .6]
        return "\n".join(lines) or "OCR Error: No clear printed text found. Try a sharper English document image."
    except (UnidentifiedImageError, OSError, ValueError):
        return "OCR Error: This image could not be read. Try a PNG or JPEG."
    except Exception:
        return "OCR Error: The local reader is unavailable. Check the OCR installation."

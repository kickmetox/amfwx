"""Windows OCR via optional winsdk."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path


class OcrError(RuntimeError):
    pass


def available():
    try:
        import winsdk.windows.media.ocr  # noqa: F401
        return True
    except ImportError:
        return False


async def _recognize(path, language=None):
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapDecoder
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.storage import StorageFile

    if language:
        engine = OcrEngine.try_create_from_language(Language(str(language)))
    else:
        engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        raise OcrError("keine OCR-Sprache installiert")
    file = await StorageFile.get_file_from_path_async(str(path))
    stream = await file.open_async(0)
    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    result = await engine.recognize_async(bitmap)
    return result.text


def ocr_image(path, language=None):
    if not available():
        raise OcrError("winsdk fehlt: pip install winsdk")
    return asyncio.run(_recognize(path, language))


def ocr_pdf(path, language=None, dpi=200):
    from .pdf_print import render_pdf
    pages = render_pdf(path, dpi=dpi)
    texts = []
    with tempfile.TemporaryDirectory(prefix="amfwx_ocr_") as folder:
        for index, image in enumerate(pages, 1):
            target = Path(folder) / f"page_{index:03d}.png"
            image.save(target)
            texts.append(ocr_image(target, language))
    return "\n\n".join(texts)

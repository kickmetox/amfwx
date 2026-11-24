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

async def _recognize_words(path, language=None):
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapDecoder
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.storage import StorageFile

    engine = (OcrEngine.try_create_from_language(Language(str(language)))
              if language else
              OcrEngine.try_create_from_user_profile_languages())
    if engine is None:
        raise OcrError("keine OCR-Sprache installiert")
    file = await StorageFile.get_file_from_path_async(str(path))
    stream = await file.open_async(0)
    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    result = await engine.recognize_async(bitmap)
    words = []
    for line in result.lines:
        for word in line.words:
            rect = word.bounding_rect
            words.append({"text": word.text, "x": float(rect.x),
                          "y": float(rect.y), "width": float(rect.width),
                          "height": float(rect.height)})
    return result.text, words


def ocr_words(path, language=None):
    if not available():
        raise OcrError("winsdk fehlt: pip install winsdk")
    return asyncio.run(_recognize_words(path, language))


def make_searchable_pdf(source, output, language=None, dpi=200):
    if not available():
        raise OcrError("winsdk fehlt: pip install winsdk")
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError as error:
            raise OcrError("pymupdf fehlt: pip install pymupdf") from error
    source_doc = pymupdf.open(str(source))
    target_doc = pymupdf.open()
    with tempfile.TemporaryDirectory(prefix="amfwx_search_") as folder:
        for index, page in enumerate(source_doc):
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            image_path = Path(folder) / f"page_{index:03d}.png"
            pixmap.save(image_path)
            text, words = ocr_words(image_path, language)
            target_page = target_doc.new_page(width=page.rect.width,
                                              height=page.rect.height)
            target_page.insert_image(target_page.rect, filename=str(image_path))
            scale_x = page.rect.width / max(1, pixmap.width)
            scale_y = page.rect.height / max(1, pixmap.height)
            for word in words:
                size = max(1.0, word["height"] * scale_y * 0.8)
                target_page.insert_text(
                    (word["x"] * scale_x,
                     (word["y"] + word["height"]) * scale_y),
                    word["text"], fontsize=size, render_mode=3)
    target_doc.save(str(output))
    source_doc.close()
    target_doc.close()
    return str(output)


"""PDF merge and split helpers."""

from __future__ import annotations

from pathlib import Path


class PdfToolError(RuntimeError):
    pass


def _pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
            return pymupdf
        except ImportError as error:
            raise PdfToolError("pymupdf fehlt: pip install pymupdf") from error


def merge(paths, output):
    module = _pymupdf()
    result = module.open()
    try:
        for path in paths:
            document = module.open(str(path))
            result.insert_pdf(document)
            document.close()
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        result.save(str(output))
    finally:
        result.close()
    return str(output)


def split(path, output_dir, pages=None):
    module = _pymupdf()
    source = module.open(str(path))
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    stem = Path(path).stem
    outputs = []
    try:
        indexes = list(range(source.page_count)) if pages is None else [
            int(page) - 1 for page in pages]
        for number, index in enumerate(indexes, 1):
            if index < 0 or index >= source.page_count:
                raise PdfToolError(f"Seite ausserhalb: {index + 1}")
            target = folder / f"{stem}_{number:03d}.pdf"
            result = module.open()
            try:
                result.insert_pdf(source, from_page=index, to_page=index)
                result.save(str(target))
            finally:
                result.close()
            outputs.append(str(target))
    finally:
        source.close()
    return outputs


def page_count(path):
    module = _pymupdf()
    document = module.open(str(path))
    try:
        return document.page_count
    finally:
        document.close()

"""JPEG scans to multi-page PDF."""

from __future__ import annotations

import struct
from pathlib import Path


class PdfError(RuntimeError):
    pass


def _jpeg_size(data):
    if data[:2] != b"\xff\xd8":
        raise PdfError("keine JPEG-Datei")
    index = 2
    while index + 4 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in (0xD8, 0xD9):
            continue
        length = struct.unpack(">H", data[index:index + 2])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[index + 3:index + 7])
            components = data[index + 7]
            return width, height, components
        index += length
    raise PdfError("JPEG-Größe nicht gefunden")


def images_to_pdf(paths, output):
    paths = [Path(path) for path in paths]
    if not paths:
        raise PdfError("keine Bilder")
    objects = [None, None]  # catalog, pages
    page_ids = []
    for image_path in paths:
        data = image_path.read_bytes()
        width, height, components = _jpeg_size(data)
        colorspace = "/DeviceGray" if components == 1 else "/DeviceRGB"
        page_id = len(objects) + 1
        image_id = page_id + 1
        content_id = page_id + 2
        page_ids.append(page_id)
        objects.extend([None, None, None])
        content = f"q\n{width} 0 0 {height} 0 0 cm\n/Im0 Do\nQ\n".encode("ascii")
        objects[page_id - 1] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /XObject << /Im0 {image_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>").encode("ascii")
        objects[image_id - 1] = (
            f"<< /Type /XObject /Subtype /Image /Width {width} "
            f"/Height {height} /ColorSpace {colorspace} "
            f"/BitsPerComponent 8 /Filter /DCTDecode /Length {len(data)} >>\n"
            f"stream\n").encode("ascii") + data + b"\nendstream"
        objects[content_id - 1] = (
            f"<< /Length {len(content)} >>\nstream\n").encode("ascii") + \
            content + b"endstream"
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[1] = (f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"
                  ).encode("ascii")
    buffer = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(buffer))
        buffer.extend(f"{number} 0 obj\n".encode("ascii"))
        buffer.extend(body)
        buffer.extend(b"\nendobj\n")
    xref = len(buffer)
    buffer.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    buffer.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.extend((f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                   f"startxref\n{xref}\n%%EOF\n").encode("ascii"))
    target = Path(output)
    target.write_bytes(buffer)
    return str(target)


def scan_to_pdf(scanner, path, source="Platen", max_pages=1, **kwargs):
    import tempfile
    with tempfile.TemporaryDirectory(prefix="amfwx_pdf_") as folder:
        if int(max_pages) <= 1:
            pages = [scanner.scan(str(Path(folder) / "page.jpg"),
                                  source=source, **kwargs)]
        else:
            pages = scanner.scan_pages(folder, prefix="page", source=source,
                                       max_pages=max_pages, **kwargs)
        return images_to_pdf(pages, path)

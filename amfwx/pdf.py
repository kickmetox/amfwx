"""Minimal PDF export for AMFWX canvases."""

from __future__ import annotations

import zlib
from pathlib import Path


def _rgb(canvas):
    data = canvas.data
    output = bytearray(canvas.width * canvas.height * 3)
    target = 0
    for index in range(0, len(data), 4):
        output[target] = data[index + 2]
        output[target + 1] = data[index + 1]
        output[target + 2] = data[index]
        target += 3
    return bytes(output)


def canvas_to_pdf(canvas, path):
    width, height = canvas.width, canvas.height
    image = zlib.compress(_rgb(canvas), 9)
    content = f"q\n{width} 0 0 {height} 0 0 cm\n/Im0 Do\nQ\n".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
         f"/Resources << /XObject << /Im0 4 0 R >> >> "
         f"/Contents 5 0 R >>").encode("ascii"),
        (f"<< /Type /XObject /Subtype /Image /Width {width} "
         f"/Height {height} /ColorSpace /DeviceRGB /BitsPerComponent 8 "
         f"/Filter /FlateDecode /Length {len(image)} >>\nstream\n").encode(
             "ascii") + image + b"\nendstream",
        (f"<< /Length {len(content)} >>\nstream\n").encode("ascii") +
        content + b"endstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode("ascii"))
    Path(path).write_bytes(bytes(output))
    return path

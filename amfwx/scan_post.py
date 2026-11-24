"""Scanner post-processing: deskew, crop, blank pages, grayscale."""

from __future__ import annotations

from pathlib import Path

try:
    import numpy as np
except ImportError:  # optional
    np = None


class PostProcessError(RuntimeError):
    pass


def _pil():
    try:
        from PIL import Image, ImageChops, ImageOps
        return Image, ImageChops, ImageOps
    except ImportError as error:
        raise PostProcessError("Pillow fehlt: pip install pillow") from error


def is_blank(image, threshold=0.985, dark=235):
    Image, _chops, ImageOps = _pil()
    gray = ImageOps.grayscale(image)
    if np is not None:
        values = np.asarray(gray, dtype=np.uint8)
        if values.size == 0:
            return True
        return float((values < int(dark)).mean()) < (1.0 - float(threshold))
    histogram = gray.histogram()
    dark_pixels = sum(histogram[:int(dark)])
    return (dark_pixels / max(1, gray.width * gray.height)) < (
        1.0 - float(threshold))


def crop_white(image, margin=12, threshold=245):
    Image, ImageChops, ImageOps = _pil()
    gray = ImageOps.grayscale(image)
    background = Image.new("L", gray.size, 255)
    difference = ImageChops.difference(gray, background)
    mask = difference.point(lambda value: 255 if value > (255 - threshold)
                            else 0)
    box = mask.getbbox()
    if not box:
        return image
    left, top, right, bottom = box
    left = max(0, left - int(margin))
    top = max(0, top - int(margin))
    right = min(image.width, right + int(margin))
    bottom = min(image.height, bottom + int(margin))
    if right - left < 16 or bottom - top < 16:
        return image
    return image.crop((left, top, right, bottom))


def estimate_skew(image, max_angle=8.0, step=0.5):
    if np is None:
        return 0.0
    Image, _chops, ImageOps = _pil()
    gray = ImageOps.grayscale(image)
    scale = min(1.0, 1200 / max(1, gray.width))
    if scale < 1.0:
        gray = gray.resize((max(1, int(gray.width * scale)),
                            max(1, int(gray.height * scale))))
    values = np.asarray(gray, dtype=np.float32)
    values = np.clip((220 - values) / 220, 0, 1)
    best_angle, best_score = 0.0, -1.0
    angle = -float(max_angle)
    while angle <= max_angle + 0.001:
        rotated = np.asarray(
            Image.fromarray((values * 255).astype(np.uint8)).rotate(
                angle, resample=Image.Resampling.BILINEAR, expand=False),
            dtype=np.float32)
        rows = rotated.sum(axis=1)
        score = float(np.var(np.diff(rows)))
        if score > best_score:
            best_angle, best_score = angle, score
        angle += float(step)
    return best_angle


def deskew(image, angle=None, max_angle=8.0):
    Image, _chops, _ops = _pil()
    if angle is None:
        angle = estimate_skew(image, max_angle)
    if abs(angle) < 0.2:
        return image
    return image.rotate(-float(angle), resample=Image.Resampling.BICUBIC,
                        expand=False, fillcolor="white")


def postprocess(image, deskew_enabled=True, crop_enabled=True,
                grayscale=False):
    result = image.convert("RGB")
    if deskew_enabled:
        result = deskew(result)
    if crop_enabled:
        result = crop_white(result)
    if grayscale:
        result = result.convert("L")
    return result


def process_file(path, output=None, **options):
    Image, _chops, _ops = _pil()
    image = Image.open(path)
    result = postprocess(image, **options)
    target = Path(output or path)
    if target.suffix.lower() not in (".jpg", ".jpeg"):
        target = target.with_suffix(".jpg")
    result.convert("RGB").save(target, "JPEG", quality=92)
    return str(target)


def postprocess_pages(paths, deskew_enabled=True, crop_enabled=True,
                      grayscale=False, drop_blank=False):
    result = []
    for path in paths:
        Image, _chops, _ops = _pil()
        image = Image.open(path)
        if drop_blank and is_blank(image):
            continue
        processed = postprocess(image, deskew_enabled, crop_enabled,
                                grayscale)
        target = Path(path).with_suffix(".jpg")
        processed.convert("RGB").save(target, "JPEG", quality=92)
        result.append(str(target))
    return result

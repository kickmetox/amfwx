"""Small UAX#9-style bidi level resolver for AMFWX."""

from __future__ import annotations

import unicodedata

RTL_RANGES = (
    (0x0590, 0x05FF), (0x0600, 0x06FF), (0x0750, 0x077F),
    (0x08A0, 0x08FF), (0xFB1D, 0xFDFF), (0xFE70, 0xFEFF),
)
STRONG_R = set()
STRONG_AL = set()


def _rtl(character):
    code = ord(character)
    return any(low <= code <= high for low, high in RTL_RANGES)


def bidi_type(character):
    code = ord(character)
    if 0x0590 <= code <= 0x05FF:
        return "R"
    if 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F or \
            0x08A0 <= code <= 0x08FF or 0xFB50 <= code <= 0xFDFF:
        return "AL"
    if 0x30 <= code <= 0x39:
        return "EN"
    if 0x0660 <= code <= 0x0669 or 0x06F0 <= code <= 0x06F9:
        return "AN"
    category = unicodedata.category(character)
    if category in ("Mn", "Me"):
        return "NSM"
    if character.isspace():
        return "WS"
    if category.startswith("L"):
        return "L"
    if category.startswith("P") or category.startswith("S"):
        return "ON"
    return "ON"


def _base_direction(text):
    for character in text:
        kind = bidi_type(character)
        if kind in ("R", "AL"):
            return 1
        if kind == "L":
            return 0
    return 0


def bidi_levels(text):
    text = str(text)
    types = [bidi_type(character) for character in text]
    base = _base_direction(text)
    levels = [base] * len(text)
    for index, kind in enumerate(types):
        if kind in ("R", "AL"):
            levels[index] = 1
        elif kind in ("EN", "AN"):
            levels[index] = 2
        else:
            levels[index] = base
    # W1: NSM takes the type of the previous character.
    for index in range(1, len(types)):
        if types[index] == "NSM":
            types[index] = types[index - 1]
    # W2: EN after AL becomes AN.
    previous_strong = None
    for index, kind in enumerate(types):
        if kind in ("R", "L", "AL"):
            previous_strong = kind
        elif kind == "EN" and previous_strong == "AL":
            types[index] = "AN"
            levels[index] = 2
    # W3: AL -> R.
    for index, kind in enumerate(types):
        if kind == "AL":
            types[index] = "R"
    # W4: ES/CS between numbers.
    for index in range(1, len(types) - 1):
        if types[index] in ("ES", "CS") and \
                types[index - 1] in ("EN", "AN") and \
                types[index - 1] == types[index + 1]:
            types[index] = types[index - 1]
    # W5: ET adjacent to EN.
    for index in range(len(types)):
        if types[index] == "ET":
            left = types[index - 1] if index else None
            right = types[index + 1] if index + 1 < len(types) else None
            if left == "EN" or right == "EN":
                types[index] = "EN"
    # W6: remaining separators -> ON.
    for index, kind in enumerate(types):
        if kind in ("ES", "ET", "CS"):
            types[index] = "ON"
    # W7: EN after L -> L.
    previous_strong = None
    for index, kind in enumerate(types):
        if kind in ("L", "R"):
            previous_strong = kind
        elif kind == "EN" and previous_strong == "L":
            types[index] = "L"
            levels[index] = base
    # N1/N2: neutrals.
    for index, kind in enumerate(types):
        if kind not in ("ON", "WS", "B", "S"):
            continue
        left = index - 1
        while left >= 0 and types[left] in ("ON", "WS", "B", "S"):
            left -= 1
        right = index + 1
        while right < len(types) and types[right] in ("ON", "WS", "B", "S"):
            right += 1
        left_type = types[left] if left >= 0 else None
        right_type = types[right] if right < len(types) else None
        if left_type == right_type and left_type in ("L", "R"):
            direction = left_type
        else:
            direction = "R" if base else "L"
        types[index] = direction
        levels[index] = 1 if direction == "R" else base
    # I1/I2: implicit levels.
    for index, kind in enumerate(types):
        if levels[index] % 2 == 0:
            if kind == "R":
                levels[index] += 1
            elif kind in ("AN", "EN"):
                levels[index] += 2
        elif kind in ("L", "EN", "AN"):
            levels[index] += 1
    return levels


def bidi_reorder(text):
    text = str(text)
    if not any(_rtl(character) for character in text):
        return text
    levels = bidi_levels(text)
    characters = list(text)
    maximum = max(levels) if levels else 0
    for level in range(maximum, 0, -1):
        index = 0
        while index < len(characters):
            if levels[index] >= level:
                start = index
                while index < len(characters) and levels[index] >= level:
                    index += 1
                characters[start:index] = reversed(characters[start:index])
            else:
                index += 1
    return "".join(characters)

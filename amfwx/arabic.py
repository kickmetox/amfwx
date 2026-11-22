"""Arabic joining to Unicode presentation forms (self-contained)."""

from __future__ import annotations

# char -> (isolated, final, initial, medial); None = form does not exist.
FORMS = {
    "\u0621": ("\uFE80", None, None, None),
    "\u0622": ("\uFE81", "\uFE82", None, None),
    "\u0623": ("\uFE83", "\uFE84", None, None),
    "\u0624": ("\uFE85", "\uFE86", None, None),
    "\u0625": ("\uFE87", "\uFE88", None, None),
    "\u0626": ("\uFE89", "\uFE8A", "\uFE8B", "\uFE8C"),
    "\u0627": ("\uFE8D", "\uFE8E", None, None),
    "\u0628": ("\uFE8F", "\uFE90", "\uFE91", "\uFE92"),
    "\u0629": ("\uFE93", "\uFE94", None, None),
    "\u062A": ("\uFE95", "\uFE96", "\uFE97", "\uFE98"),
    "\u062B": ("\uFE99", "\uFE9A", "\uFE9B", "\uFE9C"),
    "\u062C": ("\uFE9D", "\uFE9E", "\uFE9F", "\uFEA0"),
    "\u062D": ("\uFEA1", "\uFEA2", "\uFEA3", "\uFEA4"),
    "\u062E": ("\uFEA5", "\uFEA6", "\uFEA7", "\uFEA8"),
    "\u062F": ("\uFEA9", "\uFEAA", None, None),
    "\u0630": ("\uFEAB", "\uFEAC", None, None),
    "\u0631": ("\uFEAD", "\uFEAE", None, None),
    "\u0632": ("\uFEAF", "\uFEB0", None, None),
    "\u0633": ("\uFEB1", "\uFEB2", "\uFEB3", "\uFEB4"),
    "\u0634": ("\uFEB5", "\uFEB6", "\uFEB7", "\uFEB8"),
    "\u0635": ("\uFEB9", "\uFEBA", "\uFEBB", "\uFEBC"),
    "\u0636": ("\uFEBD", "\uFEBE", "\uFEBF", "\uFEC0"),
    "\u0637": ("\uFEC1", "\uFEC2", "\uFEC3", "\uFEC4"),
    "\u0638": ("\uFEC5", "\uFEC6", "\uFEC7", "\uFEC8"),
    "\u0639": ("\uFEC9", "\uFECA", "\uFECB", "\uFECC"),
    "\u063A": ("\uFECD", "\uFECE", "\uFECF", "\uFED0"),
    "\u0641": ("\uFED1", "\uFED2", "\uFED3", "\uFED4"),
    "\u0642": ("\uFED5", "\uFED6", "\uFED7", "\uFED8"),
    "\u0643": ("\uFED9", "\uFEDA", "\uFEDB", "\uFEDC"),
    "\u0644": ("\uFEDD", "\uFEDE", "\uFEDF", "\uFEE0"),
    "\u0645": ("\uFEE1", "\uFEE2", "\uFEE3", "\uFEE4"),
    "\u0646": ("\uFEE5", "\uFEE6", "\uFEE7", "\uFEE8"),
    "\u0647": ("\uFEE9", "\uFEEA", "\uFEEB", "\uFEEC"),
    "\u0648": ("\uFEED", "\uFEEE", None, None),
    "\u0649": ("\uFEEF", "\uFEF0", None, None),
    "\u064A": ("\uFEF1", "\uFEF2", "\uFEF3", "\uFEF4"),
}

DUAL = {char for char, forms in FORMS.items() if forms[2] is not None}
RIGHT = {char for char, forms in FORMS.items() if forms[1] is not None}
NON_JOINING = {char for char, forms in FORMS.items() if forms[1] is None}
TRANSPARENT = set("ًٌٍَُِّْـ")

LAM = "\u0644"
ALEF_FORMS = {
    "\u0627": ("\uFEFB", "\uFEFC"),
    "\u0622": ("\uFEF5", "\uFEF6"),
    "\u0623": ("\uFEF7", "\uFEF8"),
    "\u0625": ("\uFEF9", "\uFEFA"),
}


def _is_arabic(character):
    return character in FORMS


def _lam_alef(characters):
    result = []
    index = 0
    while index < len(characters):
        character = characters[index]
        if character == LAM and index + 1 < len(characters):
            following = characters[index + 1]
            if following in ALEF_FORMS:
                previous = None
                cursor = index - 1
                while cursor >= 0:
                    if characters[cursor] in TRANSPARENT:
                        cursor -= 1
                        continue
                    previous = characters[cursor]
                    break
                isolated, final = ALEF_FORMS[following]
                result.append(final if previous in DUAL else isolated)
                index += 2
                continue
        result.append(character)
        index += 1
    return result


def arabic_shape(text):
    """Replace Arabic letters by isolated/final/initial/medial forms."""
    characters = _lam_alef(list(str(text)))
    for index, character in enumerate(characters):
        if not _is_arabic(character):
            continue
        previous = None
        cursor = index - 1
        while cursor >= 0:
            if characters[cursor] in TRANSPARENT:
                cursor -= 1
                continue
            previous = characters[cursor]
            break
        following = None
        cursor = index + 1
        while cursor < len(characters):
            if characters[cursor] in TRANSPARENT:
                cursor += 1
                continue
            following = characters[cursor]
            break
        previous_links = previous in DUAL
        following_links = following in (DUAL | RIGHT)
        forms = FORMS[character]
        isolated, final, initial, medial = forms
        if previous_links and following_links and medial:
            characters[index] = medial
        elif previous_links and final:
            characters[index] = final
        elif following_links and initial:
            characters[index] = initial
        else:
            characters[index] = isolated
    return "".join(characters)

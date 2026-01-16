"""
Helpers for formatting values into speech-friendly text for voice agents.

These helpers are intentionally simple and optimized for common real-estate patterns:
- Addresses like "6794 BOSS COURT" should be spoken like "sixty-seven ninety-four Boss Court"
- Prices like 339000 should be spoken like "three thirty-nine thousand" (or "about three forty")
"""

from __future__ import annotations

import re
from typing import Optional


_ONES = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
}

_TEENS = {
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
}

_TENS = {
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety",
}


def _two_digit(n: int, *, pad_oh: bool = False) -> str:
    """Convert 0-99 to spoken words (US English)."""
    if n < 0 or n > 99:
        raise ValueError("n must be 0-99")
    if n < 10:
        return f"oh {_ONES[n]}" if pad_oh else _ONES[n]
    if 10 <= n <= 19:
        return _TEENS[n]
    tens = (n // 10) * 10
    ones = n % 10
    if ones == 0:
        return _TENS[tens]
    return f"{_TENS[tens]}-{_ONES[ones]}"


def number_to_spoken_pair_style(n: int) -> str:
    """
    Convert typical street numbers to a pair style:
    - 6794 -> "sixty-seven ninety-four"
    - 1205 -> "twelve oh five"
    Falls back to a reasonable reading for other sizes.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    s = str(n)
    if len(s) == 4:
        first = int(s[:2])
        last = int(s[2:])
        return f"{_two_digit(first)} {_two_digit(last, pad_oh=last < 10)}"
    if len(s) == 3:
        # 105 -> "one oh five"
        hundreds = int(s[0])
        last2 = int(s[1:])
        return f"{_ONES[hundreds]} {_two_digit(last2, pad_oh=last2 < 10)}"
    if len(s) <= 2:
        return _two_digit(int(s), pad_oh=False) if len(s) == 2 else _ONES[int(s)]
    # 5+ digits: just return digits grouped; better than digit-by-digit TTS
    return s


def format_spoken_address(address: str) -> str:
    """
    Convert an address string into a more speakable form.
    If it starts with a street number, convert that to pair-style words.
    """
    if not address:
        return address
    address = address.strip()

    m = re.match(r"^(?P<num>\\d{1,6})\\s+(?P<rest>.+)$", address)
    if not m:
        # title-case the non-numeric address lightly
        return _titleish(address)

    num = int(m.group("num"))
    rest = m.group("rest")
    spoken_num = number_to_spoken_pair_style(num)
    return f"{spoken_num} {_titleish(rest)}".strip()


def format_spoken_price(price: Optional[float]) -> Optional[str]:
    """
    Convert a numeric price into common US real estate speech style:
    - 249000 -> "two forty-nine thousand"
    - 418000 -> "four eighteen thousand" (not "four hundred eighteen thousand")
    - 339000 -> "three thirty-nine thousand"
    - 1250000 -> "one point two five million"
    """
    if price is None:
        return None
    try:
        p = int(round(float(price)))
    except Exception:
        return None

    if p <= 0:
        return None

    if p >= 1_000_000:
        millions = p / 1_000_000
        # Keep it simple: 1.25 -> "one point two five"
        s = f"{millions:.2f}".rstrip("0").rstrip(".")
        left, _, right = s.partition(".")
        if not right:
            return f"{_int_to_words(int(left))} million"
        # speak digits after the decimal in pairs (2 digits)
        right_words = " ".join(_ONES[int(ch)] for ch in right)
        return f"{_int_to_words(int(left))} point {right_words} million"

    thousands = p // 1000  # 249000 -> 249, 418000 -> 418
    remainder = p % 1000
    
    # For prices like 249000 or 418000, prefer shorter form
    # 249 -> "two forty-nine" (not "two hundred forty-nine")
    # 418 -> "four eighteen" (not "four hundred eighteen")
    spoken_thousands = _three_digit_thousands_style_short(thousands)
    
    if remainder == 0:
        return f"{spoken_thousands} thousand"
    else:
        # Rare case: prices like 249500
        return f"{spoken_thousands} thousand, {_three_digit_thousands_style(remainder)}"


def _three_digit_thousands_style(n: int) -> str:
    """
    Convert 0-999 into the real-estate "three thirty-nine" style for thousands.
    339 -> "three thirty-nine"
    265 -> "two sixty-five"
    105 -> "one oh five"
    """
    if n < 0 or n > 999:
        return str(n)
    if n < 100:
        return _two_digit(n, pad_oh=False)
    hundreds = n // 100
    last2 = n % 100
    return f"{_ONES[hundreds]} {_two_digit(last2, pad_oh=last2 < 10)}"


def _three_digit_thousands_style_short(n: int) -> str:
    """
    Convert 0-999 into shorter "two forty-nine" style (preferred for prices).
    249 -> "two forty-nine" (not "two hundred forty-nine")
    418 -> "four eighteen" (not "four hundred eighteen")
    339 -> "three thirty-nine"
    """
    if n < 0 or n > 999:
        return str(n)
    if n < 100:
        return _two_digit(n, pad_oh=False)
    
    # For numbers >= 100, prefer shorter form (drop "hundred")
    hundreds = n // 100
    last2 = n % 100
    
    # Only use "hundred" if last2 is 0 (e.g., 300 -> "three hundred")
    if last2 == 0:
        return f"{_ONES[hundreds]} hundred"
    
    # Otherwise, drop "hundred" for more natural speech (249 -> "two forty-nine")
    return f"{_ONES[hundreds]} {_two_digit(last2, pad_oh=last2 < 10)}"


def _int_to_words(n: int) -> str:
    """Very small helper for 0-9 for our million formatter."""
    if 0 <= n <= 9:
        return _ONES[n]
    return str(n)


def _titleish(s: str) -> str:
    # Keep common ALL CAPS from MLS but don't over-format.
    # This makes "BOSS COURT" -> "Boss Court" while preserving acronyms.
    words = []
    for w in re.split(r"\\s+", s.strip()):
        if not w:
            continue
        if len(w) <= 2 and w.isupper():
            words.append(w)
        else:
            words.append(w.capitalize())
    return " ".join(words)



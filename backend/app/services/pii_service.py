import re
from typing import Tuple

from app.models.event import Classification

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PAN_REGEX = re.compile(r'\b[A-Za-z]{5}\d{4}[A-Za-z]{1}\b')
PHONE_REGEX = re.compile(r'(?<!\d)(?:\+?91[\-\s]?)?[6-9](?:[\-\s]?\d){9}(?!\d)')
AADHAAR_REGEX = re.compile(r'(?<!\d)[2-9](?:[\-\s]?\d){11}(?!\d)')
CC_REGEX = re.compile(r'(?<!\d)\d(?:[\-\s]*\d){12,18}(?!\d)')

def is_luhn_valid(cc: str) -> bool:
    digits = [int(c) for c in cc if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0

def validate_aadhaar(aadhaar_str: str) -> bool:
    d = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    p = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    digits = [int(c) for c in aadhaar_str if c.isdigit()]
    if len(digits) != 12: return False
    c = 0
    for i, num in enumerate(digits[::-1]):
        c = d[c][p[i % 8][num]]
    return c == 0

class PIIDetector:
    @staticmethod
    def process_text(text: str) -> Tuple[str, Classification]:
        if not text:
            return text, Classification.PUBLIC
        
        classification = Classification.PUBLIC
        processed_text = text

        # 1. Credit Card
        def replace_cc(match):
            nonlocal classification
            matched_str = match.group(0)
            if is_luhn_valid(matched_str):
                classification = Classification.RESTRICTED
                return '[credit_card]'
            return matched_str
        
        processed_text = CC_REGEX.sub(replace_cc, processed_text)

        # 2. Aadhaar
        def replace_aadhaar(match):
            nonlocal classification
            matched_str = match.group(0)
            if validate_aadhaar(matched_str):
                if classification != Classification.RESTRICTED:
                    classification = Classification.CONFIDENTIAL
                return '[aadhaar]'
            return matched_str

        processed_text = AADHAAR_REGEX.sub(replace_aadhaar, processed_text)

        # 3. PAN
        def replace_pan(match):
            nonlocal classification
            if classification != Classification.RESTRICTED:
                classification = Classification.CONFIDENTIAL
            return '[pan]'
        
        processed_text = PAN_REGEX.sub(replace_pan, processed_text)

        # 4. Email
        def replace_email(match):
            nonlocal classification
            if classification not in (Classification.RESTRICTED, Classification.CONFIDENTIAL):
                classification = Classification.INTERNAL
            return '[email]'
        
        processed_text = EMAIL_REGEX.sub(replace_email, processed_text)

        # 5. Phone
        def replace_phone(match):
            nonlocal classification
            if classification not in (Classification.RESTRICTED, Classification.CONFIDENTIAL):
                classification = Classification.INTERNAL
            return '[phone]'
        
        processed_text = PHONE_REGEX.sub(replace_phone, processed_text)

        return processed_text, classification


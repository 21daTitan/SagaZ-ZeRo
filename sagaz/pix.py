"""Static Brazilian PIX BR Code (EMV), no telemetry or configured key by default."""
from decimal import Decimal, InvalidOperation
import os
import unicodedata


def tlv(tag, value):
    if not isinstance(value, str):
        raise ValueError("Value must be text")
    size = len(value.encode("utf-8"))
    if size > 99:
        raise ValueError("BR Code TLV maximum 99 bytes")
    return f"{tag}{size:02d}{value}"


def crc16(value):
    crc = 0xFFFF
    for byte in value.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ (0x1021 if crc & 0x8000 else 0)) & 0xFFFF
    return f"{crc:04X}"


def clean_label(text, limit):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return "".join(c for c in text.upper() if c.isalnum() or c in " -.")[:limit].strip()


def static_brcode(key=None, name="SYSTEMIA SOLUTIONS", city="RIO DE JANEIRO", amount=None, txid="***"):
    key = (key if key is not None else os.environ.get("SAGA_PIX_KEY", "")).strip()
    if not key:
        raise ValueError("SAGA_PIX_KEY not configured; no placeholder is a real PIX key")
    if len(key.encode("utf-8")) > 77:
        raise ValueError("PIX key too long")
    merchant = tlv("00", "br.gov.bcb.pix") + tlv("01", key)
    data = tlv("00", "01") + tlv("26", merchant) + tlv("52", "0000") + tlv("53", "986")
    if amount is not None:
        try:
            number = Decimal(str(amount))
        except InvalidOperation as exc:
            raise ValueError("Invalid amount") from exc
        if not number.is_finite() or number <= 0:
            raise ValueError("Amount must be positive")
        data += tlv("54", f"{number:.2f}")
    name, city = clean_label(name, 25), clean_label(city, 15)
    if not name or not city:
        raise ValueError("Merchant name and city required")
    data += tlv("58", "BR") + tlv("59", name) + tlv("60", city)
    data += tlv("62", tlv("05", txid))
    data += "6304"
    return data + crc16(data)

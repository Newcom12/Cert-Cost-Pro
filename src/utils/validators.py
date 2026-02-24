"""Валидация ввода пользователя."""
import re

# Российский номер: +7..., 8..., 7...
PHONE_REGEX = re.compile(r"^(\+7|8|7)\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def normalize_phone(raw: str) -> str:
    """Убирает пробелы и скобки для проверки."""
    return re.sub(r"[\s\-\(\)]", "", raw)


def is_valid_phone(phone: str) -> bool:
    normalized = normalize_phone(phone)
    return bool(PHONE_REGEX.match(normalized)) and len(normalized) >= 11


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip())) if email else False

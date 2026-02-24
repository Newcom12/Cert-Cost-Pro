"""Расчёт стоимости сертификации по формуле из ТЗ."""
from typing import Tuple

# Базовые тарифы (₽)
BASE_PRICES = {
    "cert_tr_ts": 35_000,
    "declaration": 25_000,
    "iso": 120_000,
    "ce": 90_000,
    "halal": 70_000,
    "tm": 45_000,
}

# Коэффициент страны
K_COUNTRY = {
    "russia": 1.0,
    "china": 1.3,
    "turkey": 1.15,
    "eu": 1.2,
    "other": 1.25,
}

# Коэффициент срочности
K_URGENCY = {
    "standard": 1.0,
    "14": 1.25,
    "7": 1.5,
}

INSPECTION_COST = 18_000
MIN_CHECK = 25_000
ROUND_TO = 100


def k_sku(sku_count: int) -> float:
    """K_sku = 1 + (SKU_count - 1) * 0.08"""
    return 1.0 + (sku_count - 1) * 0.08


def round_price(value: float) -> int:
    """Округление до 100 ₽ вверх. Минимум 25 000 ₽."""
    rounded = int((value + ROUND_TO - 1) // ROUND_TO * ROUND_TO)
    return max(rounded, MIN_CHECK)


def calculate(
    service_key: str,
    country_key: str,
    sku_count: int,
    urgency_key: str,
    inspection_required: bool,
) -> Tuple[float, float, float, float, float, int]:
    """
    Возвращает: (base_price, k_country, k_sku, k_urgency, final_before_round, final_rounded).
    """
    base = BASE_PRICES.get(service_key, BASE_PRICES["cert_tr_ts"])
    k_c = K_COUNTRY.get(country_key, K_COUNTRY["other"])
    k_s = k_sku(sku_count)
    k_u = K_URGENCY.get(urgency_key, 1.0)
    inspection = INSPECTION_COST if inspection_required else 0

    subtotal = base * k_c * k_s * k_u
    final_before_round = subtotal + inspection
    final_rounded = round_price(final_before_round)

    return (base, k_c, k_s, k_u, final_before_round, final_rounded)

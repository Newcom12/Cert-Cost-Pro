"""Метрики для админ-панели: конверсия, средний чек, топ услуг и т.д."""
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Calculation, Lead


async def get_stats(session: AsyncSession) -> dict[str, Any]:
    """Общая статистика."""
    total_calcs = await session.scalar(select(func.count(Calculation.id)))
    total_leads = await session.scalar(select(func.count(Lead.id)))
    conversion = (total_leads / total_calcs * 100) if total_calcs and total_calcs > 0 else 0
    return {
        "total_calculations": total_calcs or 0,
        "total_leads": total_leads or 0,
        "conversion_percent": round(conversion, 1),
    }


async def get_avg_check(session: AsyncSession) -> float:
    """Средний чек по расчётам."""
    r = await session.execute(select(func.avg(Calculation.final_price)))
    avg = r.scalar()
    return round(float(avg or 0), 0)


async def get_top_services(session: AsyncSession, limit: int = 5) -> list[tuple[str, int]]:
    """Самые популярные услуги (по количеству расчётов)."""
    r = await session.execute(
        select(Calculation.service_type, func.count(Calculation.id))
        .group_by(Calculation.service_type)
        .order_by(func.count(Calculation.id).desc())
        .limit(limit)
    )
    return r.all()


async def get_top_countries(session: AsyncSession, limit: int = 5) -> list[tuple[str, int]]:
    """Самый частый коэффициент страны."""
    r = await session.execute(
        select(Calculation.country, func.count(Calculation.id))
        .group_by(Calculation.country)
        .order_by(func.count(Calculation.id).desc())
        .limit(limit)
    )
    return r.all()


async def get_calculations_per_day(session: AsyncSession, days: int = 7) -> list[tuple[datetime, int]]:
    """Количество расчётов по дням."""
    since = datetime.utcnow() - timedelta(days=days)
    r = await session.execute(
        select(func.date(Calculation.created_at), func.count(Calculation.id))
        .where(Calculation.created_at >= since)
        .group_by(func.date(Calculation.created_at))
        .order_by(func.date(Calculation.created_at))
    )
    return r.all()

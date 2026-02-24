"""Модели SQLAlchemy: users, calculations, leads."""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    calculations: Mapped[list["Calculation"]] = relationship(back_populates="user")
    leads: Mapped[list["Lead"]] = relationship(back_populates="user")


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    service_type: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(50))
    product_type: Mapped[str] = mapped_column(Text)
    sku_count: Mapped[int] = mapped_column()
    urgency: Mapped[str] = mapped_column(String(50))
    inspection_required: Mapped[bool] = mapped_column(Boolean, default=False)
    base_price: Mapped[float] = mapped_column(Float)
    k_country: Mapped[float] = mapped_column(Float)
    k_sku: Mapped[float] = mapped_column(Float)
    k_urgency: Mapped[float] = mapped_column(Float)
    final_price: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="calculations")
    leads: Mapped[list["Lead"]] = relationship(back_populates="calculation")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calculation_id: Mapped[int] = mapped_column(ForeignKey("calculations.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="new")  # new / contacted / closed
    manager_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    calculation: Mapped["Calculation"] = relationship(back_populates="leads")
    user: Mapped["User"] = relationship(back_populates="leads")

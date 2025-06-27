import asyncio
from datetime import datetime

from sqlalchemy import create_engine, String, DateTime, ForeignKey, Integer, BIGINT, UniqueConstraint, Index,DECIMAL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
engine = create_engine("postgresql+psycopg2://postgres:1@localhost:5432/academy")
DATABASE_URL = "postgresql+asyncpg://postgres:1@localhost:5432/academy"
Base = declarative_base()

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)
async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
 expire_on_commit=False,
)
class Customer(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    owm_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    daily_info: Mapped[list["DailyInfo"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    daily_payments: Mapped[list["DailyPayment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    async def save(self, session):
        session.add(self)
        await session.commit()

# ===================== Base Payment =====================
class BasePayment(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    pay: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    paid: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)

# ===================== Payment =====================
class Payment(BasePayment):
    __tablename__ = "payments"
    user: Mapped["Customer"] = relationship(back_populates="payments")

# ===================== Daily Payment =====================
class DailyPayment(BasePayment):
    __tablename__ = "daily_payments"
    user: Mapped["Customer"] = relationship(back_populates="daily_payments")

# ===================== Daily Info =====================
class DailyInfo(Base):
    __tablename__ = "daily_info"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    info: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["Customer"] = relationship(back_populates="daily_info")

# ===================== Admin =====================
class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)
    product_price: Mapped[int] = mapped_column(Integer, nullable=True)






# ===================== Admin =====================

async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
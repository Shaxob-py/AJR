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
    owm_name: Mapped[str] = mapped_column(String,nullable=True)
    username: Mapped[str] = mapped_column(String,nullable=True)
    name: Mapped[str] = mapped_column(String,nullable=True)
    phone_number: Mapped[int] = mapped_column(String,nullable=True)
    location : Mapped[str]=mapped_column(String,nullable=True)

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()

class BasePayment(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True)
    pay: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    user_id: Mapped[int] = mapped_column(BIGINT)
    paid: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    coordinates: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)

class Payment(BasePayment):
    __tablename__ = "payments"

class DailyPayment(BasePayment):
    __tablename__ = "daily_payment"

class DailyInfo(Base):
    __tablename__ = "daily_info"
    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String)






class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(String,nullable=True)
    password : Mapped[str]=mapped_column(String,nullable=True)

#
# class GroupUser(Base):
#     __tablename__ = "group_users"
#     id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
#     user_id: Mapped[int] = mapped_column(BIGINT)
#     group_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("groups.id"))
#     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#     user_name : Mapped[str]=mapped_column(String,nullable=True)
#     name : Mapped[str]=mapped_column(String,nullable=True)
#     group = relationship("Group")
#     count: Mapped[int] = mapped_column(BIGINT, default=0)
#
#     __table_args__ = (
#         Index("idx_groupuser_user_group", "user_id", "group_id"),)
# #
# class GroupUserSeven(Base):
#     __tablename__ = "group_users_seven"
#     id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
#     user_id: Mapped[int] = mapped_column(BIGINT)
#     group_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("groups.id"))
#     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#     user_name: Mapped[str] = mapped_column(String, nullable=True)
#     name: Mapped[str] = mapped_column(String, nullable=True)
#     group = relationship("Group")
#     count: Mapped[int] = mapped_column(BIGINT, default=0)
#
#     __table_args__ = (
#         Index("idx_groupuser_seven_user_group", "user_id", "group_id"),)
#
# class GroupUserMessage(Base):
#     __tablename__ = "group_user_messages"
#     id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
#     group_id:Mapped[int] = mapped_column(BIGINT, ForeignKey("groups.id"))
#     group_user_id: Mapped[int] = mapped_column(ForeignKey("group_users.id"))
#     message_text: Mapped[str] = mapped_column(String)
#     __table_args__ = (
#         UniqueConstraint("group_user_id", "message_text", name="uix_group_user_msg"),
#         Index("idx_gum_group_user", "group_user_id"),)

async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
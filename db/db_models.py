from sqlalchemy import Column, BigInteger, func, DECIMAL, DateTime, select
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncAttrs,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

from consts import (
    POSTGRESQL_USER,
    POSTGRESQL_PORT,
    POSTGRESQL_PASSWORD,
    POSTGRESQL_HOST,
    POSTGRESQL_DB_NAME,
)


engine = create_async_engine(
    f"postgresql+asyncpg://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:"
    f"{POSTGRESQL_PORT}/{POSTGRESQL_DB_NAME}",
    echo=False,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Weather(Base):
    __tablename__ = "weather"

    id = Column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    # дата обновления данных о погоде на сервере
    update_time = Column(DateTime)
    # температура по Цельсию
    temperature = Column(DECIMAL(10, 2))
    # осадки в мм
    precipitation = Column(DECIMAL(10, 2))
    # давление над уровнем моря гПа
    sea_level_pressure = Column(DECIMAL(10, 2))
    # давление гПа
    surface_pressure = Column(DECIMAL(10, 2))
    # скорость ветра в м/с
    wind_speed = Column(DECIMAL(10, 2))
    # направление ветра
    wind_direction = Column(DECIMAL(10, 2))

    @staticmethod
    async def add_weather(**kwargs):
        async with async_session() as session:
            new_weather = Weather(
                temperature=kwargs.get("temperature"),
                precipitation=kwargs.get("precipitation"),
                sea_level_pressure=kwargs.get("sea_level_pressure"),
                surface_pressure=kwargs.get("surface_pressure"),
                wind_speed=kwargs.get("wind_speed"),
                wind_direction=kwargs.get("wind_direction"),
                update_time=kwargs.get("update_time"),
            )
            session.add(new_weather)
            await session.commit()

    @staticmethod
    async def get_weather(rows_count=10):
        async with async_session() as session:
            res = await session.execute(
                select(
                    Weather.update_time,
                    Weather.temperature,
                    Weather.precipitation,
                    Weather.sea_level_pressure,
                    Weather.surface_pressure,
                    Weather.wind_speed,
                    Weather.wind_direction,
                )
                .order_by(Weather.created_at.desc())
                .limit(rows_count)
            )

        return res.all()

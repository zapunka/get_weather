import aioconsole
import aiohttp
from aiohttp.client_exceptions import ClientResponseError
import asyncio
from datetime import datetime
import pandas as pd

from consts import LATITUDE, LONGITUDE, OPEN_METEO_URL, WAIT_SEC, EXCEL_PATH
from db.db_models import Weather


async def get_weather():
    """
    Метод запрашивает данные о погоде с https://open-meteo.com/ и сохраняет их в БД
    """
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": [
            "temperature_2m",
            "precipitation",
            "pressure_msl",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "wind_speed_unit": "ms",
        "forecast_days": 1,
    }
    # запрос данных с open-meteo на текущее время по заданной гео-позиции
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.post(OPEN_METEO_URL, data=params) as resp:
            try:
                resp.raise_for_status()
            except ClientResponseError as ex:
                print(
                    f"Exception occurred while getting meteo data! Exception: {ex}"
                )

            print(f"Данные о погоде получены: {resp.status}")

            resp_json = await resp.json()
            current_weather = resp_json.get("current")
            update_time = datetime.strptime(
                current_weather.get("time"), "%Y-%m-%dT%H:%M"
            )
            # сохранение полученных данных в базу
            await Weather.add_weather(
                temperature=current_weather.get("temperature_2m"),
                precipitation=current_weather.get("precipitation"),
                sea_level_pressure=current_weather.get("pressure_msl"),
                surface_pressure=current_weather.get("surface_pressure"),
                wind_speed=current_weather.get("wind_speed_10m"),
                wind_direction=current_weather.get("wind_direction_10m"),
                update_time=update_time,
            )


async def download_xlsx():
    """
    Сохранение данных о погоде в файл формата xlsx по команде excel. Сохраняются последние 10 записей
    """
    command = await aioconsole.ainput(
        "Для скачивания файла с погодой введите команду excel\n"
    )
    if command == "excel":
        weather = await Weather.get_weather(10)
        df = pd.DataFrame(weather)
        df.to_excel(EXCEL_PATH)

        print("Файл успешно создан")


async def get_weather_scheduler():
    """
    Запрос погоды через заданный интервал времени
    """
    while True:
        await get_weather()
        await asyncio.sleep(WAIT_SEC)


async def main():
    await asyncio.gather(download_xlsx(), get_weather_scheduler())


if __name__ == "__main__":
    asyncio.run(main())

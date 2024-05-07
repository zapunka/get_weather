import os
from dotenv import dotenv_values


config = {
    **dotenv_values(".env"),
    **os.environ,
}


POSTGRESQL_USER = config.get("POSTGRESQL_USER")
POSTGRESQL_PASSWORD = config.get("POSTGRESQL_PASSWORD")
POSTGRESQL_HOST = config.get("POSTGRESQL_HOST")
POSTGRESQL_PORT = config.get("POSTGRESQL_PORT")
POSTGRESQL_DB_NAME = config.get("POSTGRESQL_DB_NAME")

# количество секунд между запросами погоды
WAIT_SEC = 20
# полный путь к файлу, куда выгружаем данные о погоде
EXCEL_PATH = "weather.xlsx"

LATITUDE = 55.6846556
LONGITUDE = 37.3125823
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

"""
Module smhi_lib contains the code to get forecasts from
the Swedish weather institute (SMHI) through the open
API:s
"""

import abc
import copy
import json
from collections import OrderedDict
from datetime import datetime
from typing import Any
from urllib.request import urlopen

import aiohttp

APIURL_TEMPLATE = (
    "https://opendata-download-metfcst.smhi.se/api/category"
    "/pmp3g/version/2/geotype/point/lon/{}/lat/{}/data.json"
)


class SmhiForecastException(Exception):
    """Exception thrown if failing to access API"""


class SmhiForecast:
    """
    Class to hold forecast data
    """

    # pylint: disable=R0913, R0902, R0914
    def __init__(
        self,
        temperature: float,
        temperature_max: float,
        temperature_min: float,
        humidity: int,
        pressure: float,
        thunder: int,
        cloudiness: int,
        precipitation: int,
        wind_direction: int,
        wind_speed: float,
        horizontal_visibility: float,
        wind_gust: float,
        mean_precipitation: float,
        total_precipitation: float,
        symbol: int,
        valid_time: datetime,
    ) -> None:
        """Constructor"""
        self._temperature = temperature
        self._temperature_max = temperature_max
        self._temperature_min = temperature_min
        self._humidity = humidity
        self._pressure = pressure
        self._thunder = thunder
        self._cloudiness = cloudiness
        self._precipitation = precipitation
        self._mean_precipitation = mean_precipitation
        self._total_precipitation = total_precipitation
        self._wind_speed = wind_speed
        self._wind_direction = wind_direction
        self.horizontal_visibility = horizontal_visibility
        self._wind_gust = wind_gust
        self._symbol = symbol
        self._valid_time = valid_time

    @property
    def temperature(self) -> float:
        """Air temperature (Celcius)"""
        return self._temperature

    @property
    def temperature_max(self) -> float:
        """Air temperature max during the day (Celcius)"""
        return self._temperature_max

    @property
    def temperature_min(self) -> float:
        """Air temperature min during the day (Celcius)"""
        return self._temperature_min

    @property
    def humidity(self) -> int:
        """Air humidity (Percent)"""
        return self._humidity

    @property
    def pressure(self) -> float:
        """Air pressure (hPa)"""
        return self._pressure

    @property
    def thunder(self) -> int:
        """Chance of thunder (Percent)"""
        return self._thunder

    @property
    def cloudiness(self) -> int:
        """Cloudiness (Percent)"""
        return self._cloudiness

    @property
    def wind_speed(self) -> float:
        """wind speed (m/s)"""
        return self._wind_speed

    @property
    def wind_direction(self) -> int:
        """wind direction (degrees)"""
        return self._wind_direction

    @property
    def precipitation(self) -> int:
        """Precipitation
        0	No precipitation
        1	Snow
        2	Snow and rain
        3	Rain
        4	Drizzle
        5	Freezing rain
        6	Freezing drizzle
        """
        return self._precipitation

    @property
    def mean_precipitation(self) -> float:
        """Mean Precipitation (mm/h)"""
        return self._mean_precipitation

    @property
    def total_precipitation(self) -> float:
        """Mean Precipitation (mm/h)"""
        return self._total_precipitation

    @property
    def wind_gust(self) -> float:
        """Wind gust (m/s)"""
        return self._wind_gust

    @property
    def symbol(self) -> int:
        """Symbol (Percent)
        1	Clear sky
        2	Nearly clear sky
        3	Variable cloudiness
        4	Halfclear sky
        5	Cloudy sky
        6	Overcast
        7	Fog
        8	Light rain showers
        9	Moderate rain showers
        10	Heavy rain showers
        11	Thunderstorm
        12	Light sleet showers
        13	Moderate sleet showers
        14	Heavy sleet showers
        15	Light snow showers
        16	Moderate snow showers
        17	Heavy snow showers
        18	Light rain
        19	Moderate rain
        20	Heavy rain
        21	Thunder
        22	Light sleet
        23	Moderate sleet
        24	Heavy sleet
        25	Light snowfall
        26	Moderate snowfall
        27	Heavy snowfall"""
        return self._symbol

    @property
    def valid_time(self) -> datetime:
        """Valid time"""
        return self._valid_time


# pylint: disable=R0903


class SmhiAPIBase:
    """
    Baseclass to use as dependecy incjection pattern for easier
    automatic testing
    """

    @abc.abstractmethod
    def get_forecast_api(self, longitude: str, latitude: str) -> dict[str, Any]:
        """Override this"""
        raise NotImplementedError(
            "users must define get_forecast to use this base class"
        )

    @abc.abstractmethod
    async def async_get_forecast_api(
        self, longitude: str, latitude: str
    ) -> dict[str, Any]:
        """Override this"""
        raise NotImplementedError(
            "users must define get_forecast to use this base class"
        )


# pylint: disable=R0903


class SmhiAPI(SmhiAPIBase):
    """Default implementation for SMHI api"""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        """Init the API with or without session"""
        self.session: aiohttp.ClientSession | None = session

    def get_forecast_api(self, longitude: str, latitude: str) -> dict[str, Any]:
        """gets data from API"""
        api_url = APIURL_TEMPLATE.format(longitude, latitude)

        response = urlopen(api_url)
        data = response.read().decode("utf-8")
        json_data = json.loads(data)

        return json_data

    async def async_get_forecast_api(
        self, longitude: str, latitude: str
    ) -> dict[str, Any]:
        """gets data from API asyncronious"""
        api_url = APIURL_TEMPLATE.format(longitude, latitude)

        is_new_session = False
        if self.session is None:
            self.session = aiohttp.ClientSession()
            is_new_session = True

        async with self.session.get(api_url) as response:
            if response.status != 200:
                if is_new_session:
                    await self.session.close()
                raise SmhiForecastException(
                    f"Failed to access weather API with status code {response.status}"
                )
            data = await response.text()
            if is_new_session:
                await self.session.close()

            return json.loads(data)


class Smhi:
    """
    Class that use the Swedish Weather Institute (SMHI) weather forecast
    open API to return the current forecast data
    """

    def __init__(
        self,
        longitude: str,
        latitude: str,
        session: aiohttp.ClientSession = None,
    ) -> None:
        self._longitude = str(round(float(longitude), 6))
        self._latitude = str(round(float(latitude), 6))
        self._api = SmhiAPI(session)

    def get_forecast(self) -> list[SmhiForecast]:
        """
        Returns a list of forecasts. The first in list are the current one
        """
        json_data = self._api.get_forecast_api(self._longitude, self._latitude)
        return _get_forecast(json_data)

    def get_forecast_hour(self) -> list[SmhiForecast]:
        """
        Returns a list of forecasts by hour. The first in list are the current one
        """
        json_data = self._api.get_forecast_api(self._longitude, self._latitude)
        return _get_forecast_hour(json_data)

    async def async_get_forecast(self) -> list[SmhiForecast]:
        """
        Returns a list of forecasts. The first in list are the current one
        """
        json_data = await self._api.async_get_forecast_api(
            self._longitude, self._latitude
        )
        return _get_forecast(json_data)

    async def async_get_forecast_hour(self) -> list[SmhiForecast]:
        """
        Returns a list of forecasts by hour. The first in list are the current one
        """
        json_data = await self._api.async_get_forecast_api(
            self._longitude, self._latitude
        )
        return _get_forecast_hour(json_data)


# pylint: disable=R0914, R0912, W0212, R0915
def _get_forecast(api_result: dict) -> list[SmhiForecast]:
    """Converts results fråm API to SmhiForecast list"""
    forecasts = []

    # Need the ordered dict to get
    # the days in order in next stage
    forecasts_ordered = OrderedDict()

    forecasts_ordered = _get_all_forecast_from_api(api_result)

    # Used to calc the daycount
    day_nr = 1

    forecast_day: SmhiForecast
    for day in forecasts_ordered:
        forecasts_day = forecasts_ordered[day]

        if day_nr == 1:
            # Add the most recent forecast
            forecasts.append(copy.deepcopy(forecasts_day[0]))

        total_precipitation = float(0.0)
        forecast_temp_max = -100.0
        forecast_temp_min = 100.0
        forecast = None
        for forecast_day in forecasts_day:
            temperature = forecast_day.temperature
            if forecast_temp_min > temperature:
                forecast_temp_min = temperature
            if forecast_temp_max < temperature:
                forecast_temp_max = temperature

            if forecast_day.valid_time.hour == 12:
                forecast = copy.deepcopy(forecast_day)

            total_precipitation = (
                total_precipitation + forecast_day._total_precipitation
            )

        if forecast is None:
            # We passed 12 noon, set to current
            forecast = forecasts_day[0]

        forecast._temperature_max = forecast_temp_max
        forecast._temperature_min = forecast_temp_min
        forecast._total_precipitation = total_precipitation
        forecast._mean_precipitation = total_precipitation / 24
        forecasts.append(forecast)
        day_nr = day_nr + 1

    return forecasts


def _get_forecast_hour(api_result: dict) -> list[SmhiForecast]:
    """Converts results fråm API to SmhiForecast list"""
    forecasts = []

    # Need the ordered dict to get
    # the days in order in next stage
    forecasts_ordered = OrderedDict()

    forecasts_ordered = _get_all_forecast_from_api(api_result)

    forecast_hour: SmhiForecast
    for day in forecasts_ordered:
        for forecast_hour in forecasts_ordered[day]:
            forecast = forecast_hour
            forecast._total_precipitation = forecast._mean_precipitation

            forecasts.append(forecast)

    return forecasts


# pylint: disable=R0914, R0912, W0212, R0915


def _get_all_forecast_from_api(api_result: dict) -> OrderedDict:
    """Converts results fråm API to SmhiForecast list"""
    # Total time in hours since last forecast
    total_hours_last_forecast = 1.0

    # Last forecast time
    last_time = None

    # Need the ordered dict to get
    # the days in order in next stage
    forecasts_ordered = OrderedDict()

    # Get the parameters
    for forecast in api_result["timeSeries"]:
        valid_time = datetime.strptime(forecast["validTime"], "%Y-%m-%dT%H:%M:%S%z")
        for param in forecast["parameters"]:
            if param["name"] == "t":
                temperature = float(param["values"][0])  # Celcisus
            elif param["name"] == "r":
                humidity = int(param["values"][0])  # Percent
            elif param["name"] == "msl":
                pressure = float(param["values"][0])  # hPa
            elif param["name"] == "tstm":
                thunder = int(param["values"][0])  # Percent
            elif param["name"] == "tcc_mean":
                octa = int(param["values"][0])  # Cloudiness in octas
                if 0 <= octa <= 8:  # Between 0 -> 8
                    cloudiness = round(100 * octa / 8)  # Convert octas to percent
                else:
                    cloudiness = 100  # If not determined use 100%
            elif param["name"] == "Wsymb2":
                symbol = int(param["values"][0])  # category
            elif param["name"] == "pcat":
                precipitation = int(param["values"][0])  # percipitation
            elif param["name"] == "pmean":
                mean_precipitation = float(param["values"][0])  # mean_percipitation
            elif param["name"] == "ws":
                wind_speed = float(param["values"][0])  # wind speed
            elif param["name"] == "wd":
                wind_direction = int(param["values"][0])  # wind direction
            elif param["name"] == "vis":
                horizontal_visibility = float(param["values"][0])  # Visibility
            elif param["name"] == "gust":
                wind_gust = float(param["values"][0])  # wind gust speed

        if last_time is not None:
            total_hours_last_forecast = (valid_time - last_time).seconds / 60 / 60

        # Total precipitation, have to calculate with the nr of
        # hours since last forecast to get correct total value
        total_precipitation = round(mean_precipitation * total_hours_last_forecast, 2)

        forecast = SmhiForecast(
            temperature,
            temperature,
            temperature,
            humidity,
            pressure,
            thunder,
            cloudiness,
            precipitation,
            wind_direction,
            wind_speed,
            horizontal_visibility,
            wind_gust,
            round(mean_precipitation, 1),
            total_precipitation,
            symbol,
            valid_time,
        )

        if valid_time.day not in forecasts_ordered:
            # add a new list
            forecasts_ordered[valid_time.day] = []

        forecasts_ordered[valid_time.day].append(forecast)

        last_time = valid_time

    return forecasts_ordered

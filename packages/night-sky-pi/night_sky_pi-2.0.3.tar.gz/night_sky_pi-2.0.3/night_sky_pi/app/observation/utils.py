"""
This module contains utility functions for calculating astronomical observations.

The main function in this module is `get_observation`, which calculates the observation period for a specific location and date, and returns an Observation object. The observation period is based on the sunrise and sunset times for the given location and date.

Functions:
    get_observation(configuration: ObservatoryConfig, a_datetime: datetime) -> Observation:
        Calculate the observation period for a specific location and date, and return an Observation object.

"""

from datetime import datetime, timedelta
import logging as log
from typing import Tuple

from suntime import Sun

from ..configuration.configuration import ObservatoryConfig
from ..configuration.core_configuration import LocationConfig
from .data import Observation, ObservationData, Period


def get_observation(
    configuration: ObservatoryConfig, a_datetime: datetime
) -> Observation:
    """
    Calculate the observation period for a specific location and date, and return an Observation object.

    This function calculates the observation period based on the sunrise and sunset times for the given location and date.
    It then creates an Observation object with the calculated start and end times.

    Args:
        configuration (ObservatoryConfig): The configuration object containing the location for which to calculate the observation period.
        a_datetime (datetime): The date for which to calculate the observation period.

    Returns:
        Observation: An Observation object with the calculated start and end times.
    """
    location = configuration.device.location
    log.debug("getting observation for %s @ %s", a_datetime, location.to_json())

    _, sunset_yesterday = __get_sun_data(location, a_datetime - timedelta(days=1))
    sunrise_today, sunset_today = __get_sun_data(location, a_datetime)
    sunrise_tomorrow, _ = __get_sun_data(location, a_datetime + timedelta(days=1))

    if sunrise_today.timestamp() < a_datetime.timestamp():
        log.debug("current day of observation we are after sunrise today")
        log.debug("start is sunset today and sunrise tomorrow")
        observation_start = sunset_today
        observation_end = sunrise_tomorrow
    else:
        log.debug("current date has moved to next day we are before sunrise")
        log.debug("start is sunset yesterday and sunrise today")
        observation_start = sunset_yesterday
        observation_end = sunrise_today

    period = Period(observation_start, observation_end)
    log.debug("observation start %s", period.start)
    log.debug("observation end %s", period.end)
    log.debug("observation title %s", period.date)
    log.debug(
        "are we within an observation period : %s",
        period.within_observation_period(a_datetime),
    )

    data = ObservationData(configuration.nsp.data, configuration.data, period)
    log.debug("data root is %s", data.root_path)
    log.debug("observation root is %s", data.path)
    return Observation(period, data)


def __get_sun_data(
    location: LocationConfig, for_datetime: datetime
) -> Tuple[datetime, datetime]:
    """
    Get the sunrise and sunset times for a specific location and date.

    This function uses the Sun class to calculate the local sunrise and sunset times
    for the given location and date.

    Args:
        location (LocationConfig): The location for which to get the sun data. This should be an instance of LocationConfig.
        for_datetime (datetime): The date for which to get the sun data.

    Returns:
        tuple: A tuple containing the sunrise and sunset times as datetime objects.

    """
    latitude, longitude = location.data()
    sun = Sun(latitude, longitude)
    log.debug("getting sun data for %s @ %s", location.to_json(), for_datetime)
    sunrise = sun.get_local_sunrise_time(for_datetime)
    sunset = sun.get_local_sunset_time(for_datetime)
    return sunrise, sunset

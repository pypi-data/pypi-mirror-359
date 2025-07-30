"""
This module defines data classes used in the observation module.

The main class in this module is `Period`, which represents an observation period with a start and end time. It also provides methods to check if a given datetime is within the observation period and to calculate the wait time until the observation period starts.

Classes:
    Period: Represents an observation period with a start and end time.

Functions:
    within_observation_period(for_datetime: datetime) -> bool:
        Check if a given datetime is within the observation period.

    calculate_wait_till_observation(for_datetime: datetime) -> int:
        Calculate the wait time in minutes until the observation period starts.
"""

from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json

from ..configuration.module_configuration import (
    HouseKeeping,
    ModuleDataConfig,
    DataConfig,
)


@dataclass_json
@dataclass(init=False)
class Period:
    """
    Represents an observation period with a start and end time.

    This class is used to represent an observation period for a specific location and date. It provides methods to check if a given datetime is within the observation period and to calculate the wait time until the observation period starts.

    Attributes:
        start (datetime): The start time of the observation period.
        end (datetime): The end time of the observation period.
    """

    start: datetime
    end: datetime
    date: str

    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end
        self.date = self.start.strftime("%Y-%m-%d")

    def within_observation_period(self, for_datetime: datetime) -> bool:
        """
        Check if a given datetime is within the observation period.

        This method checks if the given datetime is within the start and end times of the observation period.

        Args:
            for_datetime (datetime): The datetime to check.

        Returns:
            bool: True if the datetime is within the observation period, False otherwise.
        """
        timestamp = for_datetime.timestamp()
        return self.start.timestamp() < timestamp < self.end.timestamp()

    def calculate_wait_till_observation(self, for_datetime: datetime) -> int:
        """
        Calculate the wait time in minutes until the observation period starts.

        This method calculates the time difference between the given datetime and the start time of the observation period. If the given datetime is after the start time, the method returns 0.

        Args:
            for_datetime (datetime): The datetime for which to calculate the wait time.

        Returns:
            int: The wait time in minutes until the observation period starts.
        """
        wait_time = max((self.start - for_datetime).total_seconds(), 0)
        return int(wait_time)


@dataclass_json
@dataclass(init=False)
class ObservationData:
    """
    Represents the data collected during an observation period. Along with the paths of the data collected. with Optional housekeeping settings.
    """

    data_path: str
    root_path: str
    path: str
    observation_image_path: str
    observation_data_path: str
    house_keeping: HouseKeeping

    def __init__(
        self, module: ModuleDataConfig, global_data_config: DataConfig, period: Period
    ):
        self.data_path = f"{global_data_config.path}/"
        self.root_path = f"{self.data_path}{module.path}/"
        self.house_keeping = module.house_keeping
        self.path = f"{self.root_path}{period.date}/"
        self.observation_image_path = f"{self.path}images/"
        self.observation_data_path = f"{self.path}data/"


@dataclass_json
@dataclass
class Observation:
    """
    A class used to represent an observation.

    This class encapsulates the data and period of an observation. It uses an instance of the `Period` class to represent the observation period and an instance of the `ObservationData` class to represent the data collected during that period.

    Attributes:
        period (Period): The observation period.
        data_config (ObservationData): The data collected during the observation period.
    """

    period: Period
    data_config: ObservationData

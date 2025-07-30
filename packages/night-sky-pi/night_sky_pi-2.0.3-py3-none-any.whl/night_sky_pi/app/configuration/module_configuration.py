from dataclasses import dataclass
from typing import Optional
from dataclass_wizard import JSONWizard
from .core_configuration import LoggingConfig, DataConfig


@dataclass
class ModuleLoggingConfig(LoggingConfig):
    file: Optional[str] = None

    def merge(self, logging_config: LoggingConfig):
        if not self.path:
            self.path = logging_config.path
        if not self.level:
            self.level = logging_config.level
        if not self.format:
            self.format = logging_config.format
        if not self.rotation:
            self.rotation = logging_config.rotation


@dataclass
class HouseKeeping(JSONWizard):
    delete_after: int
    unit: Optional[str] = "DAYS"

    def __post_init__(self):
        if self.delete_after < 1.0:
            raise ValueError("Delete after must be greater or equal than 1.0")

    def get_age(self) -> int:
        if self.unit == "DAYS":
            return self.delete_after * 86400


@dataclass
class ModuleDataConfig(DataConfig):
    house_keeping: Optional[HouseKeeping] = None

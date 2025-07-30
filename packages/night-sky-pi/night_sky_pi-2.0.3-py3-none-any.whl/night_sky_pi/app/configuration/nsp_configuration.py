from dataclasses import dataclass, field
from typing import Optional
from dataclass_wizard import JSONWizard
from .module_configuration import ModuleDataConfig, ModuleLoggingConfig


@dataclass
class Shutter(JSONWizard):
    initial: Optional[int] = 250000
    slowest: Optional[int] = 15000000
    fastest: Optional[int] = 100
    current: Optional[int] = initial


@dataclass
class Gain(JSONWizard):
    initial: Optional[float] = 1.0
    lowest: Optional[float] = 1.0
    highest: Optional[float] = 8.0
    current: Optional[float] = initial


@dataclass
class WhiteBalance(JSONWizard):
    red: Optional[float] = 2.8
    blue: Optional[float] = 1.7


@dataclass
class Exposure(JSONWizard):
    target: Optional[float] = 100
    delay: Optional[int] = 5
    tolerance: Optional[float] = 0.01


@dataclass
class CaptureFormat(JSONWizard):
    file: Optional[str] = "jpg"


@dataclass
class ImageSize(JSONWizard):
    width: Optional[int] = 0
    height: Optional[int] = 0
    
@dataclass
class Capture(JSONWizard):
    shutter: Shutter = field(default_factory=Shutter)
    white_balance: WhiteBalance = field(default_factory=WhiteBalance)
    exposure: Exposure = field(default_factory=Exposure)
    format: CaptureFormat = field(default_factory=CaptureFormat)
    gain: Gain = field(default_factory=Gain)
    timeout: Optional[int] = 100
    size: ImageSize = field(default_factory=ImageSize)


@dataclass
class NSP(JSONWizard):
    logging: ModuleLoggingConfig
    data: ModuleDataConfig
    capture: Capture = field(default_factory=Capture)
    observation_cooldown: Optional[int] = 10

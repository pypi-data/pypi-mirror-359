from dataclasses import dataclass
from dataclass_wizard import JSONWizard
import json
from .core_configuration import DeviceConfig, LoggingConfig, DataConfig
from .nsp_configuration import NSP
from os.path import isfile


from logging.handlers import RotatingFileHandler

import logging
import os


@dataclass
class ObservatoryConfig(JSONWizard):
    device: DeviceConfig
    nsp: NSP
    logging: LoggingConfig
    data: DataConfig


def __configure_logging(configuration: ObservatoryConfig) -> None:
    configuration.nsp.logging.merge(configuration.logging)
    log_conf = configuration.nsp.logging

    if not os.path.exists(log_conf.path):
        os.makedirs(log_conf.path)

    file = f"{log_conf.path}/{log_conf.file}"
    handler = RotatingFileHandler(
        file, maxBytes=log_conf.rotation.size, backupCount=log_conf.rotation.backup
    )

    logging.basicConfig(
        level=log_conf.level,
        format=log_conf.format.output,
        datefmt=log_conf.format.date,
        handlers=[handler],
    )

    logging.info("configuration created")


def __configure_data(configuration: ObservatoryConfig) -> None:
    if not os.path.exists(configuration.data.path):
        logging.info("creating data directory %s", configuration.data.path)
        os.makedirs(configuration.data.path)


def build_configuration(config_path: str) -> ObservatoryConfig:
    if not isfile(config_path):
        raise IOError("Configuration file not found.")
    with open(config_path) as configuration_file:
        file_contents = configuration_file.read()
    configuration = ObservatoryConfig.from_dict(json.loads(file_contents))
    __configure_logging(configuration)
    __configure_data(configuration)
    return configuration

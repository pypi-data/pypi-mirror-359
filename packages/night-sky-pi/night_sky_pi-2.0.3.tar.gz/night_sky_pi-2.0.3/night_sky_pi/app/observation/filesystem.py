"""
filesystem.py
-------------

This module contains utility functions for setting up and managing the filesystem for observations.

Functions:
    setup_observation_filesystem(observation: Observation) -> Observation:
        Checks if the directory for the given observation exists, and if not, creates it.
"""

import logging as log
import os

from .data import Observation


def setup_observation_filesystem(observation: Observation) -> Observation:
    """
    Checks if the directory for the given observation exists, and if not, creates it.

    Parameters:
        observation (Observation): The observation for which to check and possibly create a directory.

    Returns:
        Observation: The same observation that was passed in. This allows for function chaining.
    """
    log.debug("checking directories for observation %s", observation.period.date)
    if not os.path.exists(observation.data_config.path):
        log.info(
            "creating observation %s directory at %s",
            observation.period.date,
            observation.data_config.path,
        )
        os.makedirs(observation.data_config.path)
        os.makedirs(observation.data_config.observation_image_path)
        os.makedirs(observation.data_config.observation_data_path)

    return observation

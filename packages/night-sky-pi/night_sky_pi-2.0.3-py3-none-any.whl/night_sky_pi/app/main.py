from .configuration.configuration import build_configuration
import logging as log
from datetime import datetime, timezone
from .observation.utils import get_observation
from .observation.filesystem import setup_observation_filesystem
from .housekeeping import perform_housekeeping
from .packaging import perform_packaging
from .capture.imaging import perform_observation

from time import sleep


def run(arguments):

    while True:
        configuration = build_configuration(arguments.configuration)

        current_datetime = datetime.now()
        log.debug("starting the root loop")
        log.debug("current datetime is %s", current_datetime)
        observation = get_observation(configuration, current_datetime)

        if observation.period.within_observation_period(current_datetime):
            log.info(
                "observation %s till %s",
                observation.period.date,
                observation.period.end,
            )
            observation = setup_observation_filesystem(observation)
            perform_observation(observation, configuration)
            log.info(
                "waiting configured time before performing additional tasks for %s minutes",
                configuration.nsp.observation_cooldown,
            )
            sleep(configuration.nsp.observation_cooldown * 60)
        else:
            log.info("not within observation period")
            perform_housekeeping(configuration)
            perform_packaging(configuration)
            seconds_till_observation = (
                observation.period.calculate_wait_till_observation(
                    datetime.now(timezone.utc)
                )
            )
            log.debug("%s seconds till observation start", seconds_till_observation)
            log.info("waiting for observation period at %s", observation.period.start)
            sleep(seconds_till_observation)
        log.debug("ending the root loop")

        if arguments.test_mode:  # in test no infinite loop
            break

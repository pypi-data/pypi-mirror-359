import json
import logging as log
from ..utilities.conversions import microsecond_to_seconds
from ..observation.data import Observation
from ..configuration.nsp_configuration import Capture


def create_json_file(
    observation: Observation, capture: Capture, file_name: str, image_format: str
) -> dict:
    json_data = {
        "observation": {
            "date": observation.period.date,
            "start": observation.period.start.isoformat(),
            "end": observation.period.end.isoformat(),
        },
        "data": {
            "path": observation.data_config.path,
            "root_path": observation.data_config.root_path,
            "observation_image_path": observation.data_config.observation_image_path,
            "observation_data_path": observation.data_config.observation_data_path,
        },
        "exposure": {
            "shutter": microsecond_to_seconds(capture.shutter.current),
            "gain": capture.gain.current,
            "white_balance": {
                "red": capture.white_balance.red,
                "blue": capture.white_balance.blue,
            },
        },
        "image": {
            "path": f"{observation.data_config.observation_image_path}{file_name}{image_format}",
            "format": image_format,
            "filename": file_name,
        },
    }

    output_file = f"{observation.data_config.observation_data_path}{file_name}.json"
    log.debug("Creating JSON file: %s", output_file)
    try:
        with open(output_file, "w") as json_file:
            json.dump(json_data, json_file)
        log.debug("JSON file created successfully: %s", output_file)
        return json_data
    except Exception as e:
        log.error("Failed to create JSON file: %s", e)

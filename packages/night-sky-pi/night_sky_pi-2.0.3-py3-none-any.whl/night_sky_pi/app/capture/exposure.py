import logging as log
from PIL import Image
from ..configuration.nsp_configuration import Capture
from ..utilities.conversions import microsecond_to_seconds


def calculate_next_exposure_value(image_path, capture: Capture):

    average_brightness = calculate_average_brightness(image_path)

    log.debug("Average brightness: %s", average_brightness)
    current_shutter_speed = capture.shutter.current
    current_gain = capture.gain.current
    brightness_threshold = capture.exposure.target
    tolerance = capture.exposure.tolerance
    lower_threshold = brightness_threshold - tolerance
    upper_threshold = brightness_threshold + tolerance

    new_gain = current_gain
    new_shutter_speed = current_shutter_speed

    brightness_difference = abs(
        max(
            average_brightness - brightness_threshold,
            brightness_threshold - average_brightness,
        )
    )
    log.debug("Brightness difference: %s", brightness_difference)
    # Calculate adjustments
    if average_brightness < lower_threshold:
        # Image is too dark, increase shutter speed and gain
        log.debug("Image is too dark, increasing shutter speed and gain")
        temp_shutter = min(
            current_shutter_speed + (brightness_difference + current_shutter_speed),
            capture.shutter.slowest,
        )
        if temp_shutter < capture.shutter.slowest:
            new_shutter_speed = temp_shutter
        else:
            new_shutter_speed = capture.shutter.slowest
            new_gain = min(
                current_gain + (brightness_difference * current_gain),
                capture.gain.highest,
            )

    elif average_brightness > upper_threshold:
        log.debug("Image too bright, decreasing shutter speed and increasing gain")
        log.debug("current_gain: %s", current_gain)
        log.debug("capture.gain.lowest: %s", capture.gain.lowest)
        if current_gain == capture.gain.lowest:
            log.debug("Decreasing Shutter Speed")
            new_shutter_speed = max(
                current_shutter_speed - (current_shutter_speed * brightness_difference),
                capture.shutter.fastest,
            )
        else:
            log.debug("Decreasing Gain")
            new_gain = max(
                current_gain - (brightness_difference * current_gain),
                capture.gain.lowest,
            )
    else:
        # Image is within the target range
        log.debug("Image is within the target range, no adjustments needed")
        new_shutter_speed = current_shutter_speed
        new_gain = current_gain

    # Update the capture configuration
    capture.shutter.current = new_shutter_speed
    capture.gain.current = new_gain
    log.debug("New shutter speed: %s", microsecond_to_seconds(capture.shutter.current))
    log.debug("New gain: %s", capture.gain.current)
    log.debug("Next exposure value calculated")


def calculate_average_brightness(image_path):
    log.debug("Calculating next exposure value")
    image = Image.open(image_path, formats=["JPEG"])
    crop = image.convert("L")
    histogram = crop.histogram()
    pixels = sum(histogram)
    brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        brightness += ratio * (-scale + index)

    average_brightness = 1 if brightness == 255 else round(brightness / scale, 2)
    return average_brightness

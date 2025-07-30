import argparse

from .app.main import run


def night_sky_pi():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration", type=str, required=True)
    arguments = parser.parse_args(None)
    run(arguments)


# Night Sky Pi

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/joe-mccarthy/night-sky-pi/build-test.yml?cacheSeconds=1&style=for-the-badge)](https://github.com/joe-mccarthy/night-sky-pi/actions/workflows/build-test.yml)
[![Coveralls](https://img.shields.io/coverallsCoverage/github/joe-mccarthy/night-sky-pi?cacheSeconds=1&style=for-the-badge)](https://coveralls.io/github/joe-mccarthy/night-sky-pi)
[![Sonar Quality Gate](https://img.shields.io/sonar/quality_gate/joe-mccarthy_night-sky-pi?server=https%3A%2F%2Fsonarcloud.io&cacheSeconds=1&style=for-the-badge)](https://sonarcloud.io/project/overview?id=joe-mccarthy_night-sky-pi)
![PyPI - Version](https://img.shields.io/pypi/v/night-sky-pi?style=for-the-badge&link=https%3A%2F%2Fpypi.org%2Fproject%2Fnight-sky-pi%2F)
[![GitHub License](https://img.shields.io/github/license/joe-mccarthy/night-sky-pi?cacheSeconds=1&style=for-the-badge)](LICENSE)

Night Sky Pi is a camera that takes images throughout the night currently from sunset till sunrise. These images are then zipped then the application waits for the next observation period. Along with the images that are taken there are supporting json files for each image with additional information. These data files currently contain the exposure and observation information for the image, allowing for processing off device later.

There could be additional json files created by other supporting applications. The Night Sky Pi can use MQTT to publish events so one could write other applications that respond to these events to complete additional task. One example would be to add weather information to the json file. Note: MQTT is not required for standard operation only for other applications to interact with the data in a timely manner.

## Hardware

Night Sky Pi has been created with certain hardware in mind. Wanting to keep the application simple, small and low cost the hardware that Night Sky Pi has targeted is the __Raspberry Pi Zero 2 W__. That being said any __Raspberry Pi__ more capable than this model should work fine. The camera used and tested is the __Raspberry Pi HQ Camera__, however the standard camera model could be used ensuring that the exposure times within the configuration are kept within the models capabilities.

## Prerequisites

Before deploying the Night Sky Pi it's important to ensure that you have the following configured as there are dependencies. However the installation of an MQTT broker is optional I usually have it installed instead of needing to remember to do it when starting up other applications.

### MQTT Broker

Night Sky Pi has the ability to publish events to an MQTT broker. The intent of this is so that other modules can react to the events to complete additional actions. Initially this broker will only run locally therefore only allow clients that reside on the same device as intended. Firstly we need to install MQTT on the Raspberry Pi.

```bash
sudo apt update && sudo apt upgrade
sudo apt install -y mosquitto
sudo apt install -y mosquitto-clients # Optional for testing locally
sudo systemctl enable mosquitto.service
sudo reboot # Just something I like to do, this is optional as well
```

The next step is to configure the Night Sky Pi to use the MQTT broker, as MQTT events are disabled by default.

```json
"device" : {
    "mqtt" : {
        "enabled": true,
        "host": "127.0.0.1"
    }
}
```

## Configuration

All configuration of the Night Sky Pi is done through the [config.json](config.json), which is passed into the Night Sky Pi as an argument. It's best not to update the configuration within the repository but to copy it to another location and use that for running the Night Sky Pi.

### Configuration Items

The json file structure is as follows:

- __device__ : [details](#device)
- __logging__ : [details](#logging)
- __data__ : [details](#data)
- __nsp__ : [details](#nsp)

#### Device

- __name__ : Friendly name for the camera
- __location__ : The location of the camera, this is used to calculate sun position.
  - __latitude__ : double for the latitude of the device
  - __longitude__ : double for the longitude of the device
- __mqtt__ : MQTT settings for the device
  - __enabled__ : boolean if enabled, mqtt is disabled by default
  - __host__ : location of mqtt broker, default and recommended is localhost

#### Logging

- __path__ : location of the log file
- __level__ : the level at which to log at
- __format__ : log formatting options
  - __date__ : how to represent dates
  - __output__ : how to print log statements
- __rotation__ : logging roll over settings
  - __size__ : the size of the log file before rolling over
  - __backup__ : the number of old log files to keep before deletion

#### Data

- __path__ : Root directory to save all created data

#### NSP

- __observation_cooldown__ : Time to wait in minutes between the end of an observation and starting housekeeping
- __data__ : [details](#nsp-data)
- __logging__ : [details](#nsp-logging)
- __capture__ : [details](#nsp-capture)

##### NSP Data

- __path__ : location to save the observations, this path will be appended to the root data path
- __house_keeping__ : housekeeping configuration
  - __delete_after__ : number of days to keep archived observation data, if set to 0 then no data is ever deleted

##### NSP Logging

- __file__ : set the name of the logging file for the Night Sky Pi
- __level__ : override the logging level of the Night Sky Pi logging file

##### NSP Capture

- __shutter__ : Shutter speed time of exposure in microseconds
  - __initial__ : Starting shutter speed in microseconds
  - __slowest__ : Slowest allowed shutter speed in microseconds
  - __fastest__ : Fastest allowed shutter speed in microseconds
- __gain__ : Sensitivity of the camera sensor
  - __initial__ : Starting gain represented as a double
  - __lowest__ : Lowest gain represented as a double
  - __highest__ : Highest gain represented as a double
- __white_balance__ : The white balance settings
  - __red__ : Amount of red used for white balance represented as a double
  - __blue__ : Amount of blue used for white balance represented as a double
- __exposure__ : Desired exposure settings
  - __target__ : The desired brightness of the image represented as a double 0.00 black while 1.00 white
  - __delay__ : The time between taking images in seconds
  - __tolerance__ : Different between the image brightness and target exposure before recalculating new image capture settings
- __format__ : Options to save the captured image
  - __file__ : currently only supports "jpg"
- __timeout_seconds__: Time to state that the image capture failed default is 90 seconds. This should always be more than the slowest shutter speed.

## Running Night Sky Pi

It's recommended that Night Sky Pi is run as a service. This ensures that it doesn't stop of user logging off and on system restarts to do this carry out the following.

```bash
pip install night-sky-pi
sudo nano /etc/systemd/system/nsp.service
```

Next step is to update the service definition to the correct paths and running as the correct user.

```bash
[Unit]
Description=Night Sky Pi
After=network.target

[Service]
Type=Simple
# update this to be your current user
User=username 
# the location of the night sky to work in
WorkingDirectory=/home/username
# update these paths to be the location of the nsp.sh 
# update argument to where you previously copied the json configuration.
ExecStart=night-sky-pi -c /home/username/config.json 
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Next is to enable and start the service.

```sh
sudo systemctl daemon-reload
sudo systemctl start nsp
sudo systemctl enable nsp
```

## Outputs

During an observation period there will be a folder created with the observation date as configured in the json file. Within this directory there will be two directories. First is the images directory where the captured images are stored with the filename being the timestamp of capture. The second directory is the data directory that contains any created json or artifacts from other modules.

Once the observations has completed house keeping will delete any old files if configured. Then the last observation will be zipped with the same name as the observation data, and the source folder is deleted.

### MQTT

If MQTT has been [enabled](#mqtt-broker) on Night Sky Pi, there are a couple of events that are fired through the running of the application.

#### Observation Started

When an observation starts and the file structure has been created Night Sky Pi will fire an event to the "nsp/observation-started" topic, below is an example of what to expect in the message payload.

```json
{
    "observation": {
        "date": "2024-09-04",
        "start": "2024-09-04T19:38:00+01:00",
        "end": "2024-09-05T06:19:00+01:00"
    },
    "data": {
        "path": "/home/joseph/nsp/data/observations/2024-09-04/",
        "root_path": "/home/joseph/nsp/data/observations/",
        "observation_image_path": "/home/joseph/nsp/data/observations/2024-09-04/images/",
        "observation_data_path": "/home/joseph/nsp/data/observations/2024-09-04/data/"
    }
}
```

#### Image Captured

Each and every time that an image has been captured and saved to disk. Night Sky Pi will publish a message to the "nsp/image-captured" topic, below is an example of what to expect in the message payload.

```json
{
    "observation": {
        "date": "2024-09-04",
        "start": "2024-09-04T19:38:00+01:00",
        "end": "2024-09-05T06:19:00+01:00"
    },
    "data": {
        "path": "/home/joseph/nsp/data/observations/2024-09-04/",
        "root_path": "/home/joseph/nsp/data/observations/",
        "observation_image_path": "/home/joseph/nsp/data/observations/2024-09-04/images/",
        "observation_data_path": "/home/joseph/nsp/data/observations/2024-09-04/data/"
    },
    "exposure": {
        "shutter": 0.25,
        "gain": 1,
        "white_balance": {
            "red": 2.8,
            "blue": 1.7
        }
    },
    "image": {
        "path": "/home/joseph/nsp/data/observations/2024-09-04/images/1725490896.jpg",
        "format": ".jpg",
        "filename": "1725490896"
    }
}
```

### Observation Completed

When an observation has reached it's completed datetime Night Sky Pi will fire an event to the "nsp/observation-ended" topic, below is an example of what to expect in the message payload.

```json
{
    "observation": {
        "date": "2024-09-04",
        "start": "2024-09-04T19:38:00+01:00",
        "end": "2024-09-05T06:19:00+01:00"
    },
    "data": {
        "path": "/home/joseph/nsp/data/observations/2024-09-04/",
        "root_path": "/home/joseph/nsp/data/observations/",
        "observation_image_path": "/home/joseph/nsp/data/observations/2024-09-04/images/",
        "observation_data_path": "/home/joseph/nsp/data/observations/2024-09-04/data/"
    }
}
```

### Archive Deleted

During house keeping there is an configuration option to delete zipped archives that are older than a configured number of days. If enabled and an archive is deleted, Night Sky Pi will fire an event to the "nsp/file-deleted" topic, below is an example of what to expect in the message payload.

```json
{
    "file": "/home/joseph/nsp/data/observations/2024-08-30.zip"
}
```

### Archive Completed

After the observation and housekeeping the Night Sky Pi will archive the entire observation folder. This operation can take a while once completed, Night Sky Pi will fire an event to the "nsp/archive-completed" topic, below is an example of what to expect in the message payload.

```json
{
    "name": "2024-09-04",
    "format": "zip",
    "folder" : "/home/joseph/nsp/data/observations/",
    "path": "/home/joseph/nsp/data/observations/2024-09-04.zip"
}
```

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Don't forget to give the project a star! Thanks again!

1. Fork the Project
1. Create your Feature Branch (git checkout -b feature/AmazingFeature)
1. Commit your Changes (git commit -m 'Add some AmazingFeature')
1. Push to the Branch (git push origin feature/AmazingFeature)
1. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

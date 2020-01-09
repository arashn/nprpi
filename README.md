# nprpi
NPR One radio alarm clock on the Raspberry Pi

## Introduction
This is a radio alarm clcok application for the Raspberry Pi, which currently supports NPR One. It currently has a sleep timer feature

## Getting Started
To get started using this application, you will need an NPR One account. If you don't have one already, you can create one [here](https://dev.npr.org/user/login).

Once you have an NPR One account, create a new application in the [NPR One Developer Console](https://dev.npr.org/console). After you have created the application, make note of the Application ID and the Application Secret. You will use these later.

Clone this repo to your working directory. Then in the root directory of the repo, create a file named `credentials`. Write your application ID to the first line, and your application secret to the second line, and save the file.

### Prerequisites
You will need to have Python 3 and VLC Media Player installed on your system.

In addition, you will need to have the following Python packages installed
* python-vlc
* requests

I recommended that you use a Python virtual environment (e.g. virtualenv or pyenv) to set up the necessary Python version and dependencies.

### Running the app
To run the app, simply run `python main.py`. You should see a a URL and a code display on the Raspberry Pi display. You will need to go to this URL on another device and enter the code to authorize your Raspberry Pi device.

Once you have logged in and authorized your Raspberry Pi, you can use the buttons on the Raspberry Pi to play, pause, and stop, as well as to set the sleep timer.

## Roadmap
The following features are planned for future releases:
* Controlling the radio through a mobile app
* Setting alarms (through a mobile app)
* Adding other radio stations and channels

## Contributions
If you have any suggestions for new features that you would like to see, feel free to open an issue.

Also, If you would like to contribute to this project, feel free to fork this repo and create pull requests.

Thank you for your interest!

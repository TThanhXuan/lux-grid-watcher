## About
A python script allow watch Luxpower SNA inverter grid connect state

## Configuration
* Copy `.env.example` to `.env`
* Update configuration in `.env` with your personal info

## Installation and run
* Sync gitsubmodule with `git submodule init && git submodule update`
* Python 3 required
* Setup python venv with `python -m venv venv`
* Active python venv `source venv/Scripts/activate` on git-bash Windows or `source venv/bin/active` on Unix/Linux
* Install dependencies with `pip install -r requirements.txt` or `./pip-binary-install.sh`
* Run application with `python app.py`

## Notification app
You can implement notification app for Android/iOS by your self and push Firebase Device ID to devices.json file to get notification when grid connect state change.

I also developed an app for Android. If you need it feel free to contact me

## Webviewer
You can see LuxPower realtime webviewer in http://locahost:88 like image bellow. This webview is under development

<center><img src="misc/screenshot.png" style="max-width: 800px"/></center>

## Third-party

Thanks to [@celsworth](https://github.com/celsworth) by awesome project [celsworth/lxp-packet](https://github.com/celsworth/lxp-packet) *(has been deleted)* and [celsworth/lxp-bridge](https://github.com/celsworth/lxp-bridge) (under MIT License)

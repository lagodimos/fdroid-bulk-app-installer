
A script for quickly installing your favorite apps from F-Droid for the first time (on a new phone, after a custom rom installation etc.)

## Dependencies

- adb
- python3
- python3-venv

From the repository directory run

```
python3 -m venv venv
```

to create a new virtual environment and

```
pip install -r requirements.txt
```

to install the python modules

## Usage

1. Create an apps.yml file at the root of the directory with your apps. Look at `example_apps.yml`

2. Start the adb server

```
adb start-server
```

3. Connect your device to your machine with USB and allow debugging

*Wireless debugging is supported*

4. Run the script

```
python3 setup.py
```

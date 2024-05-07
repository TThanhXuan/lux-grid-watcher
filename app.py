from dotenv import dotenv_values
import logging.handlers
import pychromecast
import logging
import time
from os import path, environ
import dongle_handler
import http_handler
from datetime import datetime, timezone
from fcm import FCM
import json

DONGLE_MODE = "DONGLE"

AUDIO_SLEEP_MAP = {
    "has-grid.mp3": 6,
    "lost-grid.mp3": 9,
}

config = {
    **dotenv_values(".env"),
    **environ
}
log_level = logging.DEBUG if config["IS_DEBUG"] == 'True' else logging.INFO

logger = logging.getLogger(__file__)
log_file_handler = logging.handlers.RotatingFileHandler(
    config["LOG_FILE"],
    mode='a',
    maxBytes=500*1024,
    backupCount=3
)
log_file_handler.setFormatter(logging.Formatter(config["LOG_FORMAT"]))
log_file_handler.setLevel(log_level)
log_handlers: list[logging.Handler] = [
    log_file_handler
]
if log_level == logging.DEBUG:
    log_handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=log_level,
    format=config["LOG_FORMAT"],
    handlers=log_handlers
)


def play_audio(audio_file: str, repeat=3):
    chromecast, _ = pychromecast.get_listed_chromecasts(
        [config["CAST_DEVICE_NAME"]])
    if len(chromecast) > 0:
        cast = chromecast[0]
        logger.debug("Cast info: %s", cast.cast_info)
        cast.wait()
        logger.debug("Cast status: %s", cast.status)
        mediaController = cast.media_controller
        logger.info(
            "Playing %s on %s %s times repeat",
            audio_file,
            config["CAST_DEVICE_NAME"],
            repeat
        )
        while repeat > 0:
            mediaController.play_media(
                f"{config['AUDIO_BASE_URL']}/{audio_file}", "audio/mp3")
            mediaController.block_until_active()
            repeat = repeat - 1
            logger.info("Play time remaining: %s", repeat)
            if repeat > 0:
                logger.info("Wating for %s second before repeat",
                            AUDIO_SLEEP_MAP[audio_file])
            time.sleep(AUDIO_SLEEP_MAP[audio_file])
        logger.debug("MediaControler status: %s", mediaController.status)
    else:
        logger.info("No device to play audio")


def handle_grid_status(json_data: dict, fcm_service: FCM):
    # is_grid_connected = True
    is_grid_connected = json_data["fac"] > 0
    last_grid_connected = True
    disconnected_time = json_data["deviceTime"]
    if path.exists(config["STATE_FILE"]):
        with open(config["STATE_FILE"], 'r') as f:
            last_grid_connected = f.read() == "True"
        if not last_grid_connected:
            # Only get disconneced time from state file if disconnected from previos
            disconnected_time = datetime.fromtimestamp(
                path.getmtime(config['STATE_FILE'])
            ).strftime("%Y-%m-%d %H:%M:%S")
    status_text = json_data["status_text"] if "status_text" in json_data else json_data["status"]
    if not is_grid_connected:
        logger.warning(
            "_________Inverter disconnected from GRID since: %s with status: \"%s\"_________",
            disconnected_time,
            status_text,
        )
    else:
        logger.info(
            "_________Inverter currently connected to GRID with\nStatus: \"%s\" at deviceTime: %s with fac: %s Hz and vacr: %s V_________",
            status_text,
            json_data['deviceTime'],
            int(json_data['fac']) / 100,
            int(json_data['vacr']) / 10,
        )
    if last_grid_connected != is_grid_connected:
        current_history = []
        if path.exists(config['HISTORY_FILE']):
            with open(config['HISTORY_FILE'], 'r') as f_history:
                current_history = json.loads(f_history.read())
        if len(current_history) == int(config["HISTORY_COUNT"]):
            del current_history[len(current_history) - 1]
        current_history.insert(0, {
            "type": "ON_GRID" if is_grid_connected else "OFF_GRID",
            "time": json_data["deviceTime"],
        })
        with open(config['HISTORY_FILE'], 'w') as f_history_w:
            f_history_w.write(json.dumps(current_history))
        with open(config["STATE_FILE"], "w") as fw:
            fw.write(str(is_grid_connected))
        if is_grid_connected:
            fcm_service.ongrid_notify()
            play_audio("has-grid.mp3")
        else:
            logger.warning("All json data: %s", json_data)
            fcm_service.offgrid_notify()
            play_audio("lost-grid.mp3", 5)
    else:
        logger.info("State did not change. Skip play notify audio")


def main():
    try:
        logger.info("Grid connect watch working on mode: %s",
                    config["WORKING_MODE"])
        fcm_service = FCM(logger, config)
        if config["WORKING_MODE"] == DONGLE_MODE:
            dongle = dongle_handler.Dongle(logger, config)
            while True:
                inverter_data = dongle.get_dongle_input()
                if inverter_data is not None:
                    handle_grid_status(inverter_data, fcm_service)
                logger.info("Wating for %s second before next check",
                            config["SLEEP_TIME"])
                time.sleep(int(config["SLEEP_TIME"]))
        else:
            http = http_handler.Http(logger, config)
            while True:
                inverter_data = http.get_run_time_data()
                handle_grid_status(inverter_data, fcm_service)
                logger.info("Wating for %s second before next check",
                            config["SLEEP_TIME"])
                time.sleep(int(config["SLEEP_TIME"]))
    except Exception as e:
        logger.exception("Got error when run main %s", e)
        exit(1)


main()

import logging
from os import path
import json
import requests
import requests.auth


class FCM():
    __config: dict
    __logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: dict) -> None:
        self.__config = config
        self.__logger = logger

    def _get_access_token(self):
        return ""

    def __get_devices(self):
        if path.exists(self.__config["DEVICE_IDS_JSON_FILE"]):
            with open(self.__config["DEVICE_IDS_JSON_FILE"], "r") as fr:
                return json.loads(fr.read())
        return []

    def __send_notify(self, title: str, body: str, devices: list[str]):
        self.__logger.debug(
            "Send notify with title: %s and body: %s to %s devices", title, body, len(devices))
        requests.post(
            "https://fcm.googleapis.com/v1/projects/chiasenhac-c845e/messages:send",
            body=json.dumps({
                "message": {
                    "notification": {
                        "title": title,
                        "body": body
                    },
                    "data": {
                        "title": title,
                        "body": body
                    }
                },
                "tokens": devices,
            }),
            headers={
                'Authorization': 'Bearer ' + self._get_access_token(),
                'Content-Type': 'application/json; UTF-8',
            }
        )

    def ongrid_notify(self):
        self.__logger.debug("ON: Start send notify")
        devices = self.__get_devices()
        if len(devices) == 0:
            self.__logger.debug("ON: No device to notify")
        else:
            self.__send_notify(
                "Đã có điện lưới.",
                "Nhà đã có điện lưới có thể sử dụng điện không giới hạn.",
                devices
            )
        self.__logger.debug("ON: Finish send notify")

    def offgrid_notify(self):
        self.__logger.debug("OFF: Start send notify")
        devices = self.__get_devices()
        if len(devices) == 0:
            self.__logger.debug("OFF: No device to notify")
        else:
            self.__send_notify(
                "Mất điện lưới.",
                "Nhà đã mất điện lưới cần hạn chế sử dụng thiết bị điện công suất lớn như bếp từ, bình nóng lạnh.",
                devices
            )
        self.__logger.debug("OFF: Finish send notify")
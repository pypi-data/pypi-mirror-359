import logging

import evdev

from ..config import Config
from ..device import Device
from ..util import BluetoothName

logger = logging.getLogger(__name__)


class DeviceManager:
    def __init__(self, config: Config):
        self.device_list = []
        self.config = config

    def scan_new_device(self):
        new_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        new_devices = list(
            filter(
                lambda device: (
                    device.uniq not in [d.inputDevice.uniq for d in self.device_list]
                    and (
                        device.name == BluetoothName.JOY_CON_LEFT
                        or device.name == BluetoothName.JOY_CON_RIGHT
                        or device.name == BluetoothName.PRO_CONTOLLER
                    )
                ),
                new_devices,
            )
        )
        for inputDevice in new_devices:
            device = Device(inputDevice, self.config)
            device.start()
            logger.info(
                "Start new device: %s, %s",
                device.inputDevice.name,
                device.inputDevice.uniq,
            )

            self.device_list.append(device)

    def clean_dead_device(self):
        for device in self.device_list[:]:
            if not device.is_alive():
                self.device_list.remove(device)
                logger.info(
                    "Remove device: %s, %s",
                    device.inputDevice.name,
                    device.inputDevice.uniq,
                )

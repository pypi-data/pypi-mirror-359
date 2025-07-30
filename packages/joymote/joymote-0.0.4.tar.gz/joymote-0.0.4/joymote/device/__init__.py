import logging
import subprocess
import threading

from evdev import InputDevice, InputEvent, UInput
from evdev import ecodes as e

from ..config import AnalogInput, Config, ControllerConfig, KeyInput, MouseTarget
from ..device.analog import CursorThread, ScrollThread
from ..util import (
    BluetoothName,
    CommandTarget,
    CursorDirectionTarget,
    Direction,
    KeyboardTarget,
    ScrollDirectionTarget,
)

logger = logging.getLogger(__name__)


class Device(threading.Thread):
    def __init__(self, inputDevice: InputDevice, config: Config):
        threading.Thread.__init__(self, daemon=True)

        self.inputDevice = inputDevice
        self.config = config
        self.controller_config: ControllerConfig = (
            config.joy_con_left
            if inputDevice.name == BluetoothName.JOY_CON_LEFT
            else config.joy_con_right
            if inputDevice.name == BluetoothName.JOY_CON_RIGHT
            else config.pro_contoller
            # if inputDevice.name == BluetoothName.PRO_CONTOLLER
        )
        self.keyboard_ui = UInput()
        self.mouse_ui = UInput(
            {
                e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT],
                e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL_HI_RES, e.REL_HWHEEL_HI_RES],
            }
        )

        cursor_idle_range = (
            self.controller_config.options["left_analog_idle_range"]
            if (
                self.controller_config.mapper.translate(AnalogInput.LEFT_ANALOG)
                == MouseTarget.CURSOR
            )
            else self.controller_config.options["right_analog_idle_range"]
            if (
                self.controller_config.mapper.translate(AnalogInput.RIGHT_ANALOG)
                == MouseTarget.CURSOR
            )
            else self.controller_config.options["analog_idle_range"]
            if (
                self.controller_config.mapper.translate(AnalogInput.ANALOG)
                == MouseTarget.CURSOR
            )
            else 1.0
        )
        scroll_idle_range = (
            self.controller_config.options["left_analog_idle_range"]
            if (
                self.controller_config.mapper.translate(AnalogInput.LEFT_ANALOG)
                == MouseTarget.SCROLL
            )
            else self.controller_config.options["right_analog_idle_range"]
            if (
                self.controller_config.mapper.translate(AnalogInput.RIGHT_ANALOG)
                == MouseTarget.SCROLL
            )
            else self.controller_config.options["analog_idle_range"]
            if (
                self.controller_config.mapper.translate(AnalogInput.ANALOG)
                == MouseTarget.SCROLL
            )
            else 1.0
        )

        self.cursor_thread = CursorThread(
            self.mouse_ui,
            speed=self.controller_config.options["cursor_speed"],
            idle_range=cursor_idle_range,
        )
        self.scroll_thread = ScrollThread(
            self.mouse_ui,
            speed=self.controller_config.options["scroll_speed"],
            idle_range=scroll_idle_range,
            revert_x=self.controller_config.options["revert_scroll_x"],
            revert_y=self.controller_config.options["revert_scroll_y"],
        )

    def push(self, event: InputEvent):
        key_input = KeyInput.from_event(event, self.controller_config.controller_type)
        analog_input = AnalogInput.from_event(
            event, self.controller_config.controller_type
        )

        if key_input is not None:
            target = self.controller_config.mapper.translate(key_input)
            if isinstance(target, KeyboardTarget):
                self.keyboard_ui.write(e.EV_KEY, target.ecodes, 1)
                self.keyboard_ui.write(e.EV_KEY, target.ecodes, 0)
                self.keyboard_ui.syn()
            elif isinstance(target, CommandTarget):
                subprocess.Popen(target.command, stdout=subprocess.DEVNULL, shell=True)
            elif isinstance(target, CursorDirectionTarget):
                if target.direction == Direction.UP:
                    self.mouse_ui.write(e.EV_REL, e.REL_Y, -target.pixel)
                elif target.direction == Direction.DOWN:
                    self.mouse_ui.write(e.EV_REL, e.REL_Y, target.pixel)
                elif target.direction == Direction.LEFT:
                    self.mouse_ui.write(e.EV_REL, e.REL_X, -target.pixel)
                elif target.direction == Direction.RIGHT:
                    self.mouse_ui.write(e.EV_REL, e.REL_X, target.pixel)
                self.mouse_ui.syn()
            elif isinstance(target, ScrollDirectionTarget):
                if target.direction == Direction.UP:
                    self.mouse_ui.write(e.EV_REL, e.REL_WHEEL_HI_RES, target.speed)
                elif target.direction == Direction.DOWN:
                    self.mouse_ui.write(e.EV_REL, e.REL_WHEEL_HI_RES, -target.speed)
                elif target.direction == Direction.LEFT:
                    self.mouse_ui.write(e.EV_REL, e.REL_HWHEEL_HI_RES, -target.speed)
                elif target.direction == Direction.RIGHT:
                    self.mouse_ui.write(e.EV_REL, e.REL_HWHEEL_HI_RES, target.speed)
                self.mouse_ui.syn()

        elif analog_input is not None:
            target = self.controller_config.mapper.translate(analog_input)
            if target == MouseTarget.CURSOR:
                self.cursor_thread.push(event)
            elif target == MouseTarget.SCROLL:
                self.scroll_thread.push(event)

    def run(self):
        logger.info(
            "Start capturing device: %s, %s",
            self.inputDevice.path,
            self.inputDevice.name,
        )
        try:
            for event in self.inputDevice.read_loop():
                self.push(event)
        except:  # noqa: E722
            logger.info(
                "Stop capturing device: %s, %s",
                self.inputDevice.path,
                self.inputDevice.name,
            )

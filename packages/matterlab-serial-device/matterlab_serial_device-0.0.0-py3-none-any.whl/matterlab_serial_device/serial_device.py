import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from logging import Logger, getLogger

import serial
from serial import Serial

SERIAL_PARITY: Dict = {"none":  serial.PARITY_NONE,
                       "odd":   serial.PARITY_ODD,
                       "even":  serial.PARITY_EVEN,
                       "mark":  serial.PARITY_MARK,
                       "space": serial.PARITY_SPACE
                       }

SERIAL_BYTESIZE: Dict = {5: serial.FIVEBITS,
                         6: serial.SIXBITS,
                         7: serial.SEVENBITS,
                         8: serial.EIGHTBITS
                         }

SERIAL_STOPBITS: Dict = {1:   serial.STOPBITS_ONE,
                         1.5: serial.STOPBITS_ONE_POINT_FIVE,
                         2:   serial.STOPBITS_TWO
                         }

SERIAL_FACTORY: Dict = {"parity":   SERIAL_PARITY,
                        "bytesize": SERIAL_BYTESIZE,
                        "stopbits": SERIAL_STOPBITS
                        }


def open_close(func):
    """
    decorator
    close communication first in case it is open (otherwise will raise error port is already open)
    open communication before sending/receiving commands
    then close in case of failure of communication
    :param func:
    :return:
    """

    def wrapper(self, *args, **kwargs):
        self.close_device_comm()  # This is done to avoid opening a port that is already open
        self.open_device_comm()
        func_return = func(self, *args, **kwargs)
        self.close_device_comm()
        return func_return

    return wrapper


class SerialDeviceSettings:
    special_keys: Tuple = ("parity", "bytesize", "stopbits",)

    def __init__(self, default_settings: Path, **kwargs) -> None:
        """
        read settings of SerialDevice
        :param default_settings: path of default settings of this device
        :param kwargs: device-specific setting, e.g. com_port, address
        """
        with default_settings.open("r") as f:
            self._defaults: Dict = json.load(f)

        settings = {**kwargs}

        if "com_port" not in settings:
            settings: Dict = self._get_com_port(settings)

        if ("RS485" in settings) and (settings["RS485"] is True) and ("address" not in settings):
            settings: Dict = self._get_address(settings)

        self._set_attrs({**self._defaults, **settings})

    def _set_attrs(self, attributes: Dict) -> None:
        """
        read settings of the device
        :param attributes:
        :return:
        """
        for key, value in attributes.items():
            self.__setattr__(key, value)

        for sp_key in self.special_keys:
            if sp_key in attributes:
                if attributes[sp_key] not in SERIAL_FACTORY[sp_key]:
                    raise ValueError(f"Invalid value for {sp_key}: {attributes[sp_key]}")
                else:
                    self.__setattr__(sp_key, SERIAL_FACTORY[sp_key][attributes[sp_key]])

    @staticmethod
    def _get_com_port(settings: Dict) -> Dict:
        """
        manual input of the COM port of the device
        other settings use default
        :return:
        """
        settings["com_port"]: str = input('Enter the appropriate communications port\
                (e.g., COM1 for windows, or /dev/ttyS0 or /dev/ttySUSB0 for Linux):\n')
        return settings

    @staticmethod
    def _get_address(settings: Dict) -> Dict:
        """
        manual input of the RS485 port of the device
        other settings use default
        :param settings:
        :return:
        """
        address: str = input('Enter the appropriate RS485 address:\n')
        if not address.isdigit():
            raise TypeError("Address must be an integer.")
        if int(address) <= 0 or int(address) > 255:
            raise ValueError("Address must be between 1 and 255.")

        settings["address"]: int = int(address)
        return settings


class SerialDevice:
    default_eol: bytes = b"\r\n"

    def __init__(
            self,
            default_settings: Path,
            settings: Dict = None,
            logger: Optional[Logger] = None,
    ) -> None:
        self.settings: SerialDeviceSettings = SerialDeviceSettings(default_settings, settings)
        self._init_device()
        self.logger = logger if logger is not None else getLogger()
        self.logger.debug(f"Created SerialDevice with settings: {self.settings.__dict__}")

    def _init_device(self):
        """
        add a device according to the device_setting
        :return: None
        """
        self.device = Serial(port=self.settings.com_port,
                             baudrate=self.settings.baudrate,
                             parity=self.settings.parity,
                             bytesize=self.settings.bytesize,
                             timeout=self.settings.timeout,
                             stopbits=self.settings.stopbits,
                             )
        self.close_device_comm()

    def open_device_comm(self):
        """
        close communication with the device to free the port
        open communication with the device
        DO NOT start the device electronically!
        :return:
        """
        self.device.close()
        self.device.open()

    def close_device_comm(self):
        """
        close communication with the device
        DO NOT shut down the device electronically!
        :return:
        """
        self.device.close()

    @staticmethod
    def _encode(command: Union[str, bytes, bytearray]) -> bytes:
        """
        encode the command to bytes
        :param command:
        :return bytes:
        """
        if isinstance(command, str):
            command: bytes = command.encode()
        elif isinstance(command, bytearray):
            command: bytes = bytes(command)
        elif isinstance(command, bytes):
            pass
        else:
            raise TypeError("'command' type must be either  str, bytes, or bytearray.")
        return command

    def write(self, command: Union[str, bytes, bytearray]) -> None:
        """
        write the command in bytes to the device
        :param command: command to write
        :return:
        """
        command_bytes: bytes = self._encode(command)
        self.device.write(command_bytes)

    def read(self, return_bytes: bool = False, **kwargs) -> Union[str, bytes]:
        """
        read the response from the device until EOL (b'\r\n')
        :return: decoded string, not including the EOL
        """
        response: bytes = self.read_bytes(**kwargs)
        if return_bytes:
            return response
        else:
            return response.decode(self.settings.encoding)

    def read_bytes(self,
                   read_until: Optional[Union[str, bytes]] = None,
                   num_bytes: int = None,
                   remove_from_start: int = 0,
                   remove_from_end: Optional[int] = None
                   ) -> bytes:
        """
        read the response from the device until EOL (b'\r\n')
        num_bytes: max number of bytes
        :return: decoded string, not including the EOL
        """
        read_until: Union[str, bytes] = read_until if read_until else self.default_eol
        command_bytes: bytes = self._encode(read_until)
        full_response: bytes = self.device.read_until(expected=command_bytes, size=num_bytes)
        if not remove_from_end:
            return full_response[remove_from_start:]
        else:
            return full_response[remove_from_start:-remove_from_end]
            
    def query(self,
              write_command: Union[str, bytes, bytearray],
              read_delay: float = 0.5,
              **kwargs
              ) -> str:
        """
        Send command to the device, wait for read_delay seconds, then read the response.
        :param write_command:
        :param read_delay:
        :return:
        """
        self.write(write_command)
        time.sleep(read_delay)
        return self.read(**kwargs)

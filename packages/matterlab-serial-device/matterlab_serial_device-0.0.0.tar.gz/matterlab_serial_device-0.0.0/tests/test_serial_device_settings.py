import serial
import pytest

from pathlib import Path

from matterlab_serial_device import SerialDeviceSettings

defaults_path = Path(__file__).parent.parent / "data" / "default_settings.json"


def test_device_settings_init():
    settings = SerialDeviceSettings(defaults_path, {"com_port": "COM1"})
    assert settings.com_port == "COM1"
    assert settings.baudrate == 19200
    assert settings.parity == serial.PARITY_ODD
    assert settings.bytesize == 7
    assert settings.timeout == 1


def test_get_com_port(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "COM123")
    settings = SerialDeviceSettings(defaults_path)
    assert settings.com_port == "COM123"


def test_get_rs485_address(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "123")
    settings = SerialDeviceSettings(defaults_path, {"com_port": "COM1", "RS485": True})
    assert settings.address == 123

    for address, error in zip(["one", "0", "256"], [TypeError, ValueError, ValueError]):
        with pytest.raises(error):
            monkeypatch.setattr("builtins.input", lambda _: address)
            settings = SerialDeviceSettings(defaults_path, {"com_port": "COM1", "RS485": True})

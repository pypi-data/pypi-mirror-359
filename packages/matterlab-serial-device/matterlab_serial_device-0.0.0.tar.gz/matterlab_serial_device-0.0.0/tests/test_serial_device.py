import pytest
from pathlib import Path

from matterlab_serial_device import SerialDevice

defaults_path = Path(__file__).parent.parent / "data" / "default_settings.json"


@pytest.fixture
def serial_device(mocker):
    # Create a SerialDevice instance for testing
    settings = {"com_port": "COM1"}
    mocker.patch("serial.Serial")
    return SerialDevice(defaults_path, settings)


def test_init_device(serial_device, mocker):
    mock_serial = mocker.patch("serial.Serial")
    device = serial_device()
    mock_serial.assert_called_once_with(
        port=serial_device.settings.com_port,
        baudrate=serial_device.settings.baudrate,
        parity=serial_device.settings.parity,
        bytesize=serial_device.settings.bytesize,
        timeout=serial_device.settings.timeout,
        stopbits=serial_device.settings.stopbits,
    )
    mock_serial.return_value.close_device_comm.assert_called_once()


def test_open_and_close_device_comm(serial_device, mocker):
    mock_serial = mocker.patch("serial.Serial")
    serial_device.open_device_comm()
    mock_serial.return_value.close.assert_called_once()
    mock_serial.return_value.open.assert_called_once()

    serial_device.close_device_comm()
    mock_serial.return_value.close.assert_called_once()


def test_encode(serial_device):
    command_str = "test"
    command_bytes = b"test"
    result_str = serial_device._encode(command_str)
    result_bytes = serial_device._encode(command_bytes)

    assert result_str == command_bytes
    assert result_bytes == command_bytes


def test_write(serial_device, mocker):
    command = "test command"
    command_bytes = b"test command"
    mock_write = mocker.patch.object(serial_device.device, "write")
    serial_device.write(command)

    mock_write.assert_called_once_with(command_bytes)


def test_read(serial_device, mocker):
    response_bytes = b"test response"
    mock_read_bytes = mocker.patch.object(serial_device, "read_bytes", return_value=response_bytes)
    result = serial_device.read()

    assert result == response_bytes.decode(serial_device.settings.encoding)
    mock_read_bytes.assert_called_once_with()


def test_read_bytes(serial_device, mocker):
    response_bytes = b"test response"
    mock_read_until = mocker.patch.object(serial_device.device, "read_until", return_value=response_bytes)
    result = serial_device.read_bytes()

    assert result == response_bytes
    mock_read_until.assert_called_once_with(expected=serial_device.default_eol, size=None)


def test_query(serial_device, mocker):
    write_command = "test command"
    read_delay = 0.5
    response = "test response"
    mock_write = mocker.patch.object(serial_device, "write")
    mock_read = mocker.patch.object(serial_device, "read", return_value=response)
    result = serial_device.query(write_command, read_delay)

    assert result == response
    mock_write.assert_called_once_with(write_command)
    mock_read.assert_called_once_with()

# import time

# from harp import MessageType, PayloadType
# from harp.messages import HarpMessage, ReplyHarpMessage
# DEFAULT_ADDRESS = 42
# # FIXME
# def test_create_device() -> None:
#     # open serial connection and load info
#     with Device("/dev/ttyUSB0") as device:
#         device.info()
from unittest.mock import MagicMock, patch

from harp.device import Device


def test_create_device_mocked():
    with patch("harp.device.serial.Serial") as mock_serial:
        # Setup the mock serial instance
        mock_instance = MagicMock()
        mock_serial.return_value = mock_instance
        mock_instance.is_open = True

        # Now Device will use the mocked serial port
        with Device("/dev/ttyUSB0") as device:
            # device.info()
            # You can add assertions here to check interactions with the mock
            mock_serial.assert_called_with("/dev/ttyUSB0", baudrate=1000000, timeout=1)
            assert mock_instance.is_open


# def test_read_U8() -> None:
#     # open serial connection and load info
#     device = Device("/dev/ttyUSB0", "dump.bin")

#     # read register 38
#     register: int = 38
#     read_size: int = 35  # TODO: automatically calculate this!

#     reply: ReplyHarpMessage = device.send(
#         HarpMessage.create(MessageType.READ, register, PayloadType.U8)
#     )
#     assert reply is not None
#     # assert reply.payload == write_value

#     print(reply)
#     assert device._dump_file_path.exists()
#     device.disconnect()

# # FIXME: this seems to be testing the Behavior device, not a generic harp device.
# def test_U8() -> None:
#     # open serial connection and load info
#     device = Device("/dev/ttyUSB0", "dump.bin")
#     assert device._dump_file_path.exists()

#     register: int = 38
#     read_size: int = 20  # TODO: automatically calculate this!
#     write_value: int = 65

#     # assert reply[11] == 0  # what is the default register value?!

#     # write 65 on register 38
#     reply = device.send(
#         HarpMessage.create(
#             MessageType.WRITE, register, PayloadType.U8, write_value
#         )
#     )
#     assert reply is not None

#     # read register 38
#     reply = device.read_u8(register)
#     assert reply is not None
#     assert reply.payload == write_value

#     device.disconnect()


# # def test_read_hw_version_integration() -> None:
# #
# #     # serial settings
# #     ser = serial.Serial(
# #         "/dev/tty.usbserial-A106C8O9",
# #         baudrate=1000000,
# #         timeout=5,
# #         parity=serial.PARITY_NONE,
# #         stopbits=1,
# #         bytesize=8,
# #         rtscts=True,
# #     )
# #
# #     assert ser.is_open
# #
# #     ser.write(b"\x01\x04\x01\xff\x01\x06")  # read HW major version (register 1)
# #     ser.write(b"\x01\x04\x02\xff\x01\x07")  # read HW minor version (register 2)
# #     # print(f"In waiting: <{ser.in_waiting}>")
# #
# #     data = ser.read(100)
# #     print(f"Data: {data}")
# #     ser.close()
# #     assert not ser.is_open
# #
# #     # assert data[0] == '\t'


# # FIXME
# # def test_device_events(device: Device) -> None:
# #     while True:
# #         print(device.event_count())
# #         for msg in device.get_events():
# #             print(msg)
# #         time.sleep(0.3)

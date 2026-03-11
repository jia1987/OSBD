import serial
import binascii
import threading
import struct
from typing import List

from core._serial import Serial
from typing import overload


class VSamplerSerial(Serial):
    TX_ANGLE = bytes.fromhex('01 03 00 00 00 01 84 0A')
    RX_ANGLE = 7
    TX_VELOCITY = bytes.fromhex('01 03 00 03 00 01 74 0A')
    RX_VELOCITY = 7
    TX_SINGLE_CYCLE_RESOLUTION = bytes.fromhex('01 03 00 88 00 01 84 0A')
    RX_SINGLE_CYCLE_RESOLUTION = 7

    def __init__(self, *args, **kwargs):
        self._frequency = 0
        self._single_cycle_resolution = None
        super(VSamplerSerial, self).__init__(*args, **kwargs)

        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._rw_lock = threading.Lock()
        self._close_lock = threading.Lock()

    def setSerial(self, serial: serial.Serial) -> None:
        super(VSamplerSerial, self).setSerial(serial=serial)
        self._thread.start()

    def close(self):
        """ 关闭, 防止线程冲突"""
        with self._close_lock:
            r = super(VSamplerSerial, self).close()
        return r

    def _monitor(self):
        while self.isOpen():
            with self._close_lock:
                if not self.isOpen(): break
                hex_list = self._write_and_read(tx=self.TX_VELOCITY, rx=self.RX_VELOCITY)
                # Rx:01 03 02 02 7A (D8 C6)
                # 校验位已删除
                hex_list = hex_list[-4:-2]
                self._frequency = self.hex2int(string=''.join(hex_list), bin=16, signed=True)

    def _write_and_read(self, tx: bytes, rx: int) -> List[str]:
        with self._rw_lock:
            self._serial.write(tx)
            data = self._serial.read(rx)
            self._serial.flushInput()

        hex_list = [format(byte, '02X') for byte in data]
        return hex_list

    def frequency(self) -> int:
        return self._frequency



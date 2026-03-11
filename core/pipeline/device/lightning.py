import time, json

from dataclasses import dataclass
import serial
import threading
from ..._serial import Serial
from ..error import LightningSerialConnectError

@dataclass
class LightningOutput():
    fault: bool = False
    distance: float = 0.0

    @classmethod
    def dumps(cls, string: str):
        cfg = json.loads(string)
        return cls(
            fault=bool(cfg['fault']),
        )


class LightningSerial(Serial):
    def __init__(self, *args, **kwargs):
        super(LightningSerial, self).__init__(*args, **kwargs)

        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._close_lock = threading.Lock()
        # 读取缓存
        self._cache: LightningOutput = LightningOutput()
        self._is_contiune = False

    def setSerial(self, serial: serial.Serial) -> None:
        super(LightningSerial, self).setSerial(serial=serial)
        # 检测是否是用于放电检测的串口
        serial.write('enable(False)\n'.encode())# 用于停止终端发送消息
        time.sleep(0.1)
        serial.reset_input_buffer()
        serial.write('machine()\n'.encode())
        time.sleep(0.1)
        result = serial.readline().decode()
        if result.startswith('Lightning-Moniter'):
            # 测试通过
            pass
        else:
            raise LightningSerialConnectError("该串口不能用于放电检测")
        serial.write('enable(True)\n'.encode())  # 通过测试开始监控
        self._thread.start() # 启动监控, 循环读取放电检测消息

    def close(self):
        """ 关闭, 防止线程冲突 """
        self._is_contiune = False
        self._serial.write('emptyOutput()\n'.encode())  # 用于停止终端发送消息
        time.sleep(0.1)
        r = super(LightningSerial, self).close()
        return r

    def _monitor(self):

        self._is_contiune = True
        # 之前的检测结果缓存与缓冲
        time.sleep(0.5)
        if self.isOpen():
            self._serial.reset_input_buffer()
        while self._is_contiune:
            if self.isOpen():
                with self._close_lock:
                    string = self._serial.readline().decode()
            else:
                continue
            self._cache = LightningOutput.dumps(string)

    def read(self) -> LightningOutput:
        return self._cache

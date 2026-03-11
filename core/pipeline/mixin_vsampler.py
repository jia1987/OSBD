import threading
import time

from .device import VSamplerSerial
from ..config import config


class VSamplerMixin():
    def __init__(self):
        self._vsampler = None
        self._location_timer = threading.Thread(target=self._locationThread)
        self._location_timer.daemon = True

        # 计米轮累加
        self._accumulated_distance = 0
        self._v_last_timestep = None
        self._is_vsampler_enabled = False

    def setVSamplerEnabled(self, enabled: bool) -> None:

        if enabled:
            baudrate = int(config.get(config.VSampler_Baudrate))
            port = str(config.get(config.VSampler_Port))
            print(f"[System] Connect VSampler(Baudrate:{baudrate}, Port:{port})...")
            self._vsampler: VSamplerSerial = VSamplerSerial.open(baudrate=baudrate, port=port)
        else:
            print(f"[System] Disconnect VSampler...")
            self._vsampler.close()
            self._vsampler = None

        self._is_vsampler_enabled = enabled

    def _locationThread(self):
        while True:
            st = time.time()
            if self._v_last_timestep is None:
                self._v_last_timestep = time.time()
            else:
                v_now_time = time.time()
                # 读取位置
                v = self.velocity()  # 速度 m/s
                timestep = v_now_time - self._v_last_timestep
                self._accumulated_distance += v * timestep
                # cache
                self._v_last_timestep = v_now_time
            # 30FPS
            if (sleep_time := time.time() - st) < 1 / 30:
                time.sleep(sleep_time)

    def velocity(self) -> float:
        ''' 速度: m/min '''
        return self.angularVelocity() * config.get(config.VSampler_Perimeter)

    def angularVelocity(self) -> float:
        ''' 速度: 转/s '''
        if self._vsampler is None:
            return 0.0
        # 编码器旋转速度 = 编码器角速度值 / 单圈分辨率 / 转速计算时间（单位：转 / 分钟）
        # 采样时间 100ms
        av = self._vsampler.frequency() / 32678 / 0.1 * 60
        # conver 单位: 转 / 秒
        av = av / 60
        return av * (-1 if config.get(config.VSampler_Direction) else 1)

    def accumulatedDistance(self) -> float:
        """ 检测的累计距离 """
        return self._accumulated_distance

    def isVSamplerEnabled(self):
        """ 计米轮使能 """
        return self._is_vsampler_enabled

from .const import Path
from .utils.config import QConfig,ConfigItem


class Config(QConfig):
    # 计米轮
    VSampler_Baudrate = ConfigItem("VSampler", "Baudrate", 115200)
    VSampler_Port = ConfigItem("VSampler", "Port", "COM3")
    VSampler_Perimeter = ConfigItem("VSampler", "Perimeter", 0.2)  # 计米轮周长, unit: m (200mm)
    VSampler_Direction = ConfigItem("VSampler", "Direction", False)
    # 放电检测
    Lightning_Baudrate = ConfigItem("Lightning", "Baudrate", 115200)
    Lightning_Port = ConfigItem("Lightning", "Port", "COM4")
    # 光源
    LightSource_Baudrate = ConfigItem("LightSource", "Baudrate", 19200)
    LightSource_Port = ConfigItem("LightSource", "Port", "COM5")
    LightSource_Level = ConfigItem("LightSource", "Level", 128)
    # IO 卡
    # 声光报警占用的物理输出通道. WENYU_EIO16P 只有 8 路输出 (ch0~ch7),
    # ch0~ch3 为光源频闪, 报警默认使用 ch4, 可按实际接线调整
    IOCard_WarningChannel = ConfigItem("IOCard", "WarningChannel", 4)
    # 相机
    Camera_ReadModes = ConfigItem("Camera", "ReadMode", [None, None, None, None])
    Camera_Videos = ConfigItem("Camera", "Video", [None, None, None, None])
    Camera_Imgs = ConfigItem("Camera", "Img", [None, None, None, None])
    Camera_Prots = ConfigItem("Camera", "Prots", [None, None, None, None])
    Camera_Captures = ConfigItem("Camera", "Capture", [0, 0, 0, 0])
    Camera_Exposures = ConfigItem("Camera", "Exposures", [2000, 2000, 2000, 2000])


config = Config()
config.load(file=Path.CONFIG)

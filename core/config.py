from .const import Path
from .utils.config import QConfig,ConfigItem


class Config(QConfig):
    # 计米轮
    VSampler_Baudrate = ConfigItem("VSampler", "Baudrate", 115200)
    VSampler_Port = ConfigItem("VSampler", "Port", "Com17")
    VSampler_Perimeter = ConfigItem("VSampler", "Perimeter", 20)  # unit: m
    VSampler_Direction = ConfigItem("VSampler", "Direction", False)  # unit: m
    # 放电检测
    Lightning_Baudrate = ConfigItem("Lightning", "Baudrate", 115200)
    Lightning_Port = ConfigItem("Lightning", "Port", "Com17")
    # 光源
    LightSource_Baudrate = ConfigItem("LightSource", "Baudrate", 19200)
    LightSource_Port = ConfigItem("LightSource", "Port", "Com17")
    LightSource_Level = ConfigItem("LightSource", "Level", 128)
    # 相机
    Camera_ReadModes = ConfigItem("Camera", "ReadMode", [None, None, None, None])
    Camera_Videos = ConfigItem("Camera", "Video", [None, None, None, None])
    Camera_Imgs = ConfigItem("Camera", "Img", [None, None, None, None])
    Camera_Prots = ConfigItem("Camera", "Prots", [None, None, None, None])
    Camera_Captures = ConfigItem("Camera", "Capture", [0, 0, 0, 0])
    Camera_Exposures = ConfigItem("Camera", "Exposures", [4200, 4200, 4200, 4200])


config = Config()
config.load(file=Path.CONFIG)

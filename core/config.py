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
    # 相机触发模式: True=频闪(随光源触发), False=连续采集
    Camera_Triggers = ConfigItem("Camera", "Triggers", [True, True, True, True])
    # 检测算法 (默认值与历史硬编码一致)
    Detect_Conf = ConfigItem("Detect", "Conf", 0.60)          # YOLO 置信度阈值
    Detect_UseYolo = ConfigItem("Detect", "UseYolo", True)    # YOLO 开关, 环境变量 OSBD_USE_YOLO 优先
    # IO 卡报警时序 (秒)
    IOCard_WarningDuration = ConfigItem("IOCard", "WarningDuration", 3)
    IOCard_WarningInterval = ConfigItem("IOCard", "WarningInterval", 3)
    # 放电检测去抖窗口 (秒)
    Lightning_Debounce = ConfigItem("Lightning", "Debounce", 0.3)
    # 光源四路亮度 (0~255)
    LightSource_Levels = ConfigItem("LightSource", "Levels", [128, 128, 128, 128])
    # 图像预处理 (CLAHE / ROI)
    Prepare_ClipLimit = ConfigItem("Prepare", "ClipLimit", 3.0)
    Prepare_Grid = ConfigItem("Prepare", "Grid", 8)
    Prepare_RoiRatio = ConfigItem("Prepare", "RoiRatio", 1 / 3)
    # 界面
    Session_RememberUser = ConfigItem("Session", "RememberUser", "")
    UI_AlarmPopup = ConfigItem("UI", "AlarmPopup", False)


config = Config()
config.load(file=Path.CONFIG)

""" 实时检测页 (设计稿 P3): 顶部信息条 + 2×2 图像 + 底部泳道 | 右侧设备控制+统计+列表 """
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from .top_infobar import TopInfoBar
from .camera_grid import CameraGrid
from .bottom_lanes import BottomLanes
from .device_control import DeviceControlCard
from .realtime_panel import RealtimePanel


class DetectionInterface(QWidget):
    def __init__(self, parent=None):
        super(DetectionInterface, self).__init__(parent)

        self.initWidget()
        self.initLayout()

    def initWidget(self):
        self.topBar = TopInfoBar(self)
        self.cameraGrid = CameraGrid(self)
        self.bottomLanes = BottomLanes(self)
        self.deviceControl = DeviceControlCard(self)
        self.realtimePanel = RealtimePanel(self)

        # 列表单击 → 通道图像高亮定位
        self.realtimePanel.locate.connect(self.cameraGrid.flash)

    def initLayout(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(12)

        outer.addWidget(self.topBar)

        body = QHBoxLayout()
        body.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(self.cameraGrid, 1)
        left.addWidget(self.bottomLanes)

        right = QVBoxLayout()
        right.setSpacing(12)
        right.addWidget(self.deviceControl)
        right.addWidget(self.realtimePanel, 1)

        body.addLayout(left, 7)
        body.addLayout(right, 3)
        outer.addLayout(body, 1)

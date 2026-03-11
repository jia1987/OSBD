from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSpinBox, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QWidget, QStackedWidget

from core import config
from core.pipeline.device.camera import Camera
from ...companent import Label, ComboBox, FileLoadBox,SpinBox



class ModeComboBox(ComboBox):
    modes = ["海康威视", "摄像头", "视频", "图片"]

    def __init__(self, parent=None):
        super(ModeComboBox, self).__init__(parent=parent)
        self.setItems(items=self.modes)

    def readMode(self) -> str:
        return [Camera.ReadMode_Hk, Camera.ReadMode_Capture, Camera.ReadMode_Vedio, Camera.ReadMode_Img][
            self.currentIndex()]

    def indexOf(self, mode):
        if mode not in (Camera.ReadMode_Hk, Camera.ReadMode_Capture, Camera.ReadMode_Vedio, Camera.ReadMode_Img):
            return 0
        return [Camera.ReadMode_Hk, Camera.ReadMode_Capture, Camera.ReadMode_Vedio, Camera.ReadMode_Img].index(mode)


class PortComboBox(ComboBox):
    def showPopup(self):
        """ 动态加载Items """
        # 获取接入的所有串口信息，插入combobox的选项中
        posts = Camera.HK_deivces()
        self.setItems(['None'] + posts)
        super(PortComboBox, self).showPopup()  # 弹出选项框


class SingleCameraSettingWidget(QWidget):
    @classmethod
    def set(cls, item, ctx, value):
        _item = config.get(item)
        _item[ctx] = value
        config.set(item, _item.copy())
        config.save()

    @classmethod
    def get(cls, item, ctx):
        return config.get(item)[ctx]

    def __init__(self, ctx: int, parent=None):
        self._ctx = ctx
        super().__init__(parent)
        self.initWidget()
        self.initLayout()
        self.initData()
        self.initConnect()

    def initWidget(self):
        self.mode_combox = ModeComboBox(self)
        self.prot_combox = PortComboBox(self)
        self.exposure_spinbox = SpinBox(self)
        self.exposure_spinbox.setRange(0, 2 ** 16)
        self.capture_spinbox = SpinBox(self)
        self.capture_spinbox.setRange(0, 16)
        self.imageBox = FileLoadBox(parent=self, title='选择图片', filter='Images (*.png *.jpg *.jpeg)')
        self.videoBox = FileLoadBox(self, title='选择视频', filter='Video Files (*.mp4 *.avi *.mov *.mkv)')

        self.stackedWidget = QStackedWidget(self)
        self._w1 = QWidget(self)
        self._w2 = QWidget(self)
        self._w3 = QWidget(self)
        self._w4 = QWidget(self)

    def initConnect(self):
        ctx = self._ctx
        self.prot_combox.currentTextChanged.connect(lambda v: self.set(config.Camera_Prots, ctx=ctx, value=v))
        self.exposure_spinbox.valueChanged.connect(lambda v: self.set(config.Camera_Exposures, ctx=ctx, value=v))
        self.mode_combox.currentIndexChanged.connect(lambda index: self.stackedWidget.setCurrentIndex(index))
        self.mode_combox.currentIndexChanged.connect(lambda v: self.set(config.Camera_ReadModes, ctx=ctx,
                                                                        value=self.mode_combox.readMode()))
        self.imageBox.pathChanged.connect(lambda v: self.set(config.Camera_Imgs, ctx=ctx, value=v))
        self.videoBox.pathChanged.connect(lambda v: self.set(config.Camera_Videos, ctx=ctx, value=v))

    def initData(self):
        ctx = self._ctx
        if (port := self.get(config.Camera_Prots, ctx=ctx)) is not None:
            self.prot_combox.setCurrentText(port)
            self.prot_combox.addItem(port)
        if (img := self.get(config.Camera_Imgs, ctx=ctx)) is not None:
            self.imageBox.setPath(img)
        if (video := self.get(config.Camera_Videos, ctx=ctx)) is not None:
            self.videoBox.setPath(video)
        # exposure
        self.exposure_spinbox.setValue(self.get(config.Camera_Exposures, ctx=ctx))
        # capture check
        self.capture_spinbox.setValue(self.get(config.Camera_Captures, ctx=ctx))
        # read mode
        self.mode_combox.setCurrentIndex(self.mode_combox.indexOf(self.get(config.Camera_ReadModes, ctx=ctx)))
        # go to widget
        self.stackedWidget.setCurrentIndex(self.mode_combox.currentIndex())

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.gridLayout = QGridLayout()
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.viewLayout.addLayout(self.gridLayout)

        for i, (name, item) in enumerate([('读取模式', self.mode_combox), ]):
            self.gridLayout.addWidget(Label(self.tr(name), 16), i, 0, alignment=Qt.AlignRight)
            self.gridLayout.addWidget(item, i, 1, )

        for w, items in [
            (self._w1, (('HK端口', self.prot_combox), ('曝光时间', self.exposure_spinbox))),
            (self._w2, (('摄像头', self.capture_spinbox),)),
            (self._w3, (('视频路径', self.videoBox),)),
            (self._w4, (("图片路径", self.imageBox),))
        ]:
            self.stackedWidget.addWidget(w)
            layout = QGridLayout(w)
            layout.setContentsMargins(0, 0, 0, 0)
            for i, (name, item) in enumerate(items):
                layout.addWidget(Label(self.tr(name), 16), i, 0, alignment=Qt.AlignRight)
                layout.addWidget(item, i, 1, )
            layout.setColumnStretch(0, 0)
            layout.setColumnStretch(1, 1)

        self.viewLayout.addWidget(self.stackedWidget)
        self.gridLayout.setColumnStretch(0, 0)
        self.gridLayout.setColumnStretch(1, 1)
        self.viewLayout.setStretch(0, 0)
        self.viewLayout.setStretch(1, 1)
        self.viewLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))


class CameraSettingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initWidget()
        self.initLayout()
        self.initData()
        self.initConnect()

    def initWidget(self):
        self.titleLabel = Label(text=self.tr('摄像头'), weight=QFont.Bold, fontSize=32, parent=self, )
        self.camera_1 = SingleCameraSettingWidget(ctx=0, parent=self)
        self.camera_2 = SingleCameraSettingWidget(ctx=1, parent=self)
        self.camera_3 = SingleCameraSettingWidget(ctx=2, parent=self)
        self.camera_4 = SingleCameraSettingWidget(ctx=3, parent=self)

    def initConnect(self):
        pass

    def initData(self):
        pass

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout = QVBoxLayout()

        self.viewLayout.addWidget(self.titleLabel)
        for idx, (title, w) in enumerate(
                [('摄像头-1', self.camera_1),
                 ('摄像头-2', self.camera_2),
                 ('摄像头-3', self.camera_3),
                 ('摄像头-4', self.camera_4)]):
            self.vlayout.addWidget(Label(text=self.tr(title), fontSize=24, parent=self, ))
            self.vlayout.addWidget(w)
            self.vlayout.setStretch(1 + idx * 2, 0)
            self.vlayout.setStretch(2 + idx * 2, 1)
        self.viewLayout.addLayout(self.vlayout)
        self.viewLayout.setStretch(0, 0)

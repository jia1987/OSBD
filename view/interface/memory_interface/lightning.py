import json
import os
from urllib.response import addinfo

from PyQt5.QtCore import QTimer, QStandardPaths, QStringListModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QListView, QGridLayout
from PyQt5.QtWidgets import QApplication, QMainWindow, QListView

from ...companent import Label, Pivot, LightnInterface, FaultOverview

from .vision import VisionDetectWidgwt
from .navigation import Navigation
from .fault_overview import BatchFaultOverview
from core.const import Path
from core.database import UserManager
from core.pipeline import faultDetectionPipeline
from core.pipeline import FaultInfo


class LightnReviewInterface(LightnInterface):
    """ review """

    def load(self, path):
        """ 加载 """
        path = os.path.join(path, 'lightning', 'fault.json')
        if not os.path.exists(path):
            self.clear()
            return

        try:
            with open(path, 'r') as f:
                info = FaultInfo.from_dict(**json.load(f))
        except json.decoder.JSONDecodeError:
            return
        except Exception as e:
            raise e

        self.setDistance(info.location)
        self.update()

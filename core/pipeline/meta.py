import json
from dataclasses import dataclass
from typing import List, Dict, Tuple

import numpy as np
from PIL import Image

from core.pipeline.fault_detection import DetectOutput
from .device.camera import Camera


class PipelineType():
    exposureBatch = ["camera1", "camera2", "camera3", "camera4"]
    CAMERAS = ["camera1", "camera2", "camera3", "camera4"]
    CAMERA_LIST = CAMERAS
    CHANNELS = ['c1', 'c2', 'c3', 'c4']

    State_DetectDisable = '检测未使能'
    State_NoBacthName = '没有批次名称'
    State_Normal = '正常'


@dataclass
class ChannelInfo():
    oringe_image: np.ndarray = None
    detect_image: np.ndarray = None
    show_image: np.ndarray = None
    faults: List[DetectOutput] = None

    def clear(self):
        self.oringe_image = None
        self.detect_image = None
        self.show_image = None
        self.faults = []

    @property
    def camera(self) -> Camera:
        raise NotImplementedError


@dataclass
class FaultInfo():
    image: np.ndarray = None
    showImage: np.ndarray = None
    faults: List[DetectOutput] = None
    location: float = None
    batchName: str = None
    camera: str = None
    worker: str = None

    @classmethod
    def from_dict(cls, **kwargs):
        faults = kwargs.pop('faults')
        kwargs['faults'] = [DetectOutput(**f) for f in faults]
        return cls(**kwargs)

    def to_dict(self):
        return {
            'faults': [f.to_dict() for f in self.faults],
            'location': self.location,
            'worker': self.worker,
        }

    def saveImage(self, path):
        if len(self.image.shape) == 2:
            image = Image.fromarray(self.image, mode='L')
        else:
            image = Image.fromarray(self.image[:, :, ::-1], mode='RGB')
        image.save(path)


@dataclass
class ModelConfig(object):
    """ 不同漆包线型号的单独配置 """
    rectification: Dict[str, Tuple[int, int, int, int]]
    mapper: Dict[str, int]
    enable: Dict[str, bool]
    exposureBatch: Dict[str, int]

    @classmethod
    def from_dict(cls, _dict):
        return cls(
            rectification=_dict.get('rectification', {PipelineType.CHANNELS[0]: (0, 1, 0, 1),
                                                      PipelineType.CHANNELS[1]: (0, 1, 0, 1),
                                                      PipelineType.CHANNELS[2]: (0, 1, 0, 1),
                                                      PipelineType.CHANNELS[3]: (0, 1, 0, 1)}),
            mapper=_dict.get('mapper', {c1: c2 for c1, c2 in zip(PipelineType.CHANNELS, PipelineType.CAMERA_LIST)}),
            enable=_dict.get('enable', {PipelineType.CHANNELS[0]: True,
                                        PipelineType.CHANNELS[1]: True,
                                        PipelineType.CHANNELS[2]: True,
                                        PipelineType.CHANNELS[3]: True}),
            exposureBatch=_dict.get('exposureBatch', {PipelineType.CAMERA_LIST[0]: 0,
                                                      PipelineType.CAMERA_LIST[1]: 0,
                                                      PipelineType.CAMERA_LIST[2]: 0,
                                                      PipelineType.CAMERA_LIST[3]: 0}),
        )

    @classmethod
    def load(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return cls.from_dict(json_data)

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    def to_dict(self):
        return {
            'rectification': self.rectification,
            'mapper': self.mapper,
            'enable': self.enable,
            "exposureBatch": self.exposureBatch
        }

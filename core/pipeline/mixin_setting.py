from typing import Callable
import os
from .meta import PipelineType, ModelConfig


class SettingMixin(PipelineType):
    LightningOutput = None

    _batch_name = None  # 批次名称
    _worker_name = None  # 批次的负责人
    _detect_enable = False  # 检测使能
    _pipeline_state = ''

    # 型号配置
    _modelConfig = None

    def setCallback(self, callback):
        """" setter """
        assert callable(callback)
        self._callback = callback

    def setState(self, state: str):
        """" setter """
        # 描述pipeline的状态
        self._pipeline_state = state

    def setModelConfig(self, modelConfig: 'ModelConfig' or str):
        """" setter """
        if isinstance(modelConfig, str):
            modelConfig = ModelConfig.load(modelConfig)
        self._modelConfig = modelConfig

    def setDetectEnable(self, enable: bool):
        """" setter """
        self._detect_enable = enable

    def setBatchName(self, batch_name: str):
        """" setter """
        self._batch_name = batch_name

    def setWorkerName(self, worker_name: str):
        """" setter """
        self._worker_name = worker_name

    def state(self) -> str:
        return self._pipeline_state

    def isDetectEnabled(self) -> bool:
        return self._detect_enable

    def batchName(self):
        """ 批次名 """
        return self._batch_name

    def workerName(self):
        """ 批次的负责人 """
        return self._worker_name

    def callback(self) -> Callable:
        return self._callback

    def modelConfig(self) -> 'ModelConfig':
        return self._modelConfig

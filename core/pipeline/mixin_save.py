import json
import time
import threading
import os
from typing import List
from .meta import FaultInfo
from ..const import Path


class SaveMixin():
    _save_thread = None
    _save_pipe: List[FaultInfo] = []

    def save(self, fault: FaultInfo):
        assert isinstance(fault, FaultInfo), f'Expected {FaultInfo.__name__}, got {type(fault)}'
        if self._save_thread is None:
            self._save_thread = threading.Thread(target=self._saveThread)
            self._save_thread.daemon = True
            self._save_thread.start()
            self._save_pipe = []
        self._save_pipe.append(fault)

    def _saveThread(self):
        while True:
            if len(self._save_pipe) == 0:
                time.sleep(0.1)
                continue

            fault = self._save_pipe.pop(0)
            # 型号
            if fault.batchName is None or fault.batchName == '':
                continue
            save_path = os.path.join(Path.OUTPUT_DIR, fault.batchName)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 单次识别的保存路径
            save_path = os.path.join(save_path, f'{fault.location:.2f}', fault.camera)
            if os.path.exists(save_path):
                continue  # 已经保存过了
            else:
                os.makedirs(save_path)


            with open(os.path.join(save_path, f'fault.json'), 'w', encoding='utf-8') as f:
                # print(fault.to_dict())
                json.dump(fault.to_dict(), f, ensure_ascii=False, indent=4)

            fault.saveImage(os.path.join(save_path, f'image.jpg'))

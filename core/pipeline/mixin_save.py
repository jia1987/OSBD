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
        if self._save_thread is None or not self._save_thread.is_alive():
            self._save_thread = threading.Thread(target=self._saveThread)
            self._save_thread.daemon = True
            self._save_thread.start()
        self._save_pipe.append(fault)

    def _saveThread(self):
        while True:
            if len(self._save_pipe) == 0:
                time.sleep(0.1)
                continue

            fault = self._save_pipe.pop(0)
            try:
                self._saveOne(fault)
            except Exception as e:
                # 单条保存失败(磁盘满/权限等)不允许导致线程退出,
                # 否则之后所有缺陷都会静默丢失
                print(f'[System][Save] 保存缺陷数据失败: {e}')

    def _saveOne(self, fault: FaultInfo):
        # 型号
        if fault.batchName is None or fault.batchName == '':
            return
        save_path = os.path.join(Path.OUTPUT_DIR, fault.batchName)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # 单次识别的保存路径
        save_path = os.path.join(save_path, f'{fault.location:.2f}', fault.camera)
        if os.path.exists(save_path):
            return  # 已经保存过了
        else:
            os.makedirs(save_path)

        with open(os.path.join(save_path, f'fault.json'), 'w', encoding='utf-8') as f:
            # print(fault.to_dict())
            json.dump(fault.to_dict(), f, ensure_ascii=False, indent=4)

        fault.saveImage(os.path.join(save_path, f'image.jpg'))

    def waitSaveFinished(self, timeout: float = 10):
        """ 等待保存队列排空 (程序退出前调用, 避免缺陷数据丢失) """
        st = time.time()
        while len(self._save_pipe) > 0:
            if timeout is not None and time.time() - st > timeout:
                print(f'[System][Save] 等待保存队列排空超时, 剩余 {len(self._save_pipe)} 条未保存')
                break
            time.sleep(0.1)

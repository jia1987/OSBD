""" 统一的设备释放流程: 窗口关闭与登录取消共用, 顺序与历史 closeEvent 一致 """
from core import faultDetectionPipeline


def release_devices():
    """ 先释放设备并等待缺陷数据保存完成 (任何异常只打印不抛出) """
    try:
        if faultDetectionPipeline.isDetectEnabled():
            faultDetectionPipeline.setDetectEnable(False)
        if faultDetectionPipeline.isCameraEnabled():
            faultDetectionPipeline.setCameraEnabled(False)
        if faultDetectionPipeline.isLightSourceEnabled():
            faultDetectionPipeline.setLightSourceEnable(False)
        if faultDetectionPipeline.isVSamplerEnabled():
            faultDetectionPipeline.setVSamplerEnabled(False)
        if faultDetectionPipeline.isLightningEnabled():
            faultDetectionPipeline.setLightningEnabled(False)
    except Exception as e:
        print(f'[System] 退出时释放设备失败: {e}')
    try:
        # 等待保存线程排空, 避免缺陷数据丢失
        faultDetectionPipeline.waitSaveFinished(timeout=10)
    except Exception as e:
        print(f'[System] 退出时等待保存失败: {e}')

import time, pickle
import cv2, sys, os

from fault_detection import detect, DetectOutput
from fault_detection.anaylsis import FaultEnum
import numpy as np
import multiprocessing.shared_memory as shm
import argparse
from ultralytics import YOLO
import cpuinfo

info = cpuinfo.get_cpu_info()
brand = info['brand_raw']
print("CPU:", brand)
IS_INTEL = "Intel" in brand

WRITE_FINISHED_FLAG = 0
DETECT_FINISHED_FLAG = 1

IMG_SIZE = 640
height = IMG_SIZE
width = IMG_SIZE // 3
imgsz = (640, 224)
h = imgsz[0]
w = imgsz[1]

def get_args():
    parser = argparse.ArgumentParser(description="Simple example of a training script.")
    parser.add_argument(f"--img_shm_name", type=str)
    parser.add_argument(f"--op_shm_name", type=str)
    parser.add_argument(f"--out_shm_name", type=str)
    parser.add_argument(f"--width", type=int)
    parser.add_argument(f"--height", type=int)

    args = parser.parse_args()
    return args


# 是否使用 YOLO 模型推理 (可用环境变量 OSBD_USE_YOLO=0 关闭, 回退传统算法)
USE_YOLO = os.environ.get('OSBD_USE_YOLO', '1') not in ('0', 'false', 'False')
if USE_YOLO and IS_INTEL:
    import openvino as ov
def main():
    args = get_args()
    width, height = args.width, args.height
    # 连接到已存在的共享内存块
    img_shm = shm.SharedMemory(name=args.img_shm_name)
    op_shm = shm.SharedMemory(name=args.op_shm_name)
    out_shm = shm.SharedMemory(name=args.out_shm_name)
    if USE_YOLO:
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '_rc')
        if IS_INTEL:
            yolo = YOLO(os.path.join(model_path, 'yolo_openvino_model'))
        else:
            yolo = YOLO(os.path.join(model_path, 'yolo.onnx'))

    while True:
        if op_shm.buf[WRITE_FINISHED_FLAG] != 1:
            time.sleep(0.001)
            continue

        img = np.ndarray((height, width), dtype=np.uint8, buffer=img_shm.buf)

        if USE_YOLO:

            img = np.repeat(img[:, :, np.newaxis], 3, axis=-1)
            result = yolo(img,imgsz=imgsz, verbose=False,conf=0.60)
            output = []
            boxes = result[0].boxes.xywh.cpu().numpy()  # 转为numpy数组
            boxes[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
            boxes[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
            confs = result[0].boxes.conf.cpu().numpy()
            classes = result[0].boxes.cls.cpu().numpy()

            for j, (box, conf, cls) in enumerate(zip(boxes, confs, classes)):
                # print(box, conf, cls)
                output.append(DetectOutput(x=float(box[0]), y=float(box[1]), w=float(box[2]), h=float(box[3]),
                                           ftype=(FaultEnum.Bubble,
                                                  FaultEnum.Particle,
                                                  FaultEnum.Tumor,
                                                  FaultEnum.Sticky_Line)[int(cls)], ))
        else:
            output = detect(img)

        # 回传
        # 输出共享内存只有 64KiB, 结果序列化后超限时逐步裁剪, 防止写越界崩溃
        max_len = len(out_shm.buf) - 1024
        data_bytes = pickle.dumps([o.to_dict() for o in output])
        while len(data_bytes) > max_len and len(output) > 0:
            output = output[:max(0, len(output) - max(1, len(output) // 4))]
            data_bytes = pickle.dumps([o.to_dict() for o in output])
        out_shm.buf[:len(data_bytes)] = data_bytes
        # 传递数据大小
        data_length = len(data_bytes)
        # 3. 将整数转换为 bytes
        num_as_bytes = data_length.to_bytes(1024, byteorder='big')
        out_shm.buf[-1024:] = num_as_bytes

        # flag
        op_shm.buf[WRITE_FINISHED_FLAG] = 0
        op_shm.buf[DETECT_FINISHED_FLAG] = 1


if __name__ == '__main__':
    main()

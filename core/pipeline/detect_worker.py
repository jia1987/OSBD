import time, pickle
import cv2, sys,os


from fault_detection import detect
import numpy as np
import multiprocessing.shared_memory as shm
import argparse
from PIL import Image

WRITE_FINISHED_FLAG = 0
DETECT_FINISHED_FLAG = 1


def get_args():
    parser = argparse.ArgumentParser(description="Simple example of a training script.")
    parser.add_argument(f"--img_shm_name", type=str)
    parser.add_argument(f"--op_shm_name", type=str)
    parser.add_argument(f"--out_shm_name", type=str)
    parser.add_argument(f"--width", type=int)
    parser.add_argument(f"--height", type=int)

    args = parser.parse_args()
    return args


def main():
    args = get_args()
    width, height = args.width, args.height
    # 连接到已存在的共享内存块
    img_shm = shm.SharedMemory(name=args.img_shm_name)
    op_shm = shm.SharedMemory(name=args.op_shm_name)
    out_shm = shm.SharedMemory(name=args.out_shm_name)
    while True:
        if op_shm.buf[WRITE_FINISHED_FLAG] != 1:
            time.sleep(0.001)
            continue
        img = np.ndarray((height, width), dtype=np.uint8, buffer=img_shm.buf).copy()
        output = detect(img)

        # 回传
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

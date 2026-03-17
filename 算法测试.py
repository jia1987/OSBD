import os
import shutil
from core.pipeline.fault_detection import detect
from PIL import Image, ImageDraw, ImageFont
import numpy as np
def dataset():
    path = r'E:\study\My-GitHub-Project\漆包线检测\output\1'
    os.makedirs('cache\dataset', exist_ok=True)
    i = 0
    for p1, p2, p3 in os.walk(path):
        for f in p3:
            if f.endswith('.jpg'):
                p = os.path.join(p1, f)
                shutil.copy(p,
                            os.path.join('cache', 'dataset', f'{i}.jpg'),
                            )
                i = i + 1
        print(p1, p2, p3)

import cv2

def visualize_detect(image, outputs):
    img = image.copy()

    for det in outputs:
        x = int(det.x)
        y = int(det.y)
        w = int(det.w)
        h = int(det.h)

        pt1 = (x, y)
        pt2 = (x + w, y + h)

        # 画矩形框
        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 2)

        # 写类别
        label = det.ftype
        cv2.putText(
            img,
            label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    return img
if __name__ == '__main__':
    path = r'cache/dataset'
    # dataset()
    files =os.listdir(path)
    #files = ['7.jpg']
    #files = ['104.jpg']
    #image = Image.open(os.path.join(path,)'cache/dataset/115.jpg')
    #image = np.array(image)



    for file in files:
        print(file)
        image = Image.open(os.path.join(path, file))
        image = np.array(image)
        outputs = detect(image)

        vis = visualize_detect(image, outputs)

        cv2.imshow("result", vis)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()


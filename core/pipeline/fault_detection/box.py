import numpy as np


def iou(box1, box2):
    # box: [x, y, w, h]
    xi1 = max(box1[0], box2[0])
    yi1 = max(box1[1], box2[1])
    xi2 = min(box1[0] + box1[2], box2[0] + box2[2])
    yi2 = min(box1[1] + box1[3], box2[1] + box2[3])
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area


def merge_box(boxes, iou_threshold=0.5):
    while True:
        new_boxes = []
        is_break = False
        for i, box_1 in enumerate(boxes):
            for j, box_2 in enumerate(boxes[i + 1:]):
                if iou(box_1, box_2) > iou_threshold:
                    new_boxes.append(box_1)
                    is_break = True
                    break
            if is_break:
                break



def fuse_boxes(boxes, scores=None, iou_thresh=0.5):
    """
    boxes: N x 4 array
    scores: N array, optional, 用于加权融合
    """
    boxes = boxes.copy()
    scores = scores if scores is not None else np.ones(len(boxes))
    fused = []

    while len(boxes) > 0:
        # 取分数最高的 box
        idx = np.argmax(scores)
        base_box = boxes[idx]
        base_score = scores[idx]

        # 找出 IoU 大于阈值的 box
        ious = np.array([iou(base_box, b) for b in boxes])
        merge_idx = np.where(ious > iou_thresh)[0]

        # 加权平均融合
        merge_boxes = boxes[merge_idx]
        merge_scores = scores[merge_idx]
        fused_box = np.sum(merge_boxes.T * merge_scores, axis=1) / np.sum(merge_scores)
        fused.append(fused_box.tolist())

        # 删除已经融合的 box
        boxes = np.delete(boxes, merge_idx, axis=0)
        scores = np.delete(scores, merge_idx, axis=0)

    return fused


if __name__ == '__main__':
    # 示例
    boxes = np.array([[10, 10, 50, 50], [12, 12, 48, 48], [100, 100, 150, 150]])
    scores = np.array([0.9, 0.8, 0.95])
    fused = fuse_boxes(boxes, scores, iou_thresh=0.5)
    print(fused)

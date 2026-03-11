def line_by_two_points(p1, p2, x=None, y=None):
    """
    已知两点 p1, p2，求直线上第三点坐标
    输入:
        p1, p2 : (x, y)
        x      : 给定x (可选)
        y      : 给定y (可选)
    返回:
        (x, y) : 第三点坐标
    """
    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2:  # 垂直线
        if x is not None:
            return (x1, None)  # x固定，y不唯一
        elif y is not None:
            return (x1, y)
        else:
            raise ValueError("必须提供x或y")

    k = (y2 - y1) / (x2 - x1)

    if x is not None:
        y = y1 + k * (x - x1)
        return (x, y)
    elif y is not None:
        x = x1 + (y - y1) / k
        return (x, y)
    else:
        raise ValueError("必须提供x或y")




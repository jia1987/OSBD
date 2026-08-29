from PyQt5.QtGui import QColor


class Theme:
    """ 深色工业主题调色板 (与 ui_design 设计稿一致) """

    # ---- 结构色 ----
    BG = '#14161C'      # 窗口底色
    BAR = '#1B1E27'     # 顶栏/导航栏/状态栏
    CARD = '#232733'    # 卡片底色
    CARD2 = '#2A2F3D'   # 输入框/次级块
    BORDER = '#3A4152'  # 边框
    IMAGE = '#0B0D12'   # 图像区底色
    ROWALT = '#1F2330'  # 表格斑马纹

    # ---- 语义色 ----
    ACCENT = '#2E9BFF'  # 主色(品牌蓝)/选中/链接
    TEAL = '#00C2B0'    # 强调青
    GREEN = '#35C46F'   # 成功/运行/已连接
    YELLOW = '#FFB020'  # 警告/待处理
    RED = '#F5564E'     # 危险/缺陷/已断开
    ORANGE = '#FF7A2F'  # 放电类缺陷

    # ---- 文字 ----
    TXT = '#E8EAF0'     # 主文字
    TXT2 = '#8B93A7'    # 次级文字

    # ---- 兼容旧引用 ----
    GrayColor = QColor(125, 125, 125)
    PrimaryColor = QColor(23, 23, 23)

    @classmethod
    def color(cls, name: str) -> QColor:
        """ 按调色板属性名取 QColor, 如 Theme.color('ACCENT') """
        return QColor(getattr(cls, name))

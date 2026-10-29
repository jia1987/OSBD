# -*- coding: utf-8 -*-
"""
漆包线视觉检测软件 —— UI 重构设计稿生成器
运行本脚本将生成 draw.io 可直接打开的 .drawio 文件(共 7 页)。
"""
import io
import xml.sax.saxutils as xs

F = 'fontName=Microsoft YaHei;'

# ================= 调色板(深色工业主题) =================
BG      = '#14161C'   # 窗口底色
BG2     = '#1B1E27'   # 顶栏/导航栏/状态栏
CARD    = '#232733'   # 卡片底色
CARD2   = '#2A2F3D'   # 输入框/次级块
BORDER  = '#3A4152'   # 边框
ACCENT  = '#2E9BFF'   # 主色(品牌蓝)
TEAL    = '#00C2B0'   # 强调青
GREEN   = '#35C46F'   # 成功/运行
YELLOW  = '#FFB020'   # 警告
RED     = '#F5564E'   # 危险/缺陷
ORANGE  = '#FF7A2F'   # 放电缺陷
PURPLE  = '#9B7BFF'   # 辅助
TXT     = '#E8EAF0'   # 主文字
TXT2    = '#8B93A7'   # 次级文字
IMAGE   = '#0B0D12'   # 图像区底色
ROWALT  = '#1F2330'   # 表格斑马纹
NOTEBG  = '#33290F'   # 设计说明便签
NOTEF   = '#FFD479'


# ================= 基础样式 =================
def rect(fill, stroke=None, arc=6, rounded=True, dash=False, opacity=None, w=1):
    stroke = stroke if stroke is not None else 'none'
    s = (f'{F}rounded={"1" if rounded else "0"};whiteSpace=wrap;html=0;'
         f'fillColor={fill};strokeColor={stroke};arcSize={arc};')
    if dash:
        s += 'dashed=1;'
    if opacity is not None:
        s += f'opacity={opacity};'
    if w != 1:
        s += f'strokeWidth={w};'
    return s


def txt(color=TXT, size=13, align='left', valign='middle', bold=False, italic=False):
    st = (f'{F}text;html=0;whiteSpace=wrap;fillColor=none;strokeColor=none;'
          f'fontColor={color};fontSize={size};align={align};verticalAlign={valign};')
    style = 0
    if bold:
        style |= 1
    if italic:
        style |= 2
    if style:
        st += f'fontStyle={style};'
    return st


# ================= 页面容器 =================
class Page:
    def __init__(self, name, pw=2600, ph=1250):
        self.name = name
        self.pw, self.ph = pw, ph
        self.cells = []
        self.n = 1

    def id(self):
        self.n += 1
        return f'c{self.n}'

    def add(self, value, style, x, y, w, h, parent='1'):
        cid = self.id()
        self.cells.append((cid, value, style, round(x, 1), round(y, 1),
                           round(w, 1), round(h, 1), parent))
        return cid

    def xml(self, idx):
        rows = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
        for cid, value, style, x, y, w, h, parent in self.cells:
            rows.append(
                f'<mxCell id="{cid}" value="{xs.escape(value, {chr(34): "&quot;"})}" '
                f'style="{xs.escape(style, {chr(34): "&quot;"})}" vertex="1" parent="{parent}">'
                f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return (f'<diagram name="{xs.escape(self.name)}" id="p{idx}">'
                f'<mxGraphModel dx="1422" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" '
                f'connect="1" arrows="1" fold="1" page="1" pageScale="1" '
                f'pageWidth="{self.pw}" pageHeight="{self.ph}" background="#0F1115" math="0" shadow="0">'
                f'<root>' + ''.join(rows) + '</root></mxGraphModel></diagram>')


# ================= 通用组件 =================
def button(p, x, y, w, h, label, kind='primary', size=13, bold=True):
    m = {'primary': (ACCENT, 'none', '#FFFFFF'),
         'success': (GREEN, 'none', '#FFFFFF'),
         'danger': (RED, 'none', '#FFFFFF'),
         'warn': (ORANGE, 'none', '#FFFFFF'),
         'outline': (CARD2, BORDER, TXT),
         'ghost': ('#2E3444', 'none', TXT2),
         'teal': (TEAL, 'none', '#FFFFFF')}
    f, s, fc = m[kind]
    p.add(label, f'{F}rounded=1;whiteSpace=wrap;html=0;fillColor={f};strokeColor={s};'
                 f'fontColor={fc};fontSize={size};arcSize=18;'
                 + ('fontStyle=1;' if bold else ''), x, y, w, h)


def chip(p, x, y, label, state='ok', w=None):
    colors = {'ok': GREEN, 'err': RED, 'off': '#5A6274', 'warn': YELLOW, 'accent': ACCENT}
    c = colors[state]
    w = w or (36 + len(label) * 13)
    p.add('', rect('#262B38', BORDER, arc=50), x, y, w, 26)
    p.add('', f'ellipse;fillColor={c};strokeColor=none;', x + 10, y + 8, 10, 10)
    p.add(label, txt(TXT, 12, 'left'), x + 26, y, w - 32, 26)
    return w


def toggle(p, x, y, on=True, label=None, lab_color=None):
    pill = GREEN if on else '#4A5162'
    p.add('', f'{F}rounded=1;arcSize=50;whiteSpace=wrap;html=0;fillColor={pill};strokeColor=none;',
          x, y, 40, 22)
    kx = x + 21 if on else x + 3
    p.add('', 'ellipse;fillColor=#FFFFFF;strokeColor=none;', kx, y + 3, 16, 16)
    if label:
        p.add(label, txt(lab_color or TXT, 12, 'left'), x + 50, y - 2, 220, 26)


def segment(p, x, y, items, active=0, w_item=84, h=30):
    p.add('', rect(BG2, BORDER, arc=50), x, y, w_item * len(items), h)
    for i, t in enumerate(items):
        if i == active:
            p.add('', rect(ACCENT, 'none', arc=50), x + i * w_item + 2, y + 2, w_item - 4, h - 4)
            p.add(t, txt('#FFFFFF', 12, 'center', bold=True), x + i * w_item, y, w_item, h)
        else:
            p.add(t, txt(TXT2, 12, 'center'), x + i * w_item, y, w_item, h)


def stat_card(p, x, y, w, h, num, label, color=ACCENT):
    p.add('', rect(CARD, BORDER), x, y, w, h)
    p.add(num, txt(color, 22, 'center', bold=True), x, y + 8, w, 32)
    p.add(label, txt(TXT2, 12, 'center'), x, y + h - 32, w, 24)


def input_box(p, x, y, w, h, placeholder, icon=None):
    p.add('', rect(CARD2, BORDER, arc=10), x, y, w, h)
    t = (icon + '  ' if icon else '') + placeholder
    p.add(t, txt(TXT2, 12, 'left'), x + 12, y, w - 24, h)


def form_row(p, x, y, label, w=360, control='input', value='', cw=200, on=True):
    """设置页表单行: 标签 + 控件"""
    p.add(label, txt(TXT2, 13, 'left'), x, y, w - cw - 20, 32)
    cx = x + w - cw - 8
    if control == 'input':
        input_box(p, cx, y + 2, cw, 28, value)
    elif control == 'combo':
        input_box(p, cx, y + 2, cw, 28, value + '   ▾')
    elif control == 'toggle':
        toggle(p, cx, y + 5, on=on)
    elif control == 'slider':
        p.add('', rect('#3A4152', 'none', arc=50), cx, y + 14, cw, 4)
        p.add('', f'ellipse;fillColor={ACCENT};strokeColor=none;', cx + int(value) if str(value).isdigit() else cx + cw // 2, y + 8, 16, 16)


def table(p, x, y, col_ws, headers, rows, row_h=32, header_h=34, aligns=None):
    w = sum(col_ws)
    p.add('', rect(CARD2, BORDER, arc=0), x, y, w, header_h)
    cx = x
    for i, (hd, cw) in enumerate(zip(headers, col_ws)):
        p.add(hd, txt(TXT, 12, 'center', bold=True), cx + 6, y, cw - 12, header_h)
        cx += cw
    ry = y + header_h
    for ri, row in enumerate(rows):
        if ri % 2 == 0:
            p.add('', rect(ROWALT, ROWALT, arc=0), x, ry, w, row_h)
        cx = x
        for i, cw in enumerate(col_ws):
            cell = row[i] if i < len(row) else ''
            color = TXT
            if isinstance(cell, tuple):
                cell, color = cell
            al = aligns[i] if aligns else ('left' if i == 0 else 'center')
            p.add(str(cell), txt(color, 12, al), cx + 8, ry, cw - 16, row_h)
            cx += cw
        ry += row_h
    total_h = header_h + row_h * len(rows)
    p.add('', rect('none', BORDER, arc=0, w=1), x, y, w, total_h)
    return ry


def note(p, x, y, w, h, title, lines):
    p.add('', rect(NOTEBG, YELLOW, arc=4, w=1), x, y, w, h)
    p.add('📌 ' + title, txt(NOTEF, 13, 'left', bold=True), x + 14, y + 8, w - 28, 22)
    p.add('\n'.join(lines), txt('#EAD9A0', 12, 'left', valign='top'), x + 14, y + 34, w - 28, h - 44)


def nav_dot(p, x, y, c=GREEN):
    p.add('', f'ellipse;fillColor={c};strokeColor=none;', x, y, 10, 10)


# ================= 外壳(标题栏/导航/状态栏) =================
NAV_ITEMS = [('实时检测', '检'), ('历史记录', '录'), ('设备设置', '设'), ('系统设置', '管')]


def shell(p, active):
    p.add('', rect(BG, '#08090D', arc=3), 0, 0, 1920, 1080)
    # ---- 标题栏 ----
    p.add('', rect(BG2, BG2, arc=0), 0, 0, 1920, 48)
    p.add('', rect(ACCENT, 'none', arc=22), 14, 10, 28, 28)
    p.add('OS', txt('#FFFFFF', 11, 'center', bold=True), 14, 10, 28, 28)
    p.add('漆包线表面缺陷检测系统', txt(TXT, 15, 'left', bold=True), 54, 0, 240, 48)
    p.add('V2.0', txt(TXT2, 11, 'left'), 268, 0, 60, 48)
    # 右侧: 运行状态 / 用户 / 告警 / 时间 / 窗口按钮
    p.add('', rect('#14351F', GREEN, arc=50), 1226, 11, 132, 26)
    p.add('● 运行中', txt('#7BE49E', 12, 'center', bold=True), 1226, 11, 132, 26)
    p.add('', rect('#262B38', BORDER, arc=50), 1370, 11, 150, 26)
    p.add('👤 张三 · 工人', txt(TXT, 12, 'center'), 1370, 11, 150, 26)
    p.add('', rect('#262B38', BORDER, arc=50), 1532, 11, 96, 26)
    p.add('🔔 告警 0', txt(TXT, 12, 'center'), 1532, 11, 96, 26)
    p.add('2026-08-29 14:30:25', txt(TXT2, 12, 'center'), 1640, 11, 160, 26)
    for i, sym in enumerate(['—', '□', '✕']):
        bx = 1836 + i * 28
        kind = 'danger' if sym == '✕' else 'ghost'
        p.add('', rect(RED if sym == '✕' else '#2E3444', 'none', arc=14), bx, 12, 24, 24)
        p.add(sym, txt('#FFFFFF' if sym == '✕' else TXT2, 12, 'center'), bx, 12, 24, 24)
    # ---- 左侧导航 ----
    p.add('', rect(BG2, BG2, arc=0), 0, 48, 188, 996)
    y = 76
    for i, (label, glyph) in enumerate(NAV_ITEMS):
        if i == active:
            p.add('', rect('#262B38', 'none', arc=8), 10, y - 6, 168, 46)
            p.add('', rect(ACCENT, 'none', arc=50), 10, y - 6, 4, 46)
            gbg, gfc, lfc = ACCENT, '#FFFFFF', TXT
        else:
            gbg, gfc, lfc = '#2E3444', TXT2, TXT2
        p.add('', rect(gbg, 'none', arc=20), 24, y, 34, 34)
        p.add(glyph, txt(gfc, 14, 'center', bold=True), 24, y, 34, 34)
        p.add(label, txt(lfc, 14, 'left', bold=(i == active)), 70, y, 110, 34)
        y += 56
    p.add('', rect('#2E3444', 'none', arc=50), 8, 984, 172, 1)
    p.add('V2.0.0 · 已激活授权', txt(TXT2, 11, 'left'), 20, 998, 150, 24)
    # ---- 底部状态栏 ----
    p.add('', rect(BG2, BG2, arc=0), 0, 1044, 1920, 36)
    x = 16
    for label, state in [('相机1', 'ok'), ('相机2', 'ok'), ('相机3', 'err'), ('相机4', 'ok'),
                         ('光源', 'ok'), ('计米轮', 'ok'), ('放电', 'off'), ('IO卡', 'ok')]:
        x += chip(p, x, 1049, label, state) + 10
    p.add('已检长度: 1523.45 m', txt(TEAL, 12, 'center', bold=True), 1360, 1049, 160, 26)
    p.add('线速: 12.35 m/s', txt(TXT, 12, 'center'), 1540, 1049, 130, 26)
    p.add('帧率: 30 FPS', txt(TXT, 12, 'center'), 1686, 1049, 110, 26)
    p.add('14:30:25', txt(TXT2, 12, 'center'), 1812, 1049, 90, 26)


# ================= 缺陷分布总览泳道 =================
LANE_LABELS = ['左', '上', '右', '下', '放电']
LANE_TICKS = {
    0: [0.05, 0.13, 0.40, 0.415, 0.72],
    1: [0.20, 0.55, 0.90],
    2: [0.31, 0.335, 0.66],
    3: [0.08, 0.83],
    4: [0.47, 0.95],
}


def overview_lanes(p, x, y, w, lane_h=14, gap=4, scale=None):
    """5 条泳道: 左/上/右/下/放电, 红=视觉缺陷 橙=放电针孔"""
    for i, lab in enumerate(LANE_LABELS):
        ly = y + i * (lane_h + gap)
        p.add(lab, txt(TXT2 if lab != '放电' else ORANGE, 11, 'right'), x - 44, ly - 2, 38, lane_h + 4)
        p.add('', rect('#1A1E28', BORDER, arc=0), x, ly, w, lane_h)
        for f in LANE_TICKS[i]:
            tx = x + f * w
            color = ORANGE if i == 4 else RED
            p.add('', rect(color, 'none', arc=0), tx, ly + 1, 2.5, lane_h - 2)
    bottom = y + 5 * (lane_h + gap)
    if scale:
        for i, s in enumerate(scale):
            sx = x + i * (w / (len(scale) - 1))
            p.add(s, txt(TXT2, 10, 'center'), sx - 40, bottom, 80, 16)
    return bottom


# ================= 通道图像卡片 =================
def img_cell(p, x, y, w, h, title, online=True, seg=1, defects=(), nosignal=False, wire=True, mode='result'):
    p.add('', rect(CARD, BORDER, arc=4), x, y, w, h)
    p.add('', rect(CARD2, 'none', arc=4), x, y, w, 34)
    dot = GREEN if online else RED
    p.add('', f'ellipse;fillColor={dot};strokeColor=none;', x + 12, y + 12, 10, 10)
    p.add(title, txt(TXT, 13, 'left', bold=True), x + 30, y, 220, 34)
    if not online:
        p.add('已断开', txt(RED, 11, 'left', bold=True), x + 30 + len(title) * 13 + 6, y, 70, 34)
    segment(p, x + w - 176, y + 4, ['原始图', '结果图'], seg, w_item=82, h=26)
    ix, iy, iw, ih = x + 8, y + 42, w - 16, h - 52
    p.add('', rect(IMAGE, BORDER, arc=2), ix, iy, iw, ih)
    if nosignal:
        p.add('⚠ 无信号', txt(RED, 17, 'center', bold=True), ix, iy + ih / 2 - 34, iw, 26)
        p.add('请检查相机连接或读取模式设置', txt(TXT2, 12, 'center'), ix, iy + ih / 2 - 4, iw, 22)
        p.add('点击此处可打开设备设置', txt(ACCENT, 11, 'center'), ix, iy + ih / 2 + 22, iw, 20)
    else:
        if wire:
            p.add('', rect('#3C4150', 'none', arc=0), ix, iy + ih / 2 - 24, iw, 48)
            p.add('', rect('#4A5164', 'none', arc=0), ix, iy + ih / 2 - 24, iw, 6)
        for (fx, fy, fw, fh, lab, conf) in defects:
            bx, by = ix + fx * iw, iy + fy * ih
            bw, bh = fw * iw, fh * ih
            p.add('', rect('none', RED, arc=0, w=2), bx, by, bw, bh)
            p.add('', rect(RED, 'none', arc=10), bx, by - 16, len(lab) * 11 + 62, 15)
            p.add(f'{lab} {conf}', txt('#FFFFFF', 10, 'center'), bx, by - 16, len(lab) * 11 + 62, 15)
        n = len(defects)
        if n:
            p.add('', rect('#3A1A1C', RED, arc=50), ix + 8, iy + ih - 26, 88, 20)
            p.add(f'缺陷: {n}', txt(RED, 11, 'center', bold=True), ix + 8, iy + ih - 26, 88, 20)
        p.add('2000×300 @30fps', txt(TXT2, 10, 'right'), ix + iw - 130, iy + ih - 24, 122, 18)


# =========================================================
# 页 1: 设计规范
# =========================================================
def page_spec():
    p = Page('1. 设计规范', 1640, 1240)
    p.add('UI 重构设计规范 — 漆包线表面缺陷检测系统', txt(TXT, 24, 'left', bold=True), 40, 30, 900, 40)
    p.add('深色工业主题 · 触控友好 · 状态一目了然 · 面向车间产线环境 (建议分辨率 1920×1080)',
          txt(TXT2, 13, 'left'), 40, 74, 1000, 24)

    # ---- 色板 ----
    p.add('一、配色规范 (Dark Industrial Theme)', txt(TXT, 16, 'left', bold=True), 40, 116, 600, 28)
    palette = [
        ('窗口底色', BG), ('顶栏/导航/状态栏', BG2), ('卡片底色', CARD), ('输入框/次级块', CARD2),
        ('图像区底色', IMAGE), ('边框', BORDER), ('主色 · 品牌蓝', ACCENT), ('强调 · 青', TEAL),
        ('成功 · 运行', GREEN), ('警告', YELLOW), ('危险 · 缺陷', RED), ('放电缺陷 · 橙', ORANGE),
        ('主文字', TXT), ('次级文字', TXT2),
    ]
    for i, (name, c) in enumerate(palette):
        sx = 40 + (i % 7) * 176
        sy = 154 + (i // 7) * 104
        p.add('', rect(c, BORDER, arc=8, w=1), sx, sy, 160, 56)
        p.add(name, txt(TXT if c in (BG, BG2, CARD, CARD2, IMAGE, BORDER, TXT2) else '#14161C',
                        11, 'center'), sx, sy + 8, 160, 18)
        p.add(c, txt(TXT2 if c in (BG, BG2, CARD, CARD2, IMAGE, BORDER) else '#444B5C',
                     11, 'center'), sx, sy + 28, 160, 18)
    p.add('状态色使用规则: 绿=已连接/运行中 · 红=断开/缺陷/告警 · 黄=警告/待处理 · 灰=未启用 · 蓝=选中/链接 · 橙=放电类缺陷',
          txt(NOTEF, 12, 'left'), 40, 370, 1200, 22)

    # ---- 字体 ----
    p.add('二、字体规范', txt(TXT, 16, 'left', bold=True), 40, 412, 300, 28)
    table(p, 40, 448, [220, 160, 160, 420], ['用途', '字号', '字重', '示例'],
          [['页面标题', '18-20', 'Bold', ('设备设置', TXT)],
           ['卡片标题', '14', 'Bold', ('实时缺陷列表', TXT)],
           ['正文/标签', '13', 'Regular', ('当前批次: 20260829-A', TXT)],
           ['辅助说明', '11-12', 'Regular', ('修改后需重启相机生效', TXT2)],
           ['数值 KPI', '22', 'Bold', ('1523.45 m — 可用等宽字体如 DIN/Consolas', ACCENT)]],
          row_h=34)
    p.add('字体族: 微软雅黑 (Microsoft YaHei); 数字建议使用等宽或 DIN 风格字体以便快速读数',
          txt(TXT2, 12, 'left'), 40, 650, 900, 20)

    # ---- 组件 ----
    p.add('三、组件规范', txt(TXT, 16, 'left', bold=True), 40, 686, 300, 28)
    button(p, 40, 722, 120, 40, '主按钮', 'primary')
    button(p, 176, 722, 120, 40, '成功/启动', 'success')
    button(p, 312, 722, 120, 40, '停止/危险', 'danger')
    button(p, 448, 722, 120, 40, '次级按钮', 'outline')
    button(p, 584, 722, 120, 40, '文字按钮', 'ghost')
    p.add('按钮高度: 大操作 44-64(触控), 常规 32-40; 主操作每区域仅 1 个',
          txt(TXT2, 11, 'left'), 40, 770, 700, 20)

    x0 = 40
    chip(p, x0, 800, '相机1 已连接', 'ok'); x0 += 150
    chip(p, x0, 800, '相机3 已断开', 'err'); x0 += 150
    chip(p, x0, 800, '放电 未启用', 'off'); x0 += 150
    chip(p, x0, 800, '告警待处理', 'warn'); x0 += 140
    chip(p, x0, 800, '批次信息', 'accent')
    toggle(p, 40, 846, on=True, label='开关-开 (绿)')
    toggle(p, 240, 846, on=False, label='开关-关 (灰)')
    segment(p, 440, 842, ['原始图', '结果图'], 1, w_item=80, h=30)
    input_box(p, 630, 842, 220, 30, '请输入批次名称')
    p.add('', rect(CARD, BORDER), 880, 836, 150, 66)
    p.add('23', txt(ACCENT, 22, 'center', bold=True), 880, 842, 150, 32)
    p.add('统计卡片', txt(TXT2, 12, 'center'), 880, 874, 150, 24)

    # ---- 页面索引 ----
    p.add('四、页面结构索引 (本文件共 7 页)', txt(TXT, 16, 'left', bold=True), 40, 906, 600, 28)
    table(p, 40, 942, [200, 320, 560],
          ['页面', '名称', '说明'],
          [['P2', '全局框架', '标题栏 + 左侧导航 + 内容区 + 底部设备状态栏 (所有页面共用)'],
           ['P3', '实时检测 (主页)', '2×2 通道图像 + 设备一键启停 + 实时缺陷统计/列表 + 缺陷分布泳道'],
           ['P4', '历史记录', '筛选/批次树 + 批次泳道总览 + 通道图像 + 缺陷明细与复判'],
           ['P5', '设备设置', '相机×4 / 光源 / 计米轮 / 放电检测 / IO卡报警 参数卡片'],
           ['P6', '系统设置', '算法参数 / 通道与缺陷类型 / 用户权限管理'],
           ['P7', '弹窗与登录', '登录 / 更换批次确认 / 缺陷复判 / 透视矫正 / 告警弹窗']],
          row_h=34)

    note(p, 1120, 116, 460, 320, '设计原则', [
        '1. 深色主题: 车间暗光环境不刺眼, 同时让图像与缺陷框更突出;',
        '2. 检测页零学习成本: 工人只需看图像、按启停、换批次;',
        '3. 工程师功能(串口/曝光/算法)收进"设备设置/系统设置", 按权限开放;',
        '4. 状态一屏可见: 底部状态栏 8 个设备芯片 + 顶部运行徽标;',
        '5. 所有启停按钮带状态反馈(文案随状态切换: 启动↔关闭);',
        '6. 缺陷一律红色框, 放电缺陷橙色标识, 与缺陷泳道颜色一致;',
        '7. 所有确认类操作使用模态弹窗, 防误触。'])
    note(p, 1120, 460, 460, 300, '相对现有 UI 的主要改进', [
        '· 导航 4 项 → 语义更清晰: 实时检测/历史记录/设备设置/系统设置;',
        '· 启停按钮从右下小按钮 → 检测页右侧常驻大按钮面板;',
        '· 缺陷表格(位置/传感器/类型) → 增加时间/置信度列, 可点击定位;',
        '· 底部信息栏 → 升级为带彩色状态芯片的状态栏;',
        '· 新增: 实时缺陷统计卡片、放电检测独立配置、报警通道配置;',
        '· 记录页增加筛选器与复判(改类型/标误报)工作流;',
        '· 统一配色与圆角, 消除散落的硬编码颜色。'])
    note(p, 1120, 784, 460, 240, '可选扩展 (二期建议)', [
        '· 统计报表页: 按批次/日期导出缺陷趋势图、类型占比饼图;',
        '· 告警记录页: IO 报警与放电事件历史;',
        '· 复判工作站: 质检员批量复核缺陷、生成训练样本回流;',
        '· 多语言支持 (中/英)。'])
    return p


# =========================================================
# 页 2: 全局框架
# =========================================================
def page_shell():
    p = Page('2. 全局框架与导航', 2560, 1220)
    shell(p, active=0)
    # 内容区占位
    p.add('', rect(BG, BORDER, arc=2, dash=True), 200, 60, 1708, 972)
    p.add('内容区 (QStackedWidget)', txt(TXT2, 18, 'center', bold=True), 200, 480, 1708, 30)
    p.add('根据左侧导航切换:  实时检测  |  历史记录  |  设备设置  |  系统设置',
          txt(TXT2, 13, 'center'), 200, 520, 1708, 26)

    note(p, 1960, 48, 560, 300, '全局框架说明', [
        '① 标题栏(48px): Logo + 系统名 + 版本 | 运行状态徽标 | 当前用户 | 告警铃铛(有告警变红+数字) | 时钟 | 窗口按钮;',
        '② 左侧导航(188px): 图标+文字, 选中态=蓝色竖条+高亮底色; 底部显示版本与授权状态;',
        '③ 内容区: QStackedWidget 承载 4 个功能页, 切换无闪烁;',
        '④ 底部状态栏(36px): 8 个设备状态芯片 + 已检长度 + 线速 + 帧率 + 时钟, 300ms 刷新;',
        '⑤ 对应现有代码: Window + Panel + QStackedWidget + BottomInfoInterface, 保留无边框窗口方案。'])
    note(p, 1960, 380, 560, 260, '状态栏规则', [
        '· 绿点 = 已连接/已启用;  红点 = 已断开/故障;',
        '· 灰点 = 未启用(未点启动);  点击芯片可跳转到"设备设置";',
        '· 相机1~4 对应 4 路检测通道; 光源=光源控制器串口;',
        '· 计米轮=测速编码器; 放电=放电检测模块; IO卡=报警输出;',
        '· 任何设备由"已连接"变"已断开"时, 状态栏闪烁提示 3 次并在告警铃铛计数+1。'])
    note(p, 1960, 672, 560, 220, '顶部运行状态徽标', [
        '· 运行中(绿): 检测已启动且正常出帧;',
        '· 已停止(灰): 检测未启动;',
        '· 告警中(红, 闪烁): 最近 3 秒内触发过 IO 报警;',
        '· 该徽标在所有页面常驻, 工人随时掌握系统状态。'])
    return p


# =========================================================
# 页 3: 实时检测主页
# =========================================================
def page_realtime():
    p = Page('3. 实时检测主页', 2560, 1220)
    shell(p, active=0)

    # ---- 顶部信息条 ----
    p.add('', rect(CARD, BORDER, arc=8), 200, 60, 560, 52)
    for i, (lab, val) in enumerate([('当前批次', '20260829-A'), ('型号', 'QA-1 (0.5mm)'), ('负责人', '张三')]):
        px = 220 + i * 186
        p.add(lab, txt(TXT2, 11, 'left'), px, 66, 170, 16)
        p.add(val, txt(TXT, 15, 'left', bold=True), px, 84, 170, 22)
        if i < 2:
            p.add('', rect(BORDER, BORDER, arc=50), 200 + (i + 1) * 186, 70, 1, 32)
    kpis = [('线速', '12.35', 'm/s', ACCENT), ('批次长度', '856.20', 'm', TEAL),
            ('累计已检', '1523.4', 'm', TXT), ('缺陷数', '23', '个', RED), ('单帧耗时', '28', 'ms', TXT2)]
    for i, (lab, val, unit, c) in enumerate(kpis):
        kx = 780 + i * 160
        p.add('', rect(CARD, BORDER, arc=8), kx, 60, 150, 52)
        p.add(val, txt(c, 20, 'center', bold=True), kx, 62, 100, 30)
        p.add(unit, txt(TXT2, 10, 'left'), kx + 100, 74, 44, 18)
        p.add(lab, txt(TXT2, 11, 'center'), kx, 92, 150, 16)
    p.add('', rect('#14351F', GREEN, arc=10, w=1), 1744, 60, 164, 52)
    p.add('● 检测运行中', txt('#7BE49E', 16, 'center', bold=True), 1744, 60, 164, 52)

    # ---- 2×2 通道图像 ----
    img_cell(p, 200, 124, 632, 386, '通道1 · 左面', True, 1,
             [(0.30, 0.34, 0.13, 0.22, '汽包', '0.92'), (0.62, 0.42, 0.09, 0.15, '粒子', '0.81')])
    img_cell(p, 844, 124, 632, 386, '通道2 · 上面', True, 1,
             [(0.48, 0.30, 0.11, 0.20, '毛粘线', '0.88')])
    img_cell(p, 200, 522, 632, 386, '通道3 · 右面', False, 0, nosignal=True)
    img_cell(p, 844, 522, 632, 386, '通道4 · 下面', True, 0,
             [(0.22, 0.38, 0.10, 0.16, '漆瘤', '0.95')], wire=True)

    # ---- 右侧面板: 设备控制 + 统计 + 缺陷列表 ----
    rx, rw = 1488, 420
    p.add('', rect(CARD, BORDER, arc=8), rx, 124, rw, 784)
    p.add('设备控制', txt(TXT, 14, 'left', bold=True), rx + 14, 132, 200, 24)
    button(p, rx + 12, 162, rw - 24, 46, '■  停止检测  (点击关闭)', 'danger', size=16)
    devs = [('摄像头', True), ('光源', True), ('计米轮', True), ('放电检测', False)]
    for i, (lab, on) in enumerate(devs):
        dx = rx + 12 + (i % 2) * 200
        dy = 222 + (i // 2) * 60
        p.add('', rect(CARD2, BORDER, arc=8), dx, dy, 190, 50)
        nav_dot(p, dx + 12, dy + 20, GREEN if on else '#5A6274')
        p.add(('关闭' if on else '启动') + lab, txt(TXT, 13, 'left', bold=True), dx + 28, dy, 110, 50)
        toggle(p, dx + 140, dy + 14, on=on)
    p.add('', rect(BORDER, BORDER, arc=50), rx + 12, 352, rw - 24, 1)
    p.add('实时缺陷统计', txt(TXT, 14, 'left', bold=True), rx + 14, 362, 200, 24)
    stats = [('23', '总缺陷', ACCENT), ('8', '汽包', TEAL), ('6', '粒子', PURPLE),
             ('4', '漆瘤', YELLOW), ('3', '毛粘线', GREEN), ('2', '针孔·放电', ORANGE)]
    for i, (num, lab, c) in enumerate(stats):
        sx = rx + 12 + (i % 3) * 134
        sy = 392 + (i // 3) * 72
        stat_card(p, sx, sy, 126, 64, num, lab, c)
    p.add('', rect(BORDER, BORDER, arc=50), rx + 12, 548, rw - 24, 1)
    p.add('实时缺陷列表', txt(TXT, 14, 'left', bold=True), rx + 14, 558, 200, 24)
    button(p, rx + rw - 76, 556, 62, 26, '导出', 'ghost', size=11, bold=False)
    table(p, rx + 12, 590, [86, 92, 68, 84, 62],
          ['时间', '位置(m)', '通道', '类型', '置信'],
          [['14:29:51', '856.12', '通道1', ('汽包', RED), '0.93'],
           ['14:29:48', '855.90', '通道4', ('漆瘤', YELLOW), '0.95'],
           ['14:29:30', '854.31', '通道2', ('毛粘线', GREEN), '0.88'],
           ['14:29:12', '853.02', '通道1', ('粒子', PURPLE), '0.81'],
           ['14:28:57', '851.77', '通道3', ('汽包', RED), '0.90'],
           ['14:28:40', '850.24', '—', ('针孔', ORANGE), '放电'],
           ['14:28:22', '849.10', '通道2', ('汽包', RED), '0.92']],
          row_h=29, header_h=30)
    p.add('▲ 自动滚动 · 最新在上 · 点击行定位到对应通道图像', txt(TXT2, 11, 'center'), rx + 12, 852, rw - 24, 18)
    p.add('检测停止时按钮变绿色"▶ 启动检测"', txt(TXT2, 11, 'center'), rx + 12, 876, rw - 24, 18)

    # ---- 底部缺陷分布泳道 ----
    p.add('', rect(CARD, BORDER, arc=8), 200, 920, 1708, 112)
    p.add('缺陷分布总览 — 当前批次 (滚动窗口: 最近 50 m)', txt(TXT, 13, 'left', bold=True), 216, 926, 420, 22)
    button(p, 1620, 926, 80, 24, '历史', 'ghost', size=11, bold=False)
    button(p, 1708, 926, 80, 24, '缩放', 'ghost', size=11, bold=False)
    button(p, 1796, 926, 96, 24, '清空显示', 'ghost', size=11, bold=False)
    overview_lanes(p, 262, 952, 1560, lane_h=11, gap=3,
                   scale=['806.20m', '818.70m', '831.20m', '843.70m', '856.20m'])

    note(p, 1960, 48, 560, 330, '实时检测页设计说明', [
        '① 顶部信息条: 批次/型号/负责人 + 5 个 KPI + 运行状态徽标(常驻);',
        '② 图像区 2×2: 通道1~4 对应 左/上/右/下 四个检测面, 每格右上角"原始图/结果图"切换;',
        '   结果图上叠加缺陷红框+类型+置信度; 点击图像 → 模态放大查看(保留现有 FaultView);',
        '③ 右上 设备控制卡: 大按钮"启动/停止检测"(运行时红色, 停止时绿色) + 4 个设备开关;',
        '   替代现有 EnableInterface 的 5 个文字按钮, 触控目标更大、状态更直观;',
        '④ 右中 实时统计卡: 按缺陷类型计数(YOLO 4 类 + 放电针孔), 点击卡片可过滤列表;',
        '⑤ 右下 实时缺陷列表: 时间/位置/通道/类型/置信度, 点击行 → 对应通道图像高亮该缺陷;',
        '⑥ 底部 缺陷分布泳道: 保留现有 FaultOverview 的 5 线设计(左/上/右/下/放电),',
        '   改为随检测长度滚动的时间轴, 红=视觉缺陷, 橙=放电针孔。'])
    note(p, 1960, 410, 560, 260, '交互细节', [
        '· 启停顺序校验沿用现有逻辑: 串口未设置/连接失败时弹窗提示;',
        '· "启动检测"前置条件: 至少一路相机已启用, 否则提示;',
        '· 通道图像"无信号"态提供跳转"设备设置"的快捷入口;',
        '· 批次未设置时, 顶部信息条显示黄色提示"未设置批次, 缺陷将不保存";',
        '· 放电事件触发时, 底部泳道"放电"道出现橙色刻度并短促闪烁。'])
    note(p, 1960, 702, 560, 240, '与现有组件的映射', [
        'CameraDisplayInterface → 2×2 图像网格;',
        'EnableInterface → 右侧"设备控制"卡;',
        'BatchInfomationWidget(结果表) → "实时缺陷列表";',
        'BatchNameWidget(更换批次) → 顶部信息条点击"批次"打开弹窗(见 P7);',
        'ModelSettingWidget(型号配置) → 移入"系统设置"(见 P6);',
        'BottomInfoInterface → 底部状态栏;',
        'InfoWidget(速度/处理时间) → 顶部 KPI 条。'])
    return p


# =========================================================
# 页 4: 历史记录
# =========================================================
def page_history():
    p = Page('4. 历史记录与复判', 2560, 1220)
    shell(p, active=1)

    # ---- 左侧筛选/批次面板 ----
    p.add('', rect(CARD, BORDER, arc=8), 200, 60, 250, 972)
    input_box(p, 214, 74, 222, 32, '🔍 搜索批次 / 缺陷', )
    p.add('日期', txt(TXT2, 11, 'left'), 214, 118, 60, 20)
    input_box(p, 214, 138, 222, 30, '2026-08-01 ~ 2026-08-29 ▾')
    p.add('缺陷类型', txt(TXT2, 11, 'left'), 214, 180, 80, 20)
    input_box(p, 214, 200, 222, 30, '全部类型 ▾')
    p.add('通道', txt(TXT2, 11, 'left'), 214, 242, 60, 20)
    input_box(p, 214, 262, 222, 30, '全部通道 ▾')
    toggle(p, 214, 308, on=False, label='包含已标误报', lab_color=TXT2)
    p.add('', rect(BORDER, BORDER, arc=50), 214, 344, 222, 1)
    p.add('批次列表', txt(TXT, 13, 'left', bold=True), 214, 352, 120, 24)
    batches = [('20260829-A', '今天 08:20 · 张三 · 缺陷23', True),
               ('20260828-B', '昨天 14:20 · 李四 · 缺陷47', False),
               ('20260828-A', '昨天 07:55 · 张三 · 缺陷12', False),
               ('20260827-C', '08-27 22:10 · 王五 · 缺陷61', False),
               ('20260827-B', '08-27 14:02 · 李四 · 缺陷8', False),
               ('20260827-A', '08-27 07:40 · 张三 · 缺陷30', False)]
    by = 384
    for name, sub, sel in batches:
        if sel:
            p.add('', rect('#262B38', 'none', arc=6), 210, by, 230, 54)
            p.add('', rect(ACCENT, 'none', arc=50), 210, by, 4, 54)
        p.add(name, txt(TXT if sel else TXT2, 13, 'left', bold=sel), 224, by + 6, 200, 20)
        p.add(sub, txt(TXT2, 10.5, 'left'), 224, by + 28, 210, 18)
        by += 58
    p.add('共 128 个批次 · 按时间倒序', txt(TXT2, 10.5, 'center'), 214, by + 6, 222, 18)

    # ---- 中部 ----
    cx0, cw = 462, 1074
    kpis = [('当前批次', '20260828-B', TXT), ('总缺陷', '47', RED), ('检测长度', '2350.0 m', TEAL),
            ('缺陷密度', '2.0 /100m', YELLOW), ('放电针孔', '5', ORANGE), ('误报标记', '3', TXT2)]
    for i, (lab, val, c) in enumerate(kpis):
        kx = cx0 + i * 183
        p.add('', rect(CARD, BORDER, arc=8), kx, 60, 173, 52)
        p.add(val, txt(c, 17, 'center', bold=True), kx, 62, 173, 28)
        p.add(lab, txt(TXT2, 11, 'center'), kx, 92, 173, 16)
    # 泳道总览
    p.add('', rect(CARD, BORDER, arc=8), cx0, 124, cw, 140)
    p.add('批次缺陷分布总览 (红=视觉缺陷 橙=放电)', txt(TXT, 13, 'left', bold=True), cx0 + 14, 130, 400, 22)
    overview_lanes(p, cx0 + 60, 158, cw - 90, lane_h=13, gap=4,
                   scale=['0.00m', '587.5m', '1175.0m', '1762.5m', '2350.0m'])
    # 通道缺陷图
    p.add('缺陷图像 (该批次 · 按通道汇总)', txt(TXT, 13, 'left', bold=True), cx0 + 4, 276, 400, 22)
    for i in range(4):
        gx = cx0 + i * 273
        img_cell(p, gx, 302, 261, 300, f'通道{i+1}', True, 1,
                 defects=[(0.32, 0.36, 0.2, 0.2, '汽包', '0.9')] if i != 2 else [], wire=True)
    p.add('点击通道图 → 打开该通道缺陷缩略图浏览; 点击缩略图 → 右侧显示缺陷详情',
          txt(TXT2, 11, 'left'), cx0 + 4, 610, 900, 18)
    # 缺陷明细表
    p.add('', rect(CARD, BORDER, arc=8), cx0, 636, cw, 396)
    p.add('缺陷明细', txt(TXT, 14, 'left', bold=True), cx0 + 14, 644, 200, 24)
    button(p, cx0 + cw - 170, 644, 76, 26, '导出CSV', 'ghost', size=11, bold=False)
    button(p, cx0 + cw - 88, 644, 76, 26, '批量复判', 'ghost', size=11, bold=False)
    table(p, cx0 + 14, 678, [60, 150, 120, 100, 130, 110, 130, 180],
          ['#', '时间', '位置(m)', '通道', '缺陷类型', '置信度', '状态', '操作'],
          [['1', '08-28 14:21:05', '12.35', '通道1', ('汽包', RED), '0.93', ('待复判', YELLOW), '[ 复判 ]  [ 详情 ]'],
           ['2', '08-28 14:22:41', '35.90', '通道2', ('毛粘线', GREEN), '0.88', ('已确认', TXT2), '[ 复判 ]  [ 详情 ]'],
           ['3', '08-28 14:25:12', '78.02', '通道4', ('漆瘤', YELLOW), '0.95', ('待复判', YELLOW), '[ 复判 ]  [ 详情 ]'],
           ['4', '08-28 14:27:55', '121.64', '通道1', ('粒子', PURPLE), '0.81', ('误报', RED), '[ 恢复 ]  [ 详情 ]'],
           ['5', '08-28 14:30:20', '168.30', '—', ('针孔·放电', ORANGE), '放电', ('已确认', TXT2), '[ 详情 ]'],
           ['6', '08-28 14:33:47', '215.77', '通道3', ('汽包', RED), '0.90', ('待复判', YELLOW), '[ 复判 ]  [ 详情 ]'],
           ['7', '08-28 14:36:08', '260.15', '通道2', ('汽泡', RED), '0.92', ('待复判', YELLOW), '[ 复判 ]  [ 详情 ]']],
          row_h=34, header_h=32)
    p.add('共 47 条 · 第 1 / 5 页        ◀ 上一页    1  2  3  4  5    下一页 ▶',
          txt(TXT2, 12, 'center'), cx0 + 14, 990, cw - 28, 24)

    # ---- 右侧详情 ----
    dx, dw = 1548, 360
    p.add('', rect(CARD, BORDER, arc=8), dx, 60, dw, 972)
    p.add('缺陷详情', txt(TXT, 14, 'left', bold=True), dx + 14, 70, 200, 24)
    p.add('', rect(IMAGE, BORDER, arc=4), dx + 14, 102, dw - 28, 300)
    p.add('', rect('#3C4150', 'none', arc=0), dx + 14, 232, dw - 28, 40)
    p.add('', rect('none', RED, arc=0, w=2), dx + 120, 190, 96, 96)
    p.add('', rect(RED, 'none', arc=10), dx + 120, 172, 118, 16)
    p.add('汽泡 0.93', txt('#FFFFFF', 10, 'center'), dx + 120, 172, 118, 16)
    info = [('缺陷类型', '汽泡 (Bubble)'), ('位置', '12.35 m'), ('通道', '通道1 · 左面'),
            ('时间', '2026-08-28 14:21:05'), ('置信度', '0.93'), ('负责人', '李四')]
    iy = 420
    for lab, val in info:
        p.add(lab, txt(TXT2, 12, 'left'), dx + 14, iy, 100, 26)
        p.add(val, txt(TXT, 12, 'left'), dx + 118, iy, dw - 140, 26)
        iy += 30
    p.add('更改类型', txt(TXT2, 12, 'left'), dx + 14, iy + 6, 100, 26)
    input_box(p, dx + 118, iy + 6, dw - 140, 28, '汽泡 ▾  (可编辑/新增类型)')
    button(p, dx + 14, iy + 48, 160, 38, '◀ 上一个', 'outline', size=12)
    button(p, dx + 186, iy + 48, 160, 38, '下一个 ▶', 'outline', size=12)
    button(p, dx + 14, iy + 96, dw - 28, 42, '应用修改', 'primary', size=14)
    button(p, dx + 14, iy + 146, dw - 28, 38, '标记为误报', 'outline', size=13)
    p.add('缩略图 (同检测点)', txt(TXT2, 11, 'left'), dx + 14, iy + 196, 200, 18)
    for i in range(4):
        tx = dx + 14 + i * 84
        p.add('', rect(IMAGE, ACCENT if i == 0 else BORDER, arc=4, w=2 if i == 0 else 1), tx, iy + 218, 76, 56)
        p.add(f'通道{i+1}', txt(TXT2, 10, 'center'), tx, iy + 276, 76, 14)

    note(p, 1960, 48, 560, 330, '历史记录页设计说明', [
        '① 左栏: 搜索 + 筛选(日期/缺陷类型/通道/是否含误报) + 批次列表(保留现有 output 目录结构);',
        '② 中部上: 批次级 5 泳道总览(现有 BatchFaultOverview 升级为全距离轴);',
        '③ 中部中: 4 通道缺陷图像(现有 VisionDetectWidget), 点击进入缩略图浏览;',
        '④ 中部下: 缺陷明细表 + 分页 + 导出; 状态列支持复判工作流(待复判/已确认/误报);',
        '⑤ 右栏: 缺陷详情与复判 —— 大图 + 信息 + 更改类型(现有 ResultEditWidget 升级) +',
        '   "上一个/下一个"快速翻检 + "标记误报"(误报样本可回流用于模型再训练)。'])
    note(p, 1960, 410, 560, 250, '复判工作流 (新增)', [
        '· 质检员登录后, "待复判"缺陷进入队列;',
        '· 右栏逐个查看: 确认 → 自动跳下一个; 误报 → 标记并可选填原因;',
        '· 误报样本自动归档到 output/{批次}/{距离}/{通道}/, 供算法迭代;',
        '· 权限: 仅 管理员/经理 可修改缺陷类型, 工人只读。'])
    return p


# =========================================================
# 页 5: 设备设置
# =========================================================
def page_device():
    p = Page('5. 设备设置', 2560, 1220)
    shell(p, active=2)

    p.add('设备设置', txt(TXT, 19, 'left', bold=True), 200, 62, 200, 30)
    p.add('硬件连接与参数配置 · 需管理员/经理权限', txt(TXT2, 12, 'left'), 320, 70, 400, 22)
    button(p, 1640, 64, 120, 36, '恢复默认', 'outline', size=13)
    button(p, 1772, 64, 136, 36, '保存配置', 'primary', size=13)

    # ---- 相机设置(大卡) ----
    p.add('', rect(CARD, BORDER, arc=8), 200, 112, 1708, 330)
    p.add('相机设置 (4 路检测通道)', txt(TXT, 14, 'left', bold=True), 216, 122, 400, 24)
    p.add('读取模式切换后需点击"保存配置"并重启相机生效', txt(TXT2, 11, 'left'), 560, 126, 500, 20)
    table(p, 216, 156, [90, 220, 430, 170, 190, 140, 130, 260],
          ['通道', '读取模式', '设备 / 信号源', '曝光时间(µs)', '触发模式', '状态', '启用', '操作'],
          [['通道1', '海康威视 ▾', 'MV-CS050-10UM (00A1B2) ▾', '2000', '连续采集 ▾', ('● 已连接', GREEN), '开', '[ 预览 ] [ 试拍 ]'],
           ['通道2', '海康威视 ▾', 'MV-CS050-10UM (00C3D4) ▾', '2000', '频闪触发 ▾', ('● 已连接', GREEN), '开', '[ 预览 ] [ 试拍 ]'],
           ['通道3', '海康威视 ▾', '(未选择设备) ▾', '2000', '连续采集 ▾', ('● 已断开', RED), '开', '[ 重新连接 ]'],
           ['通道4', '视频文件 ▾', 'D:\\samples\\line_demo.mp4', '—', '—', ('● 就绪', TXT2), '关', '[ 预览 ]']],
          row_h=44, header_h=34)
    p.add('支持模式: 海康威视(生产) / USB摄像头 / 视频文件(演示) / 静态图片(调试)',
          txt(TXT2, 11, 'left'), 216, 396, 800, 20)

    # ---- 下方 2×2 卡片 ----
    # 光源
    p.add('', rect(CARD, BORDER, arc=8), 200, 456, 848, 280)
    p.add('光源控制器', txt(TXT, 14, 'left', bold=True), 216, 466, 200, 24)
    chip(p, 360, 466, '已连接 COM5', 'ok')
    form_row(p, 216, 506, '串口端口', control='combo', value='COM5')
    form_row(p, 216, 542, '波特率', control='combo', value='19200')
    p.add('', rect(BORDER, BORDER, arc=50), 216, 578, 816, 1)
    p.add('四路亮度', txt(TXT2, 12, 'left'), 216, 588, 100, 22)
    for i, val in enumerate([75, 128, 128, 60]):
        sx = 216 + i * 208
        p.add(f'通道{chr(65 + i)}', txt(TXT2, 11, 'left'), sx, 614, 60, 20)
        p.add(str(val), txt(ACCENT, 12, 'right', bold=True), sx + 140, 614, 50, 20)
        p.add('', rect('#3A4152', 'none', arc=50), sx, 640, 190, 5)
        p.add('', rect(ACCENT, 'none', arc=50), sx, 640, 190 * val / 255, 5)
        p.add('', f'ellipse;fillColor={ACCENT};strokeColor=#FFFFFF;', sx + 190 * val / 255 - 7, 634, 14, 14)
    p.add('曝光批次分组 (同组相机同时频闪)', txt(TXT2, 12, 'left'), 216, 664, 300, 22)
    p.add('', rect(CARD2, BORDER, arc=50), 216, 690, 190, 26)
    p.add('批次1: 相机1 · 相机2', txt(TXT, 11, 'center'), 216, 690, 190, 26)
    p.add('', rect(CARD2, BORDER, arc=50), 416, 690, 190, 26)
    p.add('批次2: 相机3 · 相机4', txt(TXT, 11, 'center'), 416, 690, 190, 26)
    button(p, 880, 688, 150, 30, '编辑分组', 'outline', size=12)

    # 计米轮
    p.add('', rect(CARD, BORDER, arc=8), 1060, 456, 848, 280)
    p.add('计米轮 (测速编码器)', txt(TXT, 14, 'left', bold=True), 1076, 466, 260, 24)
    chip(p, 1300, 466, '已连接 COM3', 'ok')
    form_row(p, 1076, 506, '串口端口', control='combo', value='COM3')
    form_row(p, 1076, 542, '波特率', control='combo', value='9600')
    form_row(p, 1076, 578, '单圈周长', control='input', value='200 mm')
    p.add('计数方向', txt(TXT2, 13, 'left'), 1076, 614, 240, 32)
    toggle(p, 1380, 619, on=False, label='反向计数', lab_color=TXT2)
    p.add('', rect(BORDER, BORDER, arc=50), 1076, 656, 816, 1)
    p.add('实时: 速度 12.35 m/s · 累计 1523.45 m', txt(TEAL, 12, 'left'), 1076, 668, 400, 22)
    button(p, 1620, 692, 120, 32, '累计清零', 'outline', size=12)
    button(p, 1748, 692, 136, 32, '读取测试', 'ghost', size=12)

    # 放电检测
    p.add('', rect(CARD, BORDER, arc=8), 200, 748, 848, 280)
    p.add('放电检测 (针孔)', txt(TXT, 14, 'left', bold=True), 216, 758, 220, 24)
    chip(p, 400, 758, '未启用', 'off')
    form_row(p, 216, 798, '串口端口', control='combo', value='COM17')
    form_row(p, 216, 834, '波特率', control='combo', value='115200')
    form_row(p, 216, 870, '去抖窗口', control='input', value='0.30 s')
    p.add('启用放电检测', txt(TXT2, 13, 'left'), 216, 908, 240, 32)
    toggle(p, 560, 913, on=False)
    p.add('触发路径: ① 串口 JSON 流  ② IO卡 ch0 硬件中断 (更快)',
          txt(TXT2, 11, 'left'), 216, 950, 700, 20)
    p.add('放电触发后生成固定缺陷类型"针孔缺陷", 显示在泳道第 5 道(橙色)',
          txt(ORANGE, 11, 'left'), 216, 972, 700, 20)

    # IO 卡与报警
    p.add('', rect(CARD, BORDER, arc=8), 1060, 748, 848, 280)
    p.add('IO 卡与报警输出', txt(TXT, 14, 'left', bold=True), 1076, 758, 220, 24)
    chip(p, 1270, 758, '正常', 'ok')
    form_row(p, 1076, 798, '报警输出通道', control='combo', value='ch4')
    form_row(p, 1076, 834, '报警持续时间', control='input', value='3.0 s')
    form_row(p, 1076, 870, '连续缺陷节流间隔', control='input', value='3.0 s')
    p.add('', rect(BORDER, BORDER, arc=50), 1076, 908, 816, 1)
    p.add('输入  IN0', txt(TXT2, 11, 'left'), 1076, 920, 70, 20)
    for i in range(8):
        c = RED if i == 0 else '#3A4152'
        p.add('', f'ellipse;fillColor={c};strokeColor={BORDER};', 1150 + i * 26, 920, 16, 16)
    p.add('输出 OUT0', txt(TXT2, 11, 'left'), 1076, 950, 70, 20)
    for i in range(8):
        c = GREEN if i == 4 else '#3A4152'
        p.add('', f'ellipse;fillColor={c};strokeColor={BORDER};', 1150 + i * 26, 950, 16, 16)
    p.add('IN0=放电中断(红闪) · OUT4=声光报警(触发时亮绿)', txt(TXT2, 10.5, 'left'), 1400, 936, 500, 20)
    button(p, 1768, 968, 116, 32, 'IO 自检', 'outline', size=12)

    note(p, 1960, 48, 560, 300, '设备设置页设计说明', [
        '① 相机大卡: 4 通道一表管 —— 读取模式/设备/曝光/触发模式/状态/启用/操作;',
        '   覆盖现有 CameraSettingInterface 的全部功能并补充触发模式与试拍预览;',
        '② 光源卡: 串口参数 + 4 路亮度滑条(现有只有单一亮度) + 曝光批次分组可视化;',
        '③ 计米轮卡: 现有 VSamplerSettingInterface 参数 + 实时读数 + 累计清零;',
        '④ 放电卡: 补全现有空壳的 LightningSettingInterface, 暴露去抖窗口与启用开关;',
        '⑤ IO卡报警: 新增 —— 报警通道/时长/节流(来自 config 的 IOCard 配置), IO 状态灯。'])
    note(p, 1960, 380, 560, 260, '交互规则', [
        '· 所有修改进入"待保存"状态, 顶部出现黄色提示条"有未保存的修改";',
        '· "保存配置"写入 config/config.json(沿用现有 Config 结构);',
        '· 串口被占用/连接失败 → 状态芯片变红并弹窗给出具体端口错误;',
        '· "预览"打开通道实时画面弹窗(复用图像组件); "试拍"抓取单帧存 output/debug/;',
        '· 权限: 设备设置页仅 管理员/经理 可编辑, 工人进入为只读。'])
    return p


# =========================================================
# 页 6: 系统设置
# =========================================================
def page_system():
    p = Page('6. 系统设置', 2560, 1220)
    shell(p, active=3)

    # 左侧子导航
    p.add('', rect(CARD, BORDER, arc=8), 200, 60, 190, 972)
    subs = ['算法设置', '透视矫正', '用户管理', '关于系统']
    for i, s in enumerate(subs):
        sy = 76 + i * 48
        if i == 0:
            p.add('', rect('#262B38', 'none', arc=8), 208, sy, 174, 40)
            p.add('', rect(ACCENT, 'none', arc=50), 208, sy, 4, 40)
        p.add(s, txt(TXT if i == 0 else TXT2, 13, 'left', bold=(i == 0)), 226, sy, 150, 40)

    # ---- 算法设置 ----
    p.add('', rect(CARD, BORDER, arc=8), 406, 60, 1502, 190)
    p.add('检测算法', txt(TXT, 14, 'left', bold=True), 422, 70, 200, 24)
    p.add('', f'ellipse;fillColor={ACCENT};strokeColor=none;', 422, 108, 16, 16)
    p.add('YOLO 深度学习检测 (推荐 · 引擎: OpenVINO/ONNX)', txt(TXT, 13, 'left'), 448, 100, 420, 30)
    p.add('', 'ellipse;fillColor=none;strokeColor=#4A5162;', 422, 142, 16, 16)
    p.add('传统算法 (FFT去纹理 + 梯度特征 + 轮廓分析)', txt(TXT2, 13, 'left'), 448, 134, 420, 30)
    p.add('置信度阈值', txt(TXT2, 13, 'left'), 950, 100, 120, 26)
    p.add('', rect('#3A4152', 'none', arc=50), 1080, 112, 360, 5)
    p.add('', rect(ACCENT, 'none', arc=50), 1080, 112, 216, 5)
    p.add('', f'ellipse;fillColor={ACCENT};strokeColor=#FFFFFF;', 1288, 106, 16, 16)
    p.add('0.60', txt(ACCENT, 14, 'left', bold=True), 1456, 100, 70, 26)
    p.add('阈值越低 → 召回越高、误报越多; 修改后即时生效', txt(TXT2, 11, 'left'), 950, 140, 560, 20)
    p.add('当前模型: yolo_openvino_model (4类: 汽包/粒子/漆瘤/毛粘线)',
          txt(TXT2, 12, 'left'), 950, 190, 600, 22)
    p.add('', rect(YELLOW, YELLOW, arc=50), 1600, 196, 8, 8)
    p.add('算法切换仅管理员可用', txt(YELLOW, 11, 'left'), 1614, 188, 240, 22)

    # ---- 图像预处理 ----
    p.add('', rect(CARD, BORDER, arc=8), 406, 262, 742, 170)
    p.add('图像预处理', txt(TXT, 14, 'left', bold=True), 422, 272, 200, 24)
    form_row(p, 422, 312, 'CLAHE 对比度限制', w=340, control='input', value='3.0', cw=120)
    form_row(p, 422, 348, 'CLAHE 分块大小', w=340, control='input', value='8 × 8', cw=120)
    form_row(p, 422, 384, '检测 ROI 高度比例', w=340, control='input', value='1/3 (中部)', cw=120)
    p.add('预处理顺序: 透视矫正 → CLAHE 增强 → ROI 裁剪 → 送检',
          txt(TXT2, 11, 'left'), 790, 320, 340, 40)

    # ---- 透视矫正入口 ----
    p.add('', rect(CARD, BORDER, arc=8), 1162, 262, 746, 170)
    p.add('透视矫正 (仿射变换)', txt(TXT, 14, 'left', bold=True), 1178, 272, 300, 24)
    p.add('每通道 4 参数: top_lower / top_upper / bottom_lower / bottom_upper',
          txt(TXT2, 12, 'left'), 1178, 306, 600, 22)
    p.add('在实时画面上拖拽两条红色引导线, 将梯形漆包线区域矫正为矩形',
          txt(TXT2, 12, 'left'), 1178, 332, 600, 22)
    button(p, 1178, 376, 180, 36, '打开矫正工具', 'primary', size=13)
    p.add('(弹窗见 P7)', txt(TXT2, 11, 'left'), 1374, 384, 150, 20)

    # ---- 通道与缺陷类型 ----
    p.add('', rect(CARD, BORDER, arc=8), 406, 444, 1502, 200)
    p.add('通道启用与缺陷类型', txt(TXT, 14, 'left', bold=True), 422, 454, 300, 24)
    table(p, 422, 488, [150, 200, 220, 220, 220, 220, 220],
          ['通道', '检测启用', '汽泡', '粒子', '漆瘤', '毛粘线', '针孔(放电)'],
          [['通道1 · 左面', ('☑ 启用', GREEN), '☑', '☑', '☑', '☑', '☑'],
           ['通道2 · 上面', ('☑ 启用', GREEN), '☑', '☑', '☑', '☑', '—'],
           ['通道3 · 右面', ('☐ 禁用', RED), '—', '—', '—', '—', '—'],
           ['通道4 · 下面', ('☑ 启用', GREEN), '☑', '☑', '☑', '☑', '—']],
          row_h=30, header_h=32)

    # ---- 用户管理 ----
    p.add('', rect(CARD, BORDER, arc=8), 406, 656, 1502, 376)
    p.add('用户管理', txt(TXT, 14, 'left', bold=True), 422, 666, 200, 24)
    button(p, 1764, 664, 128, 32, '+ 创建用户', 'primary', size=12)
    table(p, 422, 708, [260, 260, 320, 320, 310],
          ['用户名', '角色', '创建时间', '最近登录', '操作'],
          [['admin', ('管理员', ACCENT), '2026-01-05', '2026-08-29 08:15', '[ 重置密码 ]'],
           ['张三', ('工人', TXT2), '2026-03-12', '2026-08-29 08:20', '[ 重置密码 ] [ 禁用 ]'],
           ['李四', ('工人', TXT2), '2026-03-12', '2026-08-28 14:10', '[ 重置密码 ] [ 禁用 ]'],
           ['王五', ('经理', TEAL), '2026-02-20', '2026-08-27 22:05', '[ 重置密码 ] [ 禁用 ]']],
          row_h=36, header_h=34)
    p.add('角色权限: 管理员=全部 · 经理=批次/复判/设备设置 · 工人=检测操作与批次添加(沿用现有 Role 枚举)',
          txt(TXT2, 11, 'left'), 422, 990, 1300, 20)

    note(p, 1960, 48, 560, 300, '系统设置页设计说明', [
        '① 页内子导航: 算法设置 / 透视矫正 / 用户管理 / 关于系统;',
        '② 算法设置: YOLO↔传统算法切换(现有为环境变量控制, 升级为界面开关) + 置信度阈值滑条;',
        '③ 图像预处理: CLAHE 与 ROI 参数(来自 mixin_prepare)可视化配置;',
        '④ 透视矫正入口: 打开现有 AffineTransformWidget 升级版弹窗;',
        '⑤ 通道启用与缺陷类型: 对应 ModelConfig.enable, 并可按通道选择关注的缺陷类型;',
        '⑥ 用户管理: 现有数据库界面的管理员功能升级为正式表格管理。'])
    note(p, 1960, 380, 560, 240, '型号(配方)管理 — 建议放入"关于系统"之上', [
        '· 现有 ModelSettingWidget(型号下拉/添加型号/使用配置/保存配置)',
        '  建议升级为独立子页"型号管理": 型号列表 + 复制/删除/导出;',
        '· 型号内容沿用: rectification / mapper / enable / exposureBatch;',
        '· 检测页顶部信息条的"型号"点击后快速切换型号。'])
    return p


# =========================================================
# 页 7: 弹窗与登录
# =========================================================
def page_dialogs():
    p = Page('7. 弹窗与登录', 2200, 1260)

    # ---------- 登录 ----------
    p.add('', rect(BG, BORDER, arc=6, w=2), 60, 80, 420, 540)
    p.add('', rect(ACCENT, 'none', arc=22), 236, 116, 68, 68)
    p.add('OS', txt('#FFFFFF', 22, 'center', bold=True), 236, 116, 68, 68)
    p.add('漆包线表面缺陷检测系统', txt(TXT, 17, 'center', bold=True), 80, 198, 380, 26)
    p.add('请登录以继续', txt(TXT2, 12, 'center'), 80, 228, 380, 20)
    p.add('用户', txt(TXT2, 12, 'left'), 100, 268, 100, 20)
    input_box(p, 100, 292, 340, 38, '张三 ▾  (下拉选择)')
    p.add('密码', txt(TXT2, 12, 'left'), 100, 344, 100, 20)
    input_box(p, 100, 368, 340, 38, '●●●●●●●●')
    toggle(p, 100, 428, on=True, label='记住我', lab_color=TXT2)
    button(p, 100, 470, 340, 44, '登  录', 'primary', size=15)
    p.add('忘记密码请联系管理员', txt(TXT2, 11, 'center'), 100, 528, 340, 18)
    note(p, 60, 646, 420, 170, '登录弹窗', [
        '· 程序启动时弹出(现有登录在"数据库"页, 升级为启动即登录);',
        '· 用户下拉沿用 UsersComboBox; 登录成功进入实时检测页;',
        '· 角色决定可用菜单: 工人不可见"设备设置/系统设置"。'])

    # ---------- 更换批次确认 ----------
    p.add('', rect(BG, BORDER, arc=6, w=2), 540, 80, 440, 300)
    p.add('更换批次确认', txt(TXT, 15, 'left', bold=True), 564, 100, 300, 24)
    p.add('', rect(CARD2, BORDER, arc=6), 564, 136, 392, 84)
    p.add('当前批次: 20260829-A  ·  负责人: 张三', txt(TXT2, 12, 'left'), 580, 148, 360, 22)
    p.add('新  批  次: 20260829-B  ·  负责人: 李四', txt(TXT, 12, 'left', bold=True), 580, 178, 360, 22)
    p.add('⚠ 更换后, 缺陷计数与批次长度将重新累计, 缺陷保存至新批次目录',
          txt(YELLOW, 11.5, 'left'), 564, 236, 392, 34)
    button(p, 660, 296, 150, 40, '取消', 'outline', size=13)
    button(p, 824, 296, 150, 40, '确认更换', 'primary', size=13)
    note(p, 540, 406, 440, 130, '更换批次弹窗', [
        '· 顶部信息条点击"批次"打开: 输入新批次 + 选择负责人;',
        '· 沿用现有 swapBatch 逻辑与空名拦截。'])

    # ---------- 告警 ----------
    p.add('', rect(BG, RED, arc=6, w=2), 540, 566, 440, 210)
    p.add('', rect('#3A1A1C', 'none', arc=50), 564, 588, 44, 44)
    p.add('⚠', txt(RED, 20, 'center', bold=True), 564, 588, 44, 44)
    p.add('缺陷告警', txt(TXT, 15, 'left', bold=True), 622, 590, 200, 24)
    p.add('位置 856.12 m 处检出缺陷: 汽泡 (通道1)', txt(TXT, 13, 'left'), 622, 618, 340, 22)
    p.add('IO 报警输出已触发 (ch4 · 3 秒)', txt(TXT2, 12, 'left'), 564, 660, 380, 22)
    button(p, 800, 700, 156, 40, '知道了', 'danger', size=13)
    note(p, 1040, 1040, 900, 150, '告警弹窗 (可配置)', [
        '· 仅在"告警弹窗开关"开启时出现(默认关闭, 避免产线频繁打扰);',
        '· 声音提示可选; 告警历史进入"告警记录"(二期)。'])

    # ---------- 缺陷复判 ----------
    p.add('', rect(BG, BORDER, arc=6, w=2), 1040, 80, 900, 560)
    p.add('缺陷复判 — 20260828-B · 12.35 m · 通道1', txt(TXT, 15, 'left', bold=True), 1064, 96, 600, 24)
    p.add('✕', txt(TXT2, 14, 'center'), 1900, 94, 28, 28)
    p.add('', rect(IMAGE, BORDER, arc=4), 1064, 130, 520, 430)
    p.add('', rect('#3C4150', 'none', arc=0), 1064, 320, 520, 56)
    p.add('', rect('none', RED, arc=0, w=2), 1280, 290, 96, 96)
    p.add('', rect(RED, 'none', arc=10), 1280, 270, 118, 17)
    p.add('汽泡 0.93', txt('#FFFFFF', 10.5, 'center'), 1280, 270, 118, 17)
    p.add('图像上点击缺陷框可选中', txt(TXT2, 11, 'center'), 1064, 572, 520, 18)
    p.add('缺陷列表', txt(TXT, 13, 'left', bold=True), 1604, 130, 200, 22)
    p.add('', rect(CARD2, BORDER, arc=0), 1604, 158, 316, 30)
    p.add('0: 汽泡 (选中)', txt(TXT, 12, 'left'), 1614, 158, 296, 30)
    p.add('', rect(ROWALT, BORDER, arc=0), 1604, 188, 316, 30)
    p.add('1: 粒子', txt(TXT2, 12, 'left'), 1614, 188, 296, 30)
    p.add('更改类型为', txt(TXT2, 12, 'left'), 1604, 240, 200, 22)
    input_box(p, 1604, 266, 316, 34, '汽泡 ▾  (可编辑, 支持新增)')
    button(p, 1604, 316, 316, 40, '应用修改', 'primary', size=13)
    button(p, 1604, 366, 316, 36, '标记为误报', 'outline', size=12)
    p.add('', rect(BORDER, BORDER, arc=50), 1604, 416, 316, 1)
    p.add('选中: 汽泡 [214, 96, 88, 88]\n修改将写入 fault.json 并刷新图像',
          txt(TXT2, 11.5, 'left', valign='top'), 1604, 428, 316, 60)
    button(p, 1604, 508, 150, 38, '◀ 上一个', 'outline', size=12)
    button(p, 1770, 508, 150, 38, '下一个 ▶', 'outline', size=12)
    note(p, 1040, 666, 900, 120, '缺陷复判弹窗', [
        '· 由历史记录表"复判/详情"、实时列表点击打开; 是现有 ResultEditWidget 的升级版(加误报标记与翻页);',
        '· 左侧大图支持滚轮缩放(建议新增), 右侧列表与图像选中联动。'])

    # ---------- 透视矫正 ----------
    p.add('', rect(BG, BORDER, arc=6, w=2), 60, 850, 900, 360)
    p.add('透视矫正 (仿射变换)', txt(TXT, 15, 'left', bold=True), 84, 866, 300, 24)
    segment(p, 420, 864, ['通道1', '通道2', '通道3', '通道4'], 0, w_item=84, h=28)
    p.add('✕', txt(TXT2, 14, 'center'), 920, 864, 28, 28)
    p.add('上边界', txt(TXT2, 11, 'left'), 84, 904, 60, 20)
    p.add('', rect('#3A4152', 'none', arc=50), 150, 912, 720, 5)
    p.add('', f'ellipse;fillColor={ACCENT};strokeColor=#FFFFFF;', 300, 906, 14, 14)
    p.add('', f'ellipse;fillColor={ACCENT};strokeColor=#FFFFFF;', 660, 906, 14, 14)
    p.add('', rect(IMAGE, BORDER, arc=4), 84, 930, 792, 180)
    p.add('', rect('#3C4150', 'none', arc=0), 84, 1000, 792, 44)
    # 两条红色引导线(用旋转矩形模拟): 左上(307,936)↔左下(347,1104); 右上(667,936)↔右下(627,1104)
    p.add('', f'{F}rounded=0;whiteSpace=wrap;html=0;fillColor={RED};strokeColor=none;rotation=76.6;',
          327 - 86.5, 1020 - 1, 173, 2.5)
    p.add('', f'{F}rounded=0;whiteSpace=wrap;html=0;fillColor={RED};strokeColor=none;rotation=-76.6;',
          647 - 86.5, 1020 - 1, 173, 2.5)
    p.add('红色引导线: 上线两端点 ↔ 下线两端点, 共 4 参数', txt(ORANGE, 11, 'center'), 84, 1080, 792, 18)
    p.add('下边界', txt(TXT2, 11, 'left'), 84, 1122, 60, 20)
    p.add('', rect('#3A4152', 'none', arc=50), 150, 1130, 720, 5)
    p.add('', f'ellipse;fillColor={ACCENT};strokeColor=#FFFFFF;', 340, 1124, 14, 14)
    p.add('', f'ellipse;fillColor={ACCENT};strokeColor=#FFFFFF;', 620, 1124, 14, 14)
    button(p, 660, 1156, 100, 36, '返回', 'outline', size=13)
    button(p, 772, 1156, 164, 36, '应用矫正参数', 'primary', size=13)
    note(p, 1040, 850, 900, 160, '透视矫正弹窗', [
        '· 现有 AffineTransformWidget 的交互升级: 滑块改为画布上直接拖拽 4 个端点;',
        '· 红色引导线实时叠加在相机画面上; 每通道独立参数, 保存到型号配置 rectification;',
        '· "应用矫正参数"写入当前型号 JSON。'])
    return p


# =========================================================
PAGES = [page_spec, page_shell, page_realtime, page_history, page_device, page_system, page_dialogs]


def main():
    out = io.StringIO()
    out.write('<mxfile host="app.diagrams.net" version="24.7.17" type="device">')
    for i, fn in enumerate(PAGES, start=1):
        out.write(fn().xml(i))
    out.write('</mxfile>')
    with open('UI重设计_视觉检测软件.drawio', 'w', encoding='utf-8') as f:
        f.write(out.getvalue())
    print('OK -> UI重设计_视觉检测软件.drawio')


if __name__ == '__main__':
    main()

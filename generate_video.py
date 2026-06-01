"""
防范养老诈骗短视频 — 大字流风格
人保财险湄潭支公司
45秒 | 1080×1920 (9:16竖屏)
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v3 as iio
import os

# ── 配置 ──────────────────────────────
W, H = 1080, 1920
FPS = 24
TOTAL_SEC = 45
OUTPUT = os.path.join(os.path.dirname(__file__), "防范养老诈骗_人保财险湄潭支公司.mp4")

BG = (18, 18, 22)          # 深色背景
WHITE = (255, 255, 255)
RED = (255, 60, 60)
YELLOW = (255, 200, 20)
GOLD = (255, 180, 40)
GRAY = (150, 150, 150)
LIGHT_GRAY = (180, 180, 180)
GREEN = (80, 230, 120)
BLUE = (70, 150, 255)
PICC_RED = (200, 30, 40)  # 人保红

# 字体
FONT_BOLD = None
FONT_REGULAR = None
FONT_LIGHT = None

def find_font(size, bold=False):
    """Windows找字体"""
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttf",   # 微软雅黑粗体
        "C:/Windows/Fonts/msyh.ttf",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",    # 黑体
        "C:/Windows/Fonts/simsun.ttc",    # 宋体
        "C:/Windows/Fonts/simkai.ttf",    # 楷体
    ]
    for f in candidates:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except:
                continue
    return ImageFont.load_default()


def draw_centered_text(draw, text, y, font, color=WHITE, max_w=None):
    """居中绘制文字，返回绘制的bottom y"""
    if max_w is None:
        max_w = W - 120
    # 简单换行
    lines = []
    for para in text.split('\n'):
        if not para:
            lines.append('')
            continue
        chars = list(para)
        line = ''
        for c in chars:
            test = line + c
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_w:
                lines.append(line)
                line = c
            else:
                line = test
        if line:
            lines.append(line)

    line_h = font.size + 10
    total_h = len(lines) * line_h
    start_y = y - total_h // 2

    for i, line in enumerate(lines):
        if not line:
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, start_y + i * line_h), line, font=font, fill=color)

    return start_y + total_h


def draw_multiline(draw, lines_data, start_y, line_spacing=0):
    """
    lines_data: [(text, font, color), ...]
    返回 bottom y
    """
    y = start_y
    for text, font, color in lines_data:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), text, font=font, fill=color)
        y += font.size + line_spacing
    return y


def make_frame():
    return Image.new("RGB", (W, H), BG)


def draw_chat_bubble(draw, text, y, side='left', color=(60,60,65), text_color=WHITE, font=None, max_w=600):
    """画聊天气泡"""
    if font is None:
        font = FONT_REGULAR
    # 计算文字尺寸
    lines = []
    chars = list(text)
    line = ''
    for c in chars:
        test = line + c
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_w - 40:
            lines.append(line)
            line = c
        else:
            line = test
    if line:
        lines.append(line)

    line_h = font.size + 8
    bubble_h = len(lines) * line_h + 40
    bubble_w = min(max_w, max(draw.textbbox((0,0), l, font=font)[2] for l in lines) + 60)

    # 气泡位置
    if side == 'left':
        bx, by = 60, y
        triangle = [(bx + bubble_w, by + bubble_h//2 - 10),
                     (bx + bubble_w + 16, by + bubble_h//2),
                     (bx + bubble_w, by + bubble_h//2 + 10)]
    else:  # right
        bx = W - 60 - bubble_w
        by = y
        triangle = [(bx, by + bubble_h//2 - 10),
                     (bx - 16, by + bubble_h//2),
                     (bx, by + bubble_h//2 + 10)]

    # 圆角矩形
    r = 20
    draw.rounded_rectangle([bx, by, bx + bubble_w, by + bubble_h], radius=r, fill=color)
    draw.polygon(triangle, fill=color)

    # 文字
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        tx = bx + (bubble_w - tw) // 2
        ty = by + 20 + i * line_h
        draw.text((tx, ty), line, font=font, fill=text_color)

    return by + bubble_h + 10


# ── 初始化字体 ────────────────────────
FONT_BOLD = find_font(52, bold=True)
FONT_BIG = find_font(72, bold=True)
FONT_HUGE = find_font(96, bold=True)
FONT_REGULAR = find_font(40)
FONT_SMALL = find_font(32)
FONT_TINY = find_font(26)

print("字体加载完成，开始渲染...")

# ── 帧缓冲 ────────────────────────────
total_frames = TOTAL_SEC * FPS
frames = []

def add_scene(img, duration_sec):
    """将一帧画面持续duration_sec秒"""
    n = int(duration_sec * FPS)
    for _ in range(n):
        frames.append(img.copy())

def add_scene_with_fade(img1, img2, duration_sec):
    """从img1渐变到img2"""
    n = int(duration_sec * FPS)
    for i in range(n):
        alpha = i / n
        blended = Image.blend(img1.convert("RGBA"), img2.convert("RGBA"), alpha).convert("RGB")
        frames.append(blended)

# ═══════════════════════════════════════
# 场景 1 (0-3s): 标题
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)

# 顶部品牌条
draw.rectangle([0, 0, W, 120], fill=(160, 20, 30))
draw.text((60, 30), "人保财险湄潭支公司", font=FONT_SMALL, fill=WHITE)
draw.text((60, 72), "PICC", font=find_font(22), fill=LIGHT_GRAY)

# 大标题
draw_centered_text(draw, "防范养老诈骗", H//2 - 160, FONT_HUGE, GOLD)
draw_centered_text(draw, "守住爸妈的养老钱", H//2 + 20, FONT_BOLD, WHITE)

# 底部警示线
draw.rectangle([200, H//2 + 140, W-200, H//2 + 146], fill=PICC_RED)

# 底部字幕
draw_centered_text(draw, "转发给父母 · 多一人看到 少一人被骗", H - 200, FONT_SMALL, GRAY)

add_scene(img, 3.0)

# ═══════════════════════════════════════
# 场景 2 (3-7s): 对话开始
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)
# 标题条
draw.rectangle([0, 0, W, 100], fill=(30, 30, 38))
draw_centered_text(draw, "👤 儿子  ·  👵 母亲", H - 1850, FONT_TINY, LIGHT_GRAY)

y = 200
y = draw_chat_bubble(draw, "妈，看啥呢这么认真？", y, 'right', text_color=WHITE, font=FONT_REGULAR, color=(60, 100, 200))
y += 10
y = draw_chat_bubble(draw, "小王老师拉我进了一个\n养生群～说是专门给\n我们老年人的福利！", y, 'left', font=FONT_REGULAR)

add_scene(img, 4.0)

# ═══════════════════════════════════════
# 场景 3 (7-13s): 群聊截图 + 高额返利
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, W, 100], fill=(160, 20, 30))
draw.text((60, 30), "⚠ 高风险预警", font=FONT_SMALL, fill=WHITE)

# 群聊消息模拟
y = 200
messages = [
    ("恭喜张阿姨投了5万\n当天分红800元！💰", 'left', (240, 240, 245)),
    ("太划算了！我也追加了3万", 'left', (240, 240, 245)),
    ("名额有限仅剩最后7个！", 'left', (255, 230, 230)),
    ("投1万 每月返2000\n年化收益240%", 'left', (255, 220, 220)),
]
for msg, side, bg in messages:
    y = draw_chat_bubble(draw, msg, y, side, color=bg, font=FONT_REGULAR) + 6

# 红色警示大文字
draw_centered_text(draw, "投1万 每月返2000", H - 520, FONT_BIG, RED)
draw.line([(200, H-400), (W-200, H-400)], fill=RED, width=4)
draw_centered_text(draw, "年化240% = 非法集资", H - 350, FONT_BOLD, YELLOW)

add_scene(img, 6.0)

# ═══════════════════════════════════════
# 场景 4 (13-18s): 儿子警觉
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, W, 100], fill=(30, 30, 38))
draw_centered_text(draw, "儿子发现不对劲...", H - 1850, FONT_TINY, GRAY)

draw_centered_text(draw, "妈，你等一下。", H//2 - 80, FONT_BIG, WHITE)
draw_centered_text(draw, "让我查一下这个平台...", H//2 + 30, FONT_REGULAR, LIGHT_GRAY)

# 搜索动画模拟
draw.rounded_rectangle([120, H//2+160, W-120, H//2+240], radius=16, fill=(40,40,50), outline=(80,80,90), width=2)
draw.text((170, H//2 + 175), "🔍 正在查询企业信息...", font=FONT_SMALL, fill=GRAY)

add_scene(img, 5.0)

# ═══════════════════════════════════════
# 场景 5 (18-25s): 查询结果 · 已立案
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)

# 大红横幅
draw.rectangle([0, 0, W, 160], fill=(180, 20, 30))
draw_centered_text(draw, "⚠ 该平台已被立案调查", 80, FONT_BIG, WHITE)

# 搜索结果模拟框
y = 280
box_h = 600
draw.rounded_rectangle([80, y, W-80, y+box_h], radius=20, fill=(35, 35, 42), outline=(70, 70, 78), width=2)

lines_data = [
    ("【风险提示】", FONT_BOLD, RED),
    ("", FONT_REGULAR, WHITE),
    ("该平台涉嫌非法吸收公众存款", FONT_REGULAR, WHITE),
    ("已被公安机关立案侦查", FONT_REGULAR, WHITE),
    ("", FONT_REGULAR, WHITE),
    ("涉及受害老人：300+人", FONT_BOLD, YELLOW),
    ("涉案金额：最高单人损失38万元", FONT_BOLD, RED),
    ("", FONT_REGULAR, WHITE),
    ("", FONT_REGULAR, WHITE),
    ("请勿向该平台任何账户转账！", FONT_BOLD, RED),
]
draw_multiline(draw, lines_data, y + 40, line_spacing=4)

# 底部大字
draw_centered_text(draw, "已立案  ·  300+老人被骗", H - 300, FONT_BOLD, RED)

add_scene(img, 7.0)

# ═══════════════════════════════════════
# 场景 6 (25-29s): 幸好没投
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)

draw_centered_text(draw, "妈：那我还没投……", H//2 - 180, FONT_BIG, GRAY)
draw_centered_text(draw, "儿子：", H//2 - 40, FONT_BIG, WHITE)
draw_centered_text(draw, "还没投就对了！", H//2 + 60, FONT_HUGE, GREEN)

# 握手表意
draw_centered_text(draw, "🤝", H//2 + 220, FONT_BIG, WHITE)

add_scene(img, 4.0)

# ═══════════════════════════════════════
# 场景 7 (29-36s): 三个凡是
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)

draw.rectangle([0, 0, W, 120], fill=PICC_RED)
draw.text((60, 30), "人保财险湄潭支公司 · 防范非法金融宣传", font=FONT_TINY, fill=WHITE)

draw_centered_text(draw, "三个凡是", H//2 - 500, FONT_HUGE, GOLD)
draw.line([(250, H//2-400), (W-250, H//2-400)], fill=GOLD, width=3)

rules = [
    ("凡是", "拉你进群、推荐理财项目的", RED),
    ("凡是", "承诺高额返利、稳赚不赔的", RED),
    ("凡是", "让你转账到个人账户的", RED),
]

y = H//2 - 280
for prefix, text, color in rules:
    # 圆角卡片
    draw.rounded_rectangle([100, y, W-100, y+130], radius=18, fill=(40, 40, 48), outline=(70, 70, 78), width=1)
    # 红色"凡是"
    draw.text((150, y+15), prefix, font=FONT_BOLD, fill=color)
    # 文字
    tw = draw.textbbox((0, 0), text, font=FONT_REGULAR)[2]
    draw.text((150+120, y+15), text, font=FONT_REGULAR, fill=WHITE)
    y += 160

# 底部
draw_centered_text(draw, "全是骗子！", H - 380, FONT_BIG, RED)
draw_centered_text(draw, "让爸妈背下来", H - 260, FONT_SMALL, LIGHT_GRAY)

add_scene(img, 7.0)

# ═══════════════════════════════════════
# 场景 8 (36-40s): 转发
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)

draw_centered_text(draw, "妈：那我把群退了？", H//2 - 200, FONT_BIG, GRAY)
draw_centered_text(draw, "儿子：退！", H//2 - 60, FONT_HUGE, GREEN)
draw_centered_text(draw, "然后转发给你的老姐妹群。", H//2 + 80, FONT_BOLD, WHITE)
draw_centered_text(draw, "妈：发！", H//2 + 200, FONT_BIG, YELLOW)

# 转发箭头动画示意
draw_centered_text(draw, "↗ ↗ ↗", H//2 + 360, FONT_BIG, GREEN)

add_scene(img, 4.0)

# ═══════════════════════════════════════
# 场景 9 (40-45s): 片尾 · PICC品牌
# ═══════════════════════════════════════
img = make_frame()
draw = ImageDraw.Draw(img)

# 品牌红底
draw.rectangle([0, H//2 - 300, W, H], fill=PICC_RED)

# Logo区
draw_centered_text(draw, "人保财险湄潭支公司", H//2 - 200, FONT_BOLD, WHITE)
draw_centered_text(draw, "PICC", H//2 - 100, find_font(36), LIGHT_GRAY)

draw.line([(200, H//2-50), (W-200, H//2-50)], fill=WHITE, width=2)

draw_centered_text(draw, "守住爸妈的养老钱", H//2 + 30, FONT_BOLD, WHITE)
draw_centered_text(draw, "转发就是保护", H//2 + 140, FONT_BIG, GOLD)

# 警示标语
draw_centered_text(draw, "防范非法金融 人人有责", H//2 + 300, FONT_SMALL, WHITE)
draw_centered_text(draw, "举报热线：12378", H//2 + 380, FONT_TINY, LIGHT_GRAY)

add_scene(img, 5.0)

# ═══════════════════════════════════════
# 导出 MP4
# ═══════════════════════════════════════
print(f"共 {len(frames)} 帧，正在编码 MP4...")

# 用 imageio 编码（插件: pyav via imageio-ffmpeg）
# 尝试 ffmpeg 命令行, imageio 可能不行
iio.imwrite(
    OUTPUT,
    [np.array(f) for f in frames],
    fps=FPS,
    codec='h264',
    output_params=['-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p'],
)

print(f"Video generated: {OUTPUT}")
print(f"   Duration: {len(frames)/FPS:.1f}s | Resolution: {W}x{H} | FPS: {FPS}")

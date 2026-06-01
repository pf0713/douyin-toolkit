"""
Step 2: 动画版防范养老诈骗短视频
人保财险湄潭支公司
1080×1920 竖屏 | 目标45秒 | 24fps
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v3 as iio
import os, math, sys

# ── 配置 ──────────────────────────────
W, H = 1080, 1920
FPS = 24
OUT_DIR = os.path.dirname(__file__)
OUTPUT = os.path.join(OUT_DIR, "防范养老诈骗_人保财险湄潭支公司_v2.mp4")

# 颜色
BG_DARK = (22, 22, 32)
BG_CARD = (32, 34, 46)
WHITE = (255, 255, 255)
RED = (255, 55, 55)
DARK_RED = (180, 20, 30)
YELLOW = (255, 200, 30)
GOLD = (255, 185, 50)
GREEN = (80, 235, 120)
GRAY = (140, 140, 150)
LIGHT_GRAY = (190, 190, 200)
BLUE = (65, 140, 255)
PICC_RED = (195, 25, 35)

# ── 字体 ──────────────────────────────
def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttf",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for f in candidates:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except:
                continue
    return ImageFont.load_default()

FONT_HUGE = load_font(90)
FONT_BIG = load_font(64)
FONT_TITLE = load_font(52)
FONT_BODY = load_font(38)
FONT_SMALL = load_font(30)
FONT_TINY = load_font(24)

# ── 缓动函数 ──────────────────────────
def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return 3*t*t - 2*t*t*t if t < 0.5 else 1 - (-2*t + 2)**3 / 2

def ease_out_back(t):
    c1 = 1.70158
    return 1 + (c1 + 1) * (t - 1)**3 + c1 * (t - 1)**2

def bounce(t):
    if t < 1/2.75:
        return 7.5625*t*t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625*t*t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625*t*t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625*t*t + 0.984375

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    """两个颜色插值"""
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

def color_alpha(c, bg, alpha):
    """颜色叠加透明度"""
    return tuple(int(lerp(bg[i], c[i], alpha)) for i in range(3))

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ── 绘图辅助 ──────────────────────────
def draw_text_center(draw, text, y, font, color, max_w=None, alpha=1.0):
    """居中文字，支持透明度"""
    if max_w is None:
        max_w = W - 100
    if alpha >= 1.0:
        fill = color
    else:
        fill = tuple(int(lerp(BG_DARK[i], color[i], alpha)) for i in range(3))

    # 简单换行
    lines = []
    for para in text.split('\n'):
        if not para:
            lines.append('')
            continue
        line = ''
        for ch in para:
            test = line + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_w:
                lines.append(line)
                line = ch
            else:
                line = test
        if line:
            lines.append(line)

    line_h = font.size + 8
    total_h = len(lines) * line_h
    start_y = y - total_h // 2

    for i, line in enumerate(lines):
        if not line:
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, start_y + i * line_h), line, font=font, fill=fill)

    return start_y + total_h


def draw_text_left(draw, text, x, y, font, color, max_w=700):
    """左对齐文字，支持换行"""
    lines = []
    for para in text.split('\n'):
        if not para:
            lines.append('')
            continue
        line = ''
        for ch in para:
            test = line + ch
            if draw.textbbox((0, 0), test, font=font)[2] > max_w:
                lines.append(line)
                line = ch
            else:
                line = test
        if line:
            lines.append(line)
    for i, line in enumerate(lines):
        if line:
            draw.text((x, y + i * (font.size + 8)), line, font=font, fill=color)
    return y + len(lines) * (font.size + 8)


def draw_card(draw, x, y, w, h, color, radius=20, shadow=True):
    """绘制圆角卡片，带阴影"""
    if shadow:
        draw.rounded_rectangle([x+4, y+4, x+w+4, y+h+4], radius=radius, fill=(8,8,14))
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=color)


def draw_glow_text(draw, text, y, font, color, glow_color, glow_size=3):
    """带光晕的大字"""
    # glow
    for dx in range(-glow_size, glow_size+1, 2):
        for dy in range(-glow_size, glow_size+1, 2):
            if dx == 0 and dy == 0:
                continue
            draw_text_center(draw, text, y+dy, font, glow_color, alpha=0.15)
    draw_text_center(draw, text, y, font, color)


def draw_pill(draw, x, y, text, font, bg_color, text_color=WHITE):
    """药丸标签"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 20, 10
    draw.rounded_rectangle([x, y, x+tw+pad_x*2, y+th+pad_y*2], radius=th//2+pad_y, fill=bg_color)
    draw.text((x+pad_x, y+pad_y-2), text, font=font, fill=text_color)
    return x + tw + pad_x*2, y + th + pad_y*2


# ── 场景渲染函数 ──────────────────────

def render_scene_title(progress):
    """0-3s: 片头"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 品牌条从顶部滑入
    bar_y = int(lerp(-120, 0, ease_out(clamp(progress/0.3, 0, 1))))
    draw.rectangle([0, bar_y, W, 110], fill=PICC_RED)
    if bar_y > -60:
        draw.text((50, bar_y + 20), "人保财险湄潭支公司", font=FONT_SMALL, fill=WHITE)
        draw.text((50, bar_y + 60), "PICC 防范非法金融宣传", font=FONT_TINY, fill=LIGHT_GRAY)

    # 大标题缩放弹出
    title_scale = ease_out_back(clamp(progress/0.5, 0, 1))
    title_size = int(90 * title_scale)
    if title_size > 10:
        title_font = load_font(title_size)
        title_y = int(lerp(H, H//2 - 120, ease_out(clamp((progress-0.1)/0.5, 0, 1))))

        # 光晕
        glow_alpha = clamp(1 - progress/0.5, 0, 0.3)
        for r in range(8, 20, 4):
            glow_c = tuple(int(lerp(BG_DARK[i], GOLD[i], glow_alpha * (20-r)/20)) for i in range(3))
            draw_text_center(draw, "防范养老诈骗", title_y, title_font, glow_c)

        draw_text_center(draw, "防范养老诈骗", title_y, title_font, GOLD)

    # 副标题淡入
    if progress > 0.3:
        sub_alpha = clamp((progress - 0.3) / 0.3, 0, 1)
        sub_c = tuple(int(lerp(BG_DARK[i], WHITE[i], sub_alpha)) for i in range(3))
        draw_text_center(draw, "守住爸妈的养老钱", H//2 + 40, FONT_TITLE, sub_c)

    # 底部红线
    if progress > 0.5:
        line_w = int(W * 0.6 * clamp((progress-0.5)/0.3, 0, 1))
        lx = (W - line_w) // 2
        draw.rectangle([lx, H//2 + 130, W-lx, H//2 + 136], fill=PICC_RED)

    # 底部提示
    if progress > 0.7:
        hint_alpha = clamp((progress-0.7)/0.2, 0, 1)
        hint_c = tuple(int(lerp(BG_DARK[i], GRAY[i], hint_alpha)) for i in range(3))
        draw_text_center(draw, "转发给父母 · 多一人看到 少一人被骗", H - 180, FONT_SMALL, hint_c)

    return img


def render_chat_scene(progress):
    """3-8s: 聊天对话场景"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 手机框
    phone_w, phone_h = 700, 1100
    phone_x = (W - phone_w) // 2
    phone_y = 180
    draw.rounded_rectangle([phone_x, phone_y, phone_x+phone_w, phone_y+phone_h],
                           radius=40, fill=(28, 28, 40), outline=(50, 50, 65), width=3)

    # 顶部状态栏
    draw.rectangle([phone_x+40, phone_y+40, phone_x+phone_w-40, phone_y+100], fill=(28, 28, 40))
    draw.text((phone_x + 60, phone_y + 50), "幸福一家人(3)", font=FONT_TINY, fill=LIGHT_GRAY)
    draw.line([phone_x+40, phone_y+110, phone_x+phone_w-40, phone_y+110], fill=(50, 50, 65), width=1)

    # 聊天气泡
    bubble_y = phone_y + 140
    chat_w = 540

    # 气泡1: 儿子 (0-0.2)
    if progress < 0.8:
        b1_delay = 0.0
        b1_prog = clamp((progress - b1_delay) / 0.2, 0, 1)
        if b1_prog > 0:
            bx = phone_x + phone_w - chat_w - 60
            alpha = ease_out(b1_prog)
            bg = tuple(int(lerp(BG_DARK[i], BLUE[i], alpha)) for i in range(3))
            txt_c = tuple(int(lerp(BG_DARK[i], WHITE[i], alpha)) for i in range(3))
            draw.rounded_rectangle([bx, bubble_y, bx+chat_w, bubble_y+56], radius=18, fill=bg)
            draw.text((bx+20, bubble_y+8), "妈，看啥呢这么认真？", font=FONT_SMALL, fill=txt_c)
            bubble_y += 80

    # 气泡2: 母亲 (0.15-0.4)
    if progress > 0.05:
        b2_prog = clamp((progress - 0.05) / 0.35, 0, 1)
        if b2_prog > 0:
            bx = phone_x + 60
            alpha = ease_out(b2_prog)
            bg = lerp_color(BG_DARK, (55, 55, 70), alpha)
            txt_c = tuple(int(lerp(BG_DARK[i], WHITE[i], alpha)) for i in range(3))
            draw.rounded_rectangle([bx, bubble_y, bx+chat_w, bubble_y+90], radius=18, fill=bg)
            draw.text((bx+20, bubble_y+6), "小王老师拉我进了一个养生群", font=FONT_SMALL, fill=txt_c)
            draw.text((bx+20, bubble_y+42), "说是有专门给老年人的福利～", font=FONT_SMALL, fill=txt_c)
            bubble_y += 115

    # 气泡3: 母亲继续 (0.35-0.6)
    if progress > 0.25:
        b3_prog = clamp((progress - 0.25) / 0.25, 0, 1)
        if b3_prog > 0:
            bx = phone_x + 60
            alpha = ease_out(b3_prog)
            bg = lerp_color(BG_DARK, (55, 55, 70), alpha)
            txt_c = tuple(int(lerp(BG_DARK[i], WHITE[i], alpha)) for i in range(3))
            draw.rounded_rectangle([bx, bubble_y, bx+chat_w, bubble_y+90], radius=18, fill=bg)
            draw.text((bx+20, bubble_y+6), "投一万每月返两千", font=FONT_SMALL, fill=txt_c)
            draw.text((bx+20, bubble_y+42), "隔壁张姐都赚了！", font=FONT_SMALL, fill=txt_c)
            bubble_y += 115

    # 群聊消息模拟 (0.5-0.85)
    if progress > 0.4:
        g_prog = clamp((progress - 0.4) / 0.2, 0, 1)
        bx = phone_x + 60
        alpha = ease_out(g_prog)
        msgs = [
            "恭喜张阿姨投5万，当天分红800元！",
            "太划算了，我也追加了3万",
            "名额有限，仅剩最后7个名额！",
        ]
        for j, msg in enumerate(msgs):
            m_alpha = clamp((g_prog - j*0.15) * 3, 0, 1)
            if m_alpha > 0:
                c = lerp_color(BG_DARK, (210, 210, 220), m_alpha)
                draw.rounded_rectangle([bx, bubble_y, bx+520, bubble_y+48], radius=14, fill=(40, 40, 52))
                draw.text((bx+16, bubble_y+8), msg, font=FONT_TINY, fill=c)
                bubble_y += 62

    # 警示文字从底部弹出 (0.7-1.0)
    if progress > 0.55:
        warn_prog = clamp((progress - 0.55) / 0.3, 0, 1)
        warn_y = int(lerp(H + 200, H - 350, ease_out(warn_prog)))
        warn_alpha = clamp(warn_prog * 1.5, 0, 1)

        # 红色警示条
        bar_alpha = int(255 * warn_alpha)
        draw.rectangle([0, warn_y-90, W, warn_y+160], fill=(int(180*warn_alpha), int(10*warn_alpha), int(10*warn_alpha)))

        # 脉冲动画（0.85-1.0段）
        pulse = 1.0
        if progress > 0.85:
            pulse = 1.0 + 0.03 * math.sin((progress - 0.85) * 30)
        pulse_size = int(72 * pulse)
        pulse_font = load_font(pulse_size) if pulse_size > 10 else FONT_BIG

        if warn_alpha > 0.5:
            draw_text_center(draw, "⚠ 年化收益240% = 非法集资", warn_y, pulse_font, YELLOW)
            draw_text_center(draw, "高额返利都是套路！", warn_y + 80, FONT_TITLE, WHITE)

    return img


def render_search_scene(progress):
    """8-13s: 搜索查询"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 标题
    t_alpha = clamp(progress / 0.3, 0, 1)
    t_c = tuple(int(lerp(BG_DARK[i], WHITE[i], t_alpha)) for i in range(3))
    draw_text_center(draw, "儿子察觉到不对劲...", 150, FONT_TITLE, t_c)

    # 搜索框
    if progress > 0.15:
        s_prog = clamp((progress-0.15)/0.2, 0, 1)
        search_y = 350
        search_w = int(lerp(100, 900, ease_out(s_prog)))
        search_x = (W - search_w) // 2
        draw.rounded_rectangle([search_x, search_y, search_x+search_w, search_y+80],
                               radius=20, fill=(40, 42, 55), outline=(80, 85, 100), width=2)
        if s_prog > 0.3:
            draw.text((search_x + 30, search_y + 16), "正在查询该平台企业信息...", font=FONT_SMALL, fill=GRAY)

    # 进度条
    if progress > 0.3:
        bar_prog = clamp((progress-0.3)/0.4, 0, 1)
        bar_y = 500
        bar_w = 800
        bar_x = (W - bar_w) // 2
        draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+16], radius=8, fill=(40, 42, 55))
        fill_w = int(bar_w * bar_prog)
        if fill_w > 0:
            # 渐变色
            r = int(lerp(80, 255, bar_prog))
            g = int(lerp(140, 60, bar_prog))
            b = int(lerp(255, 60, bar_prog))
            draw.rounded_rectangle([bar_x, bar_y, bar_x+fill_w, bar_y+16], radius=8, fill=(r, g, b))

    # 结果卡片
    if progress > 0.5:
        r_prog = clamp((progress-0.5)/0.3, 0, 1)
        card_y = int(lerp(H, 600, ease_out(r_prog)))
        card_alpha = clamp(r_prog, 0, 1)

        if card_alpha > 0:
            # 卡片背景
            bg_c = lerp_color(BG_DARK, (45, 15, 15), card_alpha)
            draw.rounded_rectangle([60, card_y, W-60, card_y+420], radius=24, fill=bg_c,
                                   outline=tuple(int(lerp(BG_DARK[i], RED[i], card_alpha)) for i in range(3)), width=3)

            if r_prog > 0.2:
                draw_text_center(draw, "⚠ 该平台已被公安机关", card_y + 50, FONT_TITLE, RED)
                draw_text_center(draw, "立案侦查", card_y + 125, FONT_BIG, RED)

            if r_prog > 0.5:
                stats = [
                    ("涉及受害老人", "300+ 人"),
                    ("最高单人损失", "38 万元"),
                ]
                sy = card_y + 220
                for label, value in stats:
                    draw_text_center(draw, label, sy, FONT_SMALL, GRAY)
                    draw_text_center(draw, value, sy + 50, FONT_TITLE, YELLOW)
                    sy += 100

    return img


def render_result_scene(progress):
    """13-18s: 查询结果展开"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 大红警示横幅
    banner_h = int(lerp(0, 200, ease_out(clamp(progress/0.3, 0, 1))))
    if banner_h > 0:
        draw.rectangle([0, 0, W, banner_h], fill=DARK_RED)
        if banner_h > 100:
            draw_text_center(draw, "⚠ 风险提示", banner_h//2, FONT_BIG, WHITE)

    # 详细报告卡片
    if progress > 0.2:
        card_prog = clamp((progress-0.2)/0.4, 0, 1)
        card_y = int(lerp(H, 260, ease_out(card_prog)))
        card_h = 900

        draw.rounded_rectangle([50, card_y, W-50, card_y+card_h], radius=24,
                               fill=(34, 36, 50), outline=(70, 75, 90), width=1)

        # 报告内容逐行显示
        report_lines = [
            ("【案件通报】", RED, FONT_TITLE, 0.0),
            ("", WHITE, FONT_SMALL, 0.0),
            ("该平台涉嫌非法吸收公众存款", WHITE, FONT_BODY, 0.15),
            ("已被公安机关立案侦查", WHITE, FONT_BODY, 0.2),
            ("", WHITE, FONT_SMALL, 0.0),
            ("涉案受害老人 300 余人", YELLOW, FONT_TITLE, 0.35),
            ("最高单人损失 38 万元", RED, FONT_BIG, 0.45),
            ("", WHITE, FONT_SMALL, 0.0),
            ("请勿向任何不明账户转账！", RED, FONT_BODY, 0.6),
        ]

        for text, color, font, delay in report_lines:
            if not text:
                continue
            line_prog = clamp((card_prog - delay) / 0.3, 0, 1)
            if line_prog > 0:
                # 滑入动画
                lx = int(lerp(-200, 100, ease_out(line_prog)))
                alpha = clamp(line_prog * 1.5, 0, 1)
                c = tuple(int(lerp(BG_DARK[i], color[i], alpha)) for i in range(3))
                line_y = card_y + 50 + report_lines.index((text, color, font, delay)) * (font.size + 12)
                draw.text((lx, line_y), text, font=font, fill=c)

    # 底部大字警示
    if progress > 0.7:
        pulse = 1.0 + 0.04 * math.sin(progress * 20)
        bottom_size = int(56 * pulse)
        bottom_font = load_font(bottom_size) if bottom_size > 10 else FONT_TITLE
        draw_text_center(draw, "已立案 · 300+老人被骗 · 最高38万", H - 200, bottom_font, RED)

    return img


def render_relief_scene(progress):
    """18-22s: 转折·幸好没投"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 母亲的话淡入
    if progress < 0.6:
        mom_prog = clamp(progress / 0.3, 0, 1)
        mom_c = tuple(int(lerp(BG_DARK[i], GRAY[i], mom_prog)) for i in range(3))
        draw_text_center(draw, "妈：那我还没投……", H//2 - 120, FONT_BIG, mom_c)

    # 停顿后，儿子的话弹出
    if progress > 0.25:
        son_prog = clamp((progress-0.25)/0.3, 0, 1)
        son_scale = ease_out_back(son_prog)
        son_size = int(90 * son_scale)
        if son_size > 10:
            son_font = load_font(son_size)
            # 绿色大字
            g = int(lerp(80, 235, son_prog))
            c = (80, g, 120)
            draw_text_center(draw, "还没投就对了！", H//2 + 40, son_font, c)

    # 握手表意
    if progress > 0.55:
        emoji_prog = clamp((progress-0.55)/0.3, 0, 1)
        emoji_scale = ease_out_back(emoji_prog)
        emoji_size = int(80 * emoji_scale)
        if emoji_size > 10:
            emoji_font = load_font(emoji_size)
            draw_text_center(draw, "🤝", H//2 + 220, emoji_font, WHITE)

    # 底部小字
    if progress > 0.7:
        sub_c = tuple(int(lerp(BG_DARK[i], LIGHT_GRAY[i], clamp((progress-0.7)/0.3, 0, 1))) for i in range(3))
        draw_text_center(draw, "关键一步：发现得早", H - 300, FONT_SMALL, sub_c)

    return img


def render_three_rules_scene(progress):
    """22-31s: 三个凡是"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 标题
    title_prog = clamp(progress / 0.3, 0, 1)
    title_scale = ease_out_back(title_prog)
    title_size = int(80 * title_scale)
    if title_size > 10:
        tf = load_font(title_size)
        draw_text_center(draw, "三个凡是", 200, tf, GOLD)
    draw.line([(300, 280), (W-300, 280)], fill=GOLD, width=3)

    # 三张卡片依次滑入
    rules = [
        ("凡是", "拉你进群、推荐理财项目的", "01"),
        ("凡是", "承诺高额返利、稳赚不赔的", "02"),
        ("凡是", "让你转账到个人账户的", "03"),
    ]

    for i, (prefix, text, num) in enumerate(rules):
        card_delay = 0.2 + i * 0.2
        card_prog = clamp((progress - card_delay) / 0.25, 0, 1)

        card_y = 380 + i * 180
        card_x = int(lerp(W, 60, ease_out(card_prog)))
        card_w = W - 120

        if card_prog > 0.05:
            # 卡片
            alpha = clamp(card_prog, 0, 1)
            bg_c = lerp_color(BG_DARK, (40, 42, 55), alpha)
            border_c = lerp_color(BG_DARK, (70, 75, 90), alpha)
            draw.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+140],
                                   radius=20, fill=bg_c, outline=border_c, width=1)

            if card_prog > 0.3:
                # "凡是" 红色标签
                draw.text((card_x + 30, card_y + 12), prefix, font=FONT_BIG, fill=RED)
                # 编号
                draw.text((card_x + card_w - 80, card_y + 12), num, font=FONT_TITLE, fill=(60, 62, 75))
                # 内容
                draw.text((card_x + 170, card_y + 25), text, font=FONT_BODY, fill=WHITE)

    # 底部大字
    if progress > 0.75:
        end_prog = clamp((progress - 0.75) / 0.2, 0, 1)
        end_scale = ease_out_back(end_prog)
        end_size = int(96 * end_scale)
        if end_size > 10:
            ef = load_font(end_size)
            draw_text_center(draw, "全是骗子！", H - 300, ef, RED)

    return img


def render_action_scene(progress):
    """31-36s: 退群 + 转发"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 对话
    draw_text_center(draw, "妈：那我把群退了？", H//2 - 200, FONT_BIG, GRAY)

    if progress > 0.2:
        ok_prog = clamp((progress-0.2)/0.3, 0, 1)
        ok_scale = ease_out_back(ok_prog)
        ok_size = int(100 * ok_scale)
        if ok_size > 10:
            of = load_font(ok_size)
            draw_text_center(draw, "退！", H//2 - 20, of, GREEN)

    if progress > 0.4:
        fwd_prog = clamp((progress-0.4)/0.3, 0, 1)
        fwd_c = tuple(int(lerp(BG_DARK[i], WHITE[i], fwd_prog)) for i in range(3))
        draw_text_center(draw, "然后转发给你的老姐妹群", H//2 + 120, FONT_TITLE, fwd_c)

    if progress > 0.65:
        send_prog = clamp((progress-0.65)/0.25, 0, 1)
        send_scale = ease_out_back(send_prog)
        send_size = int(80 * send_scale)
        if send_size > 10:
            sf = load_font(send_size)
            draw_text_center(draw, "妈：发！", H//2 + 280, sf, YELLOW)

    # 转发箭头 (0.75-1.0)
    if progress > 0.75:
        arrow_prog = clamp((progress-0.75)/0.25, 0, 1)
        for j in range(3):
            ax = W//2 - 120 + j*120
            ay = H - 400
            arrow_y = int(ay - 30 * math.sin(arrow_prog * 3.14 + j*0.6))
            alpha = clamp(arrow_prog - j*0.1, 0, 1)
            c = tuple(int(lerp(BG_DARK[i], GREEN[i], alpha)) for i in range(3))
            af = load_font(50)
            draw.text((ax, arrow_y), "↗", font=af, fill=c)

    return img


def render_closing_scene(progress):
    """36-42s: PICC品牌片尾"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 红色从底部扩展
    if progress < 0.4:
        red_h = int(lerp(0, H//2 + 200, ease_out(clamp(progress/0.4, 0, 1))))
        if red_h > 0:
            draw.rectangle([0, H - red_h, W, H], fill=PICC_RED)
    else:
        draw.rectangle([0, H//2 - 200, W, H], fill=PICC_RED)

    # 品牌文字
    if progress > 0.3:
        brand_prog = clamp((progress-0.3)/0.3, 0, 1)
        brand_c = tuple(int(lerp(PICC_RED[i], WHITE[i], brand_prog)) for i in range(3))
        draw_text_center(draw, "人保财险湄潭支公司", H//2 - 120, FONT_BIG, brand_c)
        draw_text_center(draw, "PICC", H//2 - 30, FONT_TITLE, brand_c)
        draw.line([(300, H//2+30), (W-300, H//2+30)], fill=WHITE, width=2)

    if progress > 0.5:
        sl_prog = clamp((progress-0.5)/0.3, 0, 1)
        sl_c = tuple(int(lerp(PICC_RED[i], WHITE[i], sl_prog)) for i in range(3))
        draw_text_center(draw, "守住爸妈的养老钱", H//2 + 100, FONT_TITLE, sl_c)

    if progress > 0.7:
        call_prog = clamp((progress-0.7)/0.3, 0, 1)
        call_scale = ease_out_back(call_prog)
        call_size = int(60 * call_scale)
        if call_size > 10:
            cf = load_font(call_size)
            draw_text_center(draw, "转发就是保护", H//2 + 220, cf, GOLD)

    # 底部固定
    if progress > 0.5:
        draw_text_center(draw, "防范非法金融  人人有责", H//2 + 340, FONT_SMALL, WHITE)
        draw_text_center(draw, "举报热线：12378", H//2 + 400, FONT_TINY, LIGHT_GRAY)

    return img


# ── 主渲染 ────────────────────────────

SCENES = [
    (3.0, render_scene_title),
    (5.0, render_chat_scene),
    (5.0, render_search_scene),
    (5.0, render_result_scene),
    (4.0, render_relief_scene),
    (9.0, render_three_rules_scene),
    (5.0, render_action_scene),
    (6.0, render_closing_scene),
]

TOTAL_DURATION = sum(d for d, _ in SCENES)

def main():
    print(f"Total duration: {TOTAL_DURATION}s")
    print(f"Total frames: {int(TOTAL_DURATION * FPS)}")
    print("Rendering...")

    all_frames = []
    time_cursor = 0.0

    for dur, render_func in SCENES:
        n_frames = int(dur * FPS)
        scene_start = time_cursor

        for fi in range(n_frames):
            # progress = 当前场景中的进度 [0, 1]
            progress = fi / n_frames if n_frames > 1 else 1.0
            frame = render_func(progress)
            all_frames.append(frame)

        time_cursor += dur
        sys.stdout.write(f"\r  {render_func.__name__}: {n_frames} frames [{time_cursor:.1f}s/{TOTAL_DURATION}s]")
        sys.stdout.flush()

    print(f"\nTotal frames: {len(all_frames)}")
    print(f"Encoding MP4...")

    iio.imwrite(
        OUTPUT,
        [np.array(f) for f in all_frames],
        fps=FPS,
        codec='h264',
        output_params=['-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p'],
    )

    print(f"Video saved: {OUTPUT}")
    print(f"Duration: {len(all_frames)/FPS:.1f}s | {W}x{H} | {FPS}fps")

if __name__ == "__main__":
    main()

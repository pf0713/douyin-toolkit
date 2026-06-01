"""
最终版: 逐段生成音频→逐段渲染→边渲边写(不爆内存)→合并
"""
import asyncio, edge_tts, os, subprocess, imageio_ffmpeg, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v3 as iio

# ── 配置 ──────────────────────────────
W, H = 1080, 1920
FPS = 24
OUT_DIR = os.path.dirname(__file__)
TEMP_DIR = os.path.join(OUT_DIR, "temp_v3")
os.makedirs(TEMP_DIR, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

BG = (22, 22, 34)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GOLD = (255, 190, 40)
GREEN = (80, 240, 120)
GRAY = (140, 140, 155)
BLUE = (65, 140, 255)
ORANGE = (255, 150, 60)
PICC_RED = (195, 25, 35)

def load_font(size):
    for f in ["C:/Windows/Fonts/msyhbd.ttf", "C:/Windows/Fonts/msyh.ttf",
              "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"]:
        if os.path.exists(f):
            try: return ImageFont.truetype(f, size)
            except: continue
    return ImageFont.load_default()

FONT_HUGE = load_font(96)
FONT_BIG = load_font(64)
FONT_TITLE = load_font(52)
FONT_BODY = load_font(40)
FONT_SMALL = load_font(30)
FONT_TINY = load_font(24)

def ease_out(t): return 1 - (1-t)**3
def ease_out_back(t):
    c1 = 1.70158; return 1+(c1+1)*(t-1)**3+c1*(t-1)**2

def lerp(a,b,t): return a+(b-a)*t
def lerp_color(c1,c2,t): return tuple(int(lerp(c1[i],c2[i],t)) for i in range(3))

def draw_center_text(draw, text, y, font, color, max_w=None):
    if max_w is None: max_w = W-100
    lines = []
    for para in text.split('\n'):
        if not para: lines.append(''); continue
        line = ''
        for ch in para:
            if draw.textbbox((0,0), line+ch, font=font)[2] > max_w:
                lines.append(line); line = ch
            else: line += ch
        if line: lines.append(line)
    lh = font.size+10; sy = y - len(lines)*lh//2
    for i, ln in enumerate(lines):
        if ln:
            tw = draw.textbbox((0,0), ln, font=font)[2]
            draw.text(((W-tw)//2, sy+i*lh), ln, font=font, fill=color)

def get_duration(path):
    """用ffmpeg获取精确时长"""
    r = subprocess.run([FFMPEG, '-i', path.replace('\\','/')],
                      capture_output=True, text=True)
    import re
    m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', r.stderr)
    if m:
        return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
    return 2.0  # fallback

# ═══════════════════════════════════════
# 配音稿 (纯文本, 不用SSML)
# ═══════════════════════════════════════
VOICE_MALE = "zh-CN-YunxiNeural"
VOICE_FEMALE = "zh-CN-XiaoxiaoNeural"

LINES = [
    ("妈，看啥呢这么认真？", VOICE_MALE, "儿子"),
    ("小王老师拉我进了一个养生群，说是有专门给咱们老年人的福利项目。", VOICE_FEMALE, "母亲"),
    ("你看，投一万每月返两千，隔壁张姐都赚了。", VOICE_FEMALE, "母亲"),
    ("妈，你等一下。让我查查这个平台——", VOICE_MALE, "儿子"),
    ("你看，这个平台上个月刚被公安机关立案侦查，", VOICE_MALE, "儿子"),
    ("骗了三百多个老人，最多的一个人被骗了三十八万。", VOICE_MALE, "儿子"),
    ("啊？那我还没投呢……", VOICE_FEMALE, "母亲"),
    ("还没投就对了。", VOICE_MALE, "儿子"),
    ("妈，你记住了，这世界上没有稳赚不赔的买卖。", VOICE_MALE, "儿子"),
    ("凡是拉你进群推荐理财项目的，凡是承诺高额返利稳赚不赔的，", VOICE_MALE, "儿子"),
    ("凡是让你转账到个人账户的——全都是骗子！", VOICE_MALE, "儿子"),
    ("那我马上把群退了。", VOICE_FEMALE, "母亲"),
    ("退！然后把这条视频转发给你那些老姐妹。", VOICE_MALE, "儿子"),
    ("好，我这就发。", VOICE_FEMALE, "母亲"),
    ("守护爸妈的养老钱，多一次转发，就少一个人被骗。", VOICE_MALE, "旁白"),
    ("人保财险湄潭支公司提醒您：防范非法金融，人人有责。", VOICE_MALE, "旁白"),
    ("举报电话：12378。", VOICE_MALE, "旁白"),
]

async def gen_audio():
    print("=== Part A: 生成配音 ===")
    clips = []
    durations = []

    for i, (text, voice, role) in enumerate(LINES):
        path = os.path.join(TEMP_DIR, f"audio_{i:02d}.mp3")
        clips.append(path)

        if os.path.exists(path) and os.path.getsize(path) > 1000:
            dur = get_duration(path)
            durations.append(dur)
            print(f"  [{i}] skip {role}: {dur:.1f}s")
            continue

        print(f"  [{i}] {role}: {text[:35]}...")
        comm = edge_tts.Communicate(text, voice, rate="+8%")
        await comm.save(path)
        dur = get_duration(path)
        durations.append(dur)
        print(f"       -> {dur:.1f}s")

    # 合并
    concat = "|".join(os.path.abspath(c).replace("\\","/") for c in clips)
    merged = os.path.join(OUT_DIR, "voiceover_v3.mp3")
    subprocess.run([FFMPEG,"-y","-i",f"concat:{concat}","-c","copy",
                    merged.replace("\\","/")], capture_output=True)
    total = sum(durations)
    print(f"Merged: {total:.1f}s total\n")
    return clips, durations, merged

# ═══════════════════════════════════════
# 逐段渲染 (不存全帧, 每段直接写temp mp4)
# ═══════════════════════════════════════

def render_segment_video(seg_idx, duration_sec, role, text, output_path):
    """渲染单个片段为temp mp4"""
    n_frames = max(int(duration_sec * FPS), 1)
    frames = []

    if role == "儿子":
        accent = BLUE; icon = "👦"
    elif role == "母亲":
        accent = ORANGE; icon = "👵"
    else:
        accent = PICC_RED; icon = "📢"

    # 选字体
    if len(text) <= 8:
        font = FONT_BIG
    elif len(text) <= 20:
        font = FONT_TITLE
    else:
        font = FONT_BODY

    for fi in range(n_frames):
        t = fi/n_frames if n_frames>1 else 1.0
        img = Image.new("RGB", (W,H), BG)
        draw = ImageDraw.Draw(img)

        # 顶部条
        draw.rectangle([0,0,W,76], fill=(28,28,42))
        draw.text((40,20), "人保财险湄潭支公司", font=FONT_TINY, fill=GRAY)
        draw.text((W-220,20), "防范非法金融宣传", font=FONT_TINY, fill=PICC_RED)

        # 角色标签
        tag_x = int(lerp(-200, 50, ease_out(min(t/0.2, 1))))
        bbox = draw.textbbox((0,0), f"{icon} {role}", font=FONT_SMALL)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        px, py = 18, 10
        draw.rounded_rectangle([tag_x,120,tag_x+tw+px*2,120+th+py*2],
                              radius=(th+py*2)//2, fill=accent)
        draw.text((tag_x+px, 120+py-2), f"{icon} {role}", font=FONT_SMALL, fill=WHITE)

        # 卡片
        card_y = 260
        card_h = 1000
        alpha = min(t/0.25, 1.0)
        card_c = lerp_color(BG, (30,32,44), alpha)
        draw.rounded_rectangle([53,card_y,W-53,card_y+card_h], radius=24, fill=(8,8,16))
        draw.rounded_rectangle([50,card_y,W-50,card_y+card_h], radius=24, fill=card_c)
        draw.rectangle([80,card_y+40,88,card_y+100], fill=accent)

        # 台词
        text_alpha = min(max((t-0.12)/0.35, 0), 1.0)
        text_c = lerp_color(BG, WHITE, text_alpha)
        draw_center_text(draw, text, card_y+card_h//2, font, text_c, max_w=W-180)

        # 底部
        bar_w = 500; bar_x = (W-bar_w)//2; bar_y = H-100
        draw.rounded_rectangle([bar_x,bar_y,bar_x+bar_w,bar_y+5], radius=3, fill=(40,42,55))
        fill_w = int(bar_w*t)
        if fill_w>0:
            draw.rounded_rectangle([bar_x,bar_y,bar_x+fill_w,bar_y+5], radius=3, fill=accent)
        draw.text((W-80, H-65), f"{seg_idx+1}/{len(LINES)}", font=FONT_TINY, fill=GRAY)

        frames.append(img)

    # 直接写temp文件
    iio.imwrite(output_path, [np.array(f) for f in frames], fps=FPS,
               codec='h264', output_params=['-preset','ultrafast','-crf','20','-pix_fmt','yuv420p'])
    return output_path


def render_opening(duration_sec, output_path):
    """片头"""
    n = max(int(duration_sec*FPS), 1)
    frames = []
    for fi in range(n):
        t = fi/n if n>1 else 1.0
        img = Image.new("RGB", (W,H), (18,18,28))
        draw = ImageDraw.Draw(img)

        bar_y = int(lerp(-110, 0, ease_out(min(t/0.4,1))))
        draw.rectangle([0,bar_y,W,110], fill=PICC_RED)
        if bar_y>-50:
            draw.text((50,bar_y+20), "人保财险湄潭支公司", font=FONT_SMALL, fill=WHITE)

        s = ease_out_back(min(t/0.55,1))
        sz = max(int(90*s), 10)
        sf = load_font(sz)
        ty = int(lerp(H, H//2-120, ease_out(min((t-0.08)/0.5, 1))))
        draw_center_text(draw, "防范养老诈骗", ty, sf, GOLD)

        if t>0.4:
            a = min((t-0.4)/0.3, 1)
            draw_center_text(draw, "守住爸妈的养老钱", H//2+40, FONT_TITLE,
                           lerp_color((18,18,28), WHITE, a))
        if t>0.6:
            a = min((t-0.6)/0.3, 1)
            draw_center_text(draw, "转发给父母 · 多一人看到 少一人被骗", H-180, FONT_SMALL,
                           lerp_color((18,18,28), GRAY, a))
        frames.append(img)

    iio.imwrite(output_path, [np.array(f) for f in frames], fps=FPS,
               codec='h264', output_params=['-preset','ultrafast','-crf','20','-pix_fmt','yuv420p'])
    return output_path


def render_warning(duration_sec, text, output_path):
    """红色警示"""
    n = max(int(duration_sec*FPS), 1)
    frames = []
    for fi in range(n):
        t = fi/n if n>1 else 1.0
        img = Image.new("RGB", (W,H), BG)
        draw = ImageDraw.Draw(img)

        banner_h = int(lerp(0, 150, ease_out(min(t/0.2,1))))
        if banner_h>0:
            draw.rectangle([0,0,W,banner_h], fill=(170,18,28))
            if banner_h>80:
                draw_center_text(draw, "⚠ 风险警示", banner_h//2, FONT_TITLE, WHITE)

        if len(text)<=15: fnt=FONT_BIG
        else: fnt=FONT_TITLE

        pulse = 1.0+0.04*math.sin(t*25)
        ps = max(int(fnt.size*pulse), 20)
        pf = load_font(ps)

        alpha = min(t/0.3, 1)
        draw_center_text(draw, text, H//2, pf, lerp_color(BG, RED, alpha), max_w=W-120)

        if t>0.5:
            draw_center_text(draw, "请勿向任何不明账户转账！", H//2+200, FONT_SMALL,
                           lerp_color(BG, GOLD, min((t-0.5)/0.3,1)))
        frames.append(img)

    iio.imwrite(output_path, [np.array(f) for f in frames], fps=FPS,
               codec='h264', output_params=['-preset','ultrafast','-crf','20','-pix_fmt','yuv420p'])
    return output_path


def render_closing(duration_sec, output_path):
    """片尾"""
    n = max(int(duration_sec*FPS), 1)
    frames = []
    for fi in range(n):
        t = fi/n if n>1 else 1.0
        img = Image.new("RGB", (W,H), BG)
        draw = ImageDraw.Draw(img)

        split_y = int(lerp(H, H//2-150, ease_out(min(t/0.4,1))))
        draw.rectangle([0,split_y,W,H], fill=PICC_RED)

        if t>0.3:
            draw_center_text(draw, "人保财险湄潭支公司", H//2-80, FONT_BIG, WHITE)
            draw_center_text(draw, "PICC", H//2+10, FONT_BODY, (255,210,210))
            draw.line([(280,H//2+65),(W-280,H//2+65)], fill=WHITE, width=2)

        if t>0.5:
            a = min((t-0.5)/0.3,1)
            draw_center_text(draw, "守住爸妈的养老钱", H//2+140, FONT_TITLE,
                           lerp_color(PICC_RED, WHITE, a))
        if t>0.65:
            draw_center_text(draw, "转发就是保护", H//2+260, FONT_BIG, GOLD)
            draw_center_text(draw, "防范非法金融  人人有责", H//2+370, FONT_SMALL, WHITE)
            draw_center_text(draw, "举报热线：12378", H//2+430, FONT_TINY, (255,190,190))
        frames.append(img)

    iio.imwrite(output_path, [np.array(f) for f in frames], fps=FPS,
               codec='h264', output_params=['-preset','ultrafast','-crf','20','-pix_fmt','yuv420p'])
    return output_path


def render_all_segments(durations):
    print("=== Part B: 逐段渲染视频 ===")
    temp_videos = []

    # 片头 ~2.5s
    opening_path = os.path.join(TEMP_DIR, "seg_opening.mp4")
    print("  [opening] 片头 (2.5s)")
    render_opening(2.5, opening_path)
    temp_videos.append(opening_path)

    # 主体段
    for i, dur in enumerate(durations):
        text, voice, role = LINES[i]
        vpath = os.path.join(TEMP_DIR, f"seg_{i:02d}.mp4")

        if i in (4, 5, 10):  # 立案/被骗/全是骗子 → 红警
            print(f"  [{i}] WARNING: {text[:30]}... ({dur:.1f}s)")
            render_warning(dur, text, vpath)
        else:
            print(f"  [{i}] {role}: {text[:30]}... ({dur:.1f}s)")
            render_segment_video(i, dur, role, text, vpath)
        temp_videos.append(vpath)

    # 片尾 ~4s
    closing_path = os.path.join(TEMP_DIR, "seg_closing.mp4")
    print("  [closing] 片尾 (4.0s)")
    render_closing(4.0, closing_path)
    temp_videos.append(closing_path)

    return temp_videos


def concat_videos(temp_videos, output_path):
    """用ffmpeg concat拼接所有temp视频"""
    print(f"\n=== Concat {len(temp_videos)} segments ===")

    # 生成文件列表
    list_file = os.path.join(TEMP_DIR, "concat_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for v in temp_videos:
            f.write(f"file '{os.path.abspath(v).replace(chr(92),'/')}'\n")

    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0",
           "-i", list_file.replace("\\","/"),
           "-c", "copy",
           output_path.replace("\\","/")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("Concat failed:", r.stderr[-500:])
        return None
    print(f"Video: {output_path} ({os.path.getsize(output_path)/1024/1024:.1f}MB)")
    return output_path


def merge_av(video_path, audio_path, final_path):
    """合成音频+视频"""
    print(f"\n=== Merge A+V ===")
    vp = os.path.abspath(video_path).replace("\\","/")
    ap = os.path.abspath(audio_path).replace("\\","/")
    fp = os.path.abspath(final_path).replace("\\","/")

    # 获取音频时长来trim视频
    r = subprocess.run([FFMPEG, "-i", ap], capture_output=True, text=True)
    import re
    m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', r.stderr)
    audio_dur = int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 40

    cmd = [FFMPEG, "-y",
           "-i", vp, "-i", ap,
           "-c:v", "copy", "-c:a", "aac",
           "-t", str(audio_dur + 1),
           "-map", "0:v:0", "-map", "1:a:0",
           "-shortest", fp]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"Final: {fp} ({os.path.getsize(fp)/1024/1024:.1f}MB)")
        return fp
    print("Merge failed:", r.stderr[-400:])
    return None


# ═══════════════════════════════════════
async def main():
    # 清理旧temp
    import shutil
    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))

    # A: 音频
    clips, durations, audio_path = await gen_audio()
    total = sum(durations)
    print(f"Audio total: {total:.1f}s ({len(durations)} clips)")

    # B: 逐段渲染视频
    temp_videos = render_all_segments(durations)

    # C: 拼接
    video_path = os.path.join(OUT_DIR, "video_v3_concat.mp4")
    concat_videos(temp_videos, video_path)

    # D: 合成
    final = os.path.join(OUT_DIR, "防范养老诈骗_人保财险湄潭支公司_配音版.mp4")
    result = merge_av(video_path, audio_path, final)
    if result:
        os.startfile(result)

if __name__ == "__main__":
    asyncio.run(main())

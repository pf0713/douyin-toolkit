"""
Step 1: 生成45秒配音（旁白+对话混搭，语速偏慢）
"""
import asyncio, edge_tts, os, subprocess, imageio_ffmpeg

OUT_DIR = os.path.dirname(__file__)
COMBINED = os.path.join(OUT_DIR, "voiceover_full.mp3")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

VOICE_MALE = "zh-CN-YunxiNeural"      # 儿子/旁白
VOICE_FEMALE = "zh-CN-XiaoxiaoNeural"  # 母亲

# 加长版配音稿，目标45秒（rate="-5%", 约3-4字/秒, 共160-180字）
LINES = [
    ("妈，看啥呢这么认真？", VOICE_MALE),
    ("小王老师拉我进了一个养生群，说是有专门给咱们老年人的福利项目。", VOICE_FEMALE),
    ("你看，投一万每月返两千，隔壁张姐都赚了。", VOICE_FEMALE),
    ("妈，你等一下。让我查查这个平台——", VOICE_MALE),
    ("你看，这个平台上个月刚被公安机关立案侦查，", VOICE_MALE),
    ("骗了三百多个老人，最多的一个人被骗了三十八万。", VOICE_MALE),
    ("啊？那我还没投呢……", VOICE_FEMALE),
    ("还没投就对了。", VOICE_MALE),
    ("妈，你记住了，这世界上没有稳赚不赔的买卖。", VOICE_MALE),
    ("凡是拉你进群推荐理财项目的，凡是承诺高额返利稳赚不赔的，", VOICE_MALE),
    ("凡是让你转账到个人账户的——全都是骗子！", VOICE_MALE),
    ("那我马上把群退了。", VOICE_FEMALE),
    ("退，然后把这条视频转发给你那些老姐妹。", VOICE_MALE),
    ("好，我这就发。", VOICE_FEMALE),
    ("守护爸妈的养老钱，多一次转发，就少一个人被骗。", VOICE_MALE),
    ("人保财险湄潭支公司提醒您：防范非法金融，人人有责。", VOICE_MALE),
    ("举报热线：幺儿三七八。", VOICE_MALE),
]

async def gen_one(text, voice, path):
    # 用稍慢语速 + 小停顿让总时长接近45秒
    comm = edge_tts.Communicate(text, voice, rate="-8%")
    await comm.save(path)

async def main():
    print("Generating voice clips (slow rate for 45s target)...")
    clips = []
    for i, (text, voice) in enumerate(LINES):
        path = os.path.join(OUT_DIR, f"clip_{i:02d}.mp3")
        clips.append(path)
        print(f"  [{i}] {voice.split('-')[-1][:8]}: {text[:50]}...")
        try:
            await gen_one(text, voice, path)
            sz = os.path.getsize(path)
            print(f"       ok ({sz}B)")
        except Exception as e:
            print(f"       FAIL: {e}")
            comm = edge_tts.Communicate(text, voice)
            await comm.save(path)
            print(f"       retry ok")

    # 合并
    print(f"\nMerging {len(clips)} clips...")
    concat_input = "|".join(os.path.abspath(c).replace("\\", "/") for c in clips)
    cmd = [FFMPEG, "-y", "-i", f"concat:{concat_input}", "-c", "copy", COMBINED.replace("\\", "/")]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Merge failed, binary fallback...")
        with open(COMBINED, 'wb') as out:
            for c in clips:
                with open(c, 'rb') as f:
                    out.write(f.read())

    size_kb = os.path.getsize(COMBINED) / 1024
    print(f"Done: {COMBINED} ({size_kb:.1f} KB)")

    # 粗略估算时长 (MP3 frame count)
    with open(COMBINED, 'rb') as f:
        data = f.read()
    frames = 0
    i = 0
    while i < len(data) - 4:
        if data[i] == 0xFF and (data[i+1] & 0xE0) == 0xE0:
            bitrate_idx = (data[i+2] >> 4) & 0x0F
            srate_idx = (data[i+2] >> 2) & 0x03
            padding = (data[i+2] >> 1) & 0x01
            ver_idx = (data[i+1] >> 3) & 0x03
            bitrates = {1:32,2:40,3:48,4:56,5:64,6:80,7:96,8:112,9:128,10:160,11:192,12:224,13:256,14:320}
            srates = {0:44100, 1:48000, 2:32000}
            br = bitrates.get(bitrate_idx, 128) * 1000
            sr = srates.get(srate_idx, 44100)
            fs = 144 * br // sr + padding
            frames += 1
            i += max(fs, 1)
        else:
            i += 1
    # 粗略时长
    samples_per_frame = 1152  # MPEG1 Layer3
    dur_est = frames * samples_per_frame / 44100
    print(f"Estimated duration: {dur_est:.1f}s ({frames} frames)")

if __name__ == "__main__":
    asyncio.run(main())

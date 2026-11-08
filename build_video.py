"""Build a native 9:16 (1080x1920) canopy installation promo video for TikTok / Facebook Reels.

Usage: python3 build_video.py [uploads_dir]
"""
import subprocess, os, sys, wave
import numpy as np

UP = (sys.argv[1] if len(sys.argv) > 1 else "/root/.claude/uploads/7ad25e6e-7da5-536c-a48f-2ccd3a8b7c50") + "/"
ROOT = os.path.dirname(os.path.abspath(__file__))
W = os.environ.get("WORK", os.path.join(ROOT, ".work")); os.makedirs(W, exist_ok=True)
OUT = os.path.join(ROOT, "output"); os.makedirs(OUT, exist_ok=True)
F = "/usr/share/fonts/opentype/inter/"
BLACK = F + "Inter-Black.otf" if os.path.exists(F + "Inter-Black.otf") else F + "Inter-ExtraBold.otf"
BOLD = F + "Inter-ExtraBold.otf"
SEMI = F + "Inter-SemiBold.otf"
FPS = 30
VW, VH = 1080, 1920
YEL = "0xFFC21A"
BRAND = "UR CANOPY"
TEL = "018-290 8433"


def run(cmd):
    print(" ".join(cmd)[:200]); subprocess.run(cmd, check=True)


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def alpha(a, b, f=0.3):
    return f"if(lt(t,{a}),0,if(lt(t,{a+f}),(t-{a})/{f},if(lt(t,{b-f}),1,if(lt(t,{b}),({b}-t)/{f},0))))"


def dt(text, font, size, y, a, b, color="white", box=None, border=20, x="(w-text_w)/2"):
    s = (f"drawtext=fontfile={font}:text='{esc(text)}':fontsize={size}:fontcolor={color}"
         f":x={x}:y={y}:alpha='{alpha(a, b)}'")
    if box:
        s += f":box=1:boxcolor={box}:boxborderw={border}"
    else:
        s += ":shadowcolor=black@0.7:shadowx=4:shadowy=4:borderw=2:bordercolor=black@0.35"
    return s


def step(tag, lines, a, b, y0=1080):
    """Centered step caption: yellow tag + white lines on dark boxes (kept above TikTok/FB bottom UI)."""
    out = [dt(tag, BLACK, 54, y0, a, b, color="black", box=f"{YEL}@1", border="16|30")]
    for i, ln in enumerate(lines):
        out.append(dt(ln, BOLD, 64, y0 + 120 + i * 104, a + 0.12 * (i + 1), b, box="black@0.6", border="18|28"))
    return out


def brand_bar(a, b):
    # small persistent brand + phone at top
    return [dt(f"{BRAND}  |  {TEL}", BOLD, 42, 250, a, b, box="black@0.45", border="14|24")]


# (file, start, src_len, speed, pan_from, pan_to, overlay builder(dur) -> list)
# pan values: 0 = left edge of the landscape shot, 1 = right edge
segs = [
    ("ebaecb94-VID20261103121327.mp4", 0.3, 1.8, 1.0, 0.15, 0.35,
     lambda d: [dt("DARI INI...", BLACK, 130, "(h-text_h)/2", 0.1, d + 1)]),
    ("9022f23d-VID20261106115135.mp4", 3.0, 2.2, 1.0, 0.45, 0.60,
     lambda d: [dt("...JADI INI!", BLACK, 130, "(h-text_h)/2", 0.15, d + 1, color=YEL)]),
    ("ebaecb94-VID20261103121327.mp4", 0.0, 7.5, 1.5, 0.30, 0.60,
     lambda d: ["drawbox=x=0:y=0:w=iw:h=ih:color=black@0.4:t=fill:enable='lt(t,2.3)'",
                dt("PROSES", BLACK, 110, 640, 0.35, 2.3),
                dt("PEMASANGAN", BLACK, 110, 770, 0.45, 2.3),
                dt("KANOPI", BLACK, 190, 900, 0.6, 2.3, color=YEL)]
               + step("LANGKAH 1", ["Susun rangka besi", "di tapak"], 2.5, d - 0.1)
               + brand_bar(2.5, d + 1)),
    ("86c4e5b9-VID20261103121347.mp4", 0.0, 6.2, 1.25, 0.32, 0.40,
     lambda d: step("LANGKAH 2", ["Pasang & ketatkan", "setiap sambungan"], 0.5, d - 0.1)
               + brand_bar(0, d + 1)),
    ("dba7b19c-VID20261103134353.mp4", 0.0, 8.1, 1.5, 0.05, 0.70,
     lambda d: step("LANGKAH 3", ["Rangka dinaikkan", "kukuh & selamat"], 0.5, d - 0.1)
               + brand_bar(0, d + 1)),
    ("9022f23d-VID20261106115135.mp4", 0.0, 6.7, 1.15, 0.25, 0.70,
     lambda d: step("HASIL AKHIR", ["Kanopi siap untuk", "majlis anda"], 0.7, d - 0.1)
               + brand_bar(0, d + 1)),
    ("b046447d-VID20261106120834.mp4", 0.0, 5.9, 1.15, 0.70, 0.30,
     lambda d: brand_bar(0, d + 1)),
    ("47cda38c-VID20261106115152.mp4", 0.0, 5.45, 1.0, 0.40, 0.60,
     lambda d: ["drawbox=x=0:y=0:w=iw:h=ih:color=black@0.55:t=fill:enable='gte(t,0.5)'",
                dt("PERLUKAN KANOPI?", BLACK, 92, 520, 0.6, d + 1),
                dt(BRAND, BLACK, 145, 670, 0.9, d + 1, color=YEL),
                dt("Hubungi / WhatsApp", BOLD, 66, 900, 1.3, d + 1),
                dt(TEL, BLACK, 118, 1000, 1.5, d + 1, color="black", box=f"{YEL}@1", border="22|40"),
                dt("Kanopi  -  Khemah  -  Pentas Acara", SEMI, 54, 1220, 1.9, d + 1)]),
]
trans = [("fadewhite", 0.25), ("fadeblack", 0.4), ("smoothleft", 0.4), ("smoothleft", 0.4),
         ("fadewhite", 0.6), ("dissolve", 0.5), ("dissolve", 0.5)]

durs = []
for i, (f, ss, ln, sp, p0, p1, fx) in enumerate(segs):
    d = round(ln / sp, 3); durs.append(d)
    pan = f"(iw-{VW})*({p0}+({p1}-{p0})*min(t/{d},1))"
    vf = ",".join([f"setpts=(PTS-STARTPTS)/{sp}", f"fps={FPS}",
                   f"scale=-2:{VH}:flags=lanczos", f"crop={VW}:{VH}:x='{pan}':y=0", "setsar=1",
                   "eq=contrast=1.08:saturation=1.22:brightness=0.01", "unsharp=5:5:0.6"]
                  + fx(d) + ["format=yuv420p"])
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(ln), "-i", UP + f, "-an",
         "-vf", vf, "-t", str(d), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         os.path.join(W, f"s{i}.mp4")])

inputs, fc, offs = [], [], []
for i in range(len(segs)):
    inputs += ["-i", os.path.join(W, f"s{i}.mp4")]
prev = "[0:v]"; acc = durs[0]
for i, (tn, td) in enumerate(trans):
    off = round(acc - td, 3); offs.append(off)
    fc.append(f"{prev}[{i+1}:v]xfade=transition={tn}:duration={td}:offset={off}[x{i}]")
    prev = f"[x{i}]"; acc = off + durs[i + 1]
total = round(acc, 3)
fc.append(f"{prev}fade=t=out:st={total-0.6}:d=0.6,format=yuv420p[v]")
print("durations", durs, "offsets", offs, "total", total)

# ---------- royalty-free synthesized music ----------
np.random.seed(7)
SR = 44100; BPM = 120; beat = 60 / BPM
N = int(SR * (total + 0.5)); mix = np.zeros(N)


def add(sig, start):
    i = int(start * SR); e = min(N, i + len(sig))
    if 0 <= i < N: mix[i:e] += sig[: e - i]


def env(n, a=0.005, r=None):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: e *= np.exp(-np.arange(n) / (r * SR))
    return e


def kick():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 50 + 110 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * 0.9


def noise_hit(dur, rel, amp):
    n = int(dur * SR); x = np.diff(np.concatenate([[0], np.random.randn(n)]))
    return x * env(n, 0.001, rel) * amp


def saw(freq, dur, amp):
    n = int(dur * SR); tt = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * freq * k * tt) / k for k in range(1, 9)) * amp


bass = {"A": 55.0, "F": 43.65, "C": 65.41, "G": 49.0}
chords = {"A": [220, 261.6, 329.6], "F": [174.6, 220, 261.6], "C": [196, 261.6, 329.6], "G": [196, 246.9, 293.7]}
prog = ["A", "F", "C", "G"]
drop = offs[4]
for b in range(int(total / beat) + 2):
    st = b * beat; ch = prog[(b // 4) % 4]
    if st > total: break
    intro = st < offs[1] + 0.25
    build = drop - 4 * beat <= st < drop
    if build:
        k = int((st - (drop - 4 * beat)) / beat)
        for s in range(2 ** (k + 1)):
            add(noise_hit(0.2, 0.05, 0.35) * (0.4 + 0.15 * k), st + s * beat / 2 ** (k + 1))
    elif not intro:
        add(kick(), st)
        if b % 4 in (1, 3): add(noise_hit(0.2, 0.05, 0.35), st)
        add(saw(bass[ch], beat * 0.45, 0.10) * env(int(beat * 0.45 * SR), 0.005, 0.15), st + beat / 2)
    if not intro:
        add(noise_hit(0.05, 0.012, 0.18), st + beat / 2)
        if st > drop: add(noise_hit(0.05, 0.012, 0.12), st + beat * 0.75)
    if b % 4 == 0:
        dur = beat * 4
        pad = sum(saw(f, dur, 0.025) for f in chords[ch]) * env(int(dur * SR), 0.08)
        add(pad * (1.6 if intro else 1.0), st)
rl = 4 * beat; n = int(rl * SR); tt = np.arange(n) / SR
add(np.diff(np.concatenate([[0], np.random.randn(n)])) * (tt / rl) ** 2 * 0.25, drop - rl)
add(kick() * 1.2, drop); add(noise_hit(0.18, 0.06, 0.54), drop)
add(kick() * 1.2, offs[0] + 0.12); add(kick() * 1.2, offs[1] + 0.2)
fade_n = int(1.2 * SR); end_i = int(total * SR)
mix[end_i - fade_n:end_i] *= np.linspace(1, 0, fade_n); mix[end_i:] = 0
mix = np.tanh(mix * 1.4); mix /= np.max(np.abs(mix)) * 1.12
wav = os.path.join(W, "music.wav")
with wave.open(wav, "w") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

out = os.path.join(OUT, "UR_Canopy_pemasangan_kanopi_9x16.mp4")
run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-i", wav, "-filter_complex", ";".join(fc),
     "-map", "[v]", "-map", f"{len(segs)}:a", "-c:v", "libx264", "-preset", "slow", "-crf", "21",
     "-maxrate", "12M", "-bufsize", "24M", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
     "-t", str(total), "-movflags", "+faststart", out])
print("done", out, total)

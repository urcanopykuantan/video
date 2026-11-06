import subprocess, os, wave
import numpy as np

UP = "/root/.claude/uploads/7ad25e6e-7da5-536c-a48f-2ccd3a8b7c50/"
S = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(S, "work"); os.makedirs(W, exist_ok=True)
OUT = "/home/user/video/output"; os.makedirs(OUT, exist_ok=True)
BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
if not os.path.exists(BLACK): BLACK = BOLD
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FPS = 30
YEL = "0xFFC21A"

def run(cmd):
    print(" ".join(cmd)[:300]); subprocess.run(cmd, check=True)

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")

def alpha(a, b, f=0.3):
    # fade in at a, out at b
    return f"if(lt(t,{a}),0,if(lt(t,{a+f}),(t-{a})/{f},if(lt(t,{b-f}),1,if(lt(t,{b}),({b}-t)/{f},0))))"

def dt(text, font, size, x, y, a, b, color="white", box=None, border=None, shadow=True):
    s = f"drawtext=fontfile={font}:text='{esc(text)}':fontsize={size}:fontcolor={color}:x={x}:y={y}:alpha='{alpha(a,b)}'"
    if box: s += f":box=1:boxcolor={box}:boxborderw={border or 20}"
    if shadow and not box: s += ":shadowcolor=black@0.6:shadowx=3:shadowy=3"
    return s

def lower_third(step, desc, a, b):
    # yellow tag + white description on dark box, bottom-left
    return [
        dt(step, BLACK, 46, 90, "h-250", a, b, color="black", box=f"{YEL}@1", border="18|26"),
        dt(desc, BOLD, 58, 90, "h-165", a + 0.15, b, color="white", box="black@0.62", border="20|26"),
    ]

def center(text, size, y, a, b, font=BLACK, color="white"):
    return dt(text, font, size, "(w-text_w)/2", y, a, b, color=color)

# (file, start, src_len, speed, extra filters builder(out_dur) -> list)
segs = [
    ("ebaecb94-VID20261103121327.mp4", 0.3, 1.8, 1.0,
     lambda d: [center("DARI INI...", 150, "(h-text_h)/2", 0.1, d + 1)]),
    ("9022f23d-VID20261106115135.mp4", 3.0, 2.2, 1.0,
     lambda d: [center("...JADI INI!", 150, "(h-text_h)/2", 0.15, d + 1, color=YEL)]),
    ("ebaecb94-VID20261103121327.mp4", 0.0, 7.5, 1.5,
     lambda d: ["drawbox=x=0:y=0:w=iw:h=ih:color=black@0.35:t=fill:enable='lt(t,2.3)'",
                center("PROSES PEMASANGAN", 120, "h/2-140", 0.35, 2.3),
                center("KANOPI", 170, "h/2+0", 0.5, 2.3, color=YEL)]
               + lower_third("LANGKAH 1", "Susun rangka besi di tapak", 2.5, d - 0.1)),
    ("86c4e5b9-VID20261103121347.mp4", 0.0, 6.2, 1.25,
     lambda d: lower_third("LANGKAH 2", "Pasang & ketatkan setiap sambungan", 0.5, d - 0.1)),
    ("dba7b19c-VID20261103134353.mp4", 0.0, 8.1, 1.5,
     lambda d: lower_third("LANGKAH 3", "Rangka dinaikkan - kukuh & selamat", 0.5, d - 0.1)),
    ("9022f23d-VID20261106115135.mp4", 0.0, 6.7, 1.15,
     lambda d: lower_third("HASIL AKHIR", "Kanopi siap untuk majlis anda", 0.7, d - 0.1)),
    ("b046447d-VID20261106120834.mp4", 0.0, 5.9, 1.15,
     lambda d: [center("KEMAS  |  KUKUH  |  PROFESIONAL", 70, "h-190", 0.5, d - 0.1, font=BOLD)]),
    ("47cda38c-VID20261106115152.mp4", 0.0, 5.45, 1.0,
     lambda d: ["drawbox=x=0:y=0:w=iw:h=ih:color=black@0.5:t=fill:enable='gte(t,0.6)'",
                center("PERLUKAN KANOPI?", 130, "h/2-150", 0.8, d + 1, color=YEL),
                center("Hubungi kami untuk sebut harga", 70, "h/2+20", 1.2, d + 1, font=BOLD),
                center("Kanopi  -  Khemah  -  Pentas Acara", 52, "h/2+130", 1.6, d + 1, font=SEMI)]),
]
trans = [("fadewhite", 0.25), ("fadeblack", 0.4), ("smoothleft", 0.4), ("smoothleft", 0.4),
         ("fadewhite", 0.6), ("dissolve", 0.5), ("dissolve", 0.5)]

durs = []
for i, (f, ss, ln, sp, fx) in enumerate(segs):
    d = round(ln / sp, 3); durs.append(d)
    grade = "eq=contrast=1.08:saturation=1.22:brightness=0.01,unsharp=5:5:0.6"
    vf = ",".join([f"setpts=(PTS-STARTPTS)/{sp}", f"fps={FPS}", "scale=1920:1080:flags=lanczos",
                   "setsar=1", grade] + fx(d) + ["format=yuv420p"])
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(ln), "-i", UP + f, "-an",
         "-vf", vf, "-t", str(d), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         os.path.join(W, f"s{i}.mp4")])

# xfade chain
inputs, fc, offs, acc = [], [], [], 0.0
for i in range(len(segs)): inputs += ["-i", os.path.join(W, f"s{i}.mp4")]
prev = "[0:v]"; acc = durs[0]
for i, (tn, td) in enumerate(trans):
    off = round(acc - td, 3); offs.append(off)
    lab = f"[x{i}]"
    fc.append(f"{prev}[{i+1}:v]xfade=transition={tn}:duration={td}:offset={off}{lab}")
    prev = lab; acc = off + durs[i + 1]
total = round(acc, 3)
fc.append(f"{prev}fade=t=out:st={total-0.8}:d=0.8,format=yuv420p[v]")
print("durations", durs, "offsets", offs, "total", total)

# ---------- music synth ----------
SR = 44100; BPM = 120; beat = 60 / BPM
N = int(SR * (total + 0.5)); t = np.arange(N) / SR
mix = np.zeros(N)
def add(sig, start):
    i = int(start * SR); e = min(N, i + len(sig))
    if i < N: mix[i:e] += sig[: e - i]
def env(n, a=0.005, r=None):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: e *= np.exp(-np.arange(n) / (r * SR))
    return e
def kick():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 50 + 110 * np.exp(-tt * 30); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 9) * 0.9
def hat(o=False):
    n = int((0.18 if o else 0.05) * SR); x = np.random.randn(n)
    x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.001, 0.06 if o else 0.012) * 0.18
def clap():
    n = int(0.2 * SR); x = np.random.randn(n); x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.002, 0.05) * 0.35
def saw(freq, dur, amp):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * freq * k * tt) / k for k in range(1, 9))
    return s * amp
notes = {"A": 55.0, "F": 43.65, "C": 65.41, "G": 49.0}
chords = {"A": [220, 261.6, 329.6], "F": [174.6, 220, 261.6], "C": [196, 261.6, 329.6], "G": [196, 246.9, 293.7]}
prog = ["A", "F", "C", "G"]
reveal = offs[3] + trans[3][1]  # start of the 'raise' segment -> build energy
drop = offs[4]                   # final reveal
nb = int(total / beat) + 2
for b in range(nb):
    st = b * beat; bar = b // 4; ch = prog[bar % 4]
    if st > total: break
    intro = st < offs[1] + 0.25
    build = drop - 4 * beat <= st < drop
    if not intro and not build: add(kick(), st)
    if build:  # snare roll before reveal
        k = int((st - (drop - 4 * beat)) / beat)
        for s in range(2 ** (k + 1)):
            add(clap() * (0.4 + 0.15 * k), st + s * beat / 2 ** (k + 1))
    if not intro and b % 4 in (1, 3) and not build: add(clap(), st)
    if not intro: add(hat(), st + beat / 2); add(hat(), st + beat / 4 * 3) if st > reveal else None
    # bass offbeat 8ths
    if not intro and not build:
        for h in (0.5,):
            bs = saw(notes[ch], beat * 0.45, 0.10) * env(int(beat * 0.45 * SR), 0.005, 0.15)
            add(bs, st + h * beat)
    # pad
    if b % 4 == 0:
        dur = beat * 4
        pad = sum(saw(f, dur, 0.025) for f in chords[ch]) * env(int(dur * SR), 0.08)
        if intro: pad *= 1.6
        add(pad, st)
# riser into reveal
rl = 4 * beat; n = int(rl * SR); tt = np.arange(n) / SR
noise = np.random.randn(n); noise = np.diff(np.concatenate([[0], noise]))
add(noise * (tt / rl) ** 2 * 0.25, drop - rl)
add(kick() * 1.2, drop); add(hat(True) * 3, drop)
# impact at hook
add(kick() * 1.2, offs[0] + 0.12); add(kick() * 1.2, offs[1] + 0.2)
# simple lowpass on pad/mix: one-pole smoothing for warmth
fade_n = int(1.2 * SR); end_i = int(total * SR)
mix[end_i - fade_n:end_i] *= np.linspace(1, 0, fade_n); mix[end_i:] = 0
mix = np.tanh(mix * 1.4); mix /= np.max(np.abs(mix)) * 1.12
wav = os.path.join(W, "music.wav")
with wave.open(wav, "w") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

land = os.path.join(OUT, "kanopi_landscape_1080p.mp4")
run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-i", wav, "-filter_complex", ";".join(fc),
     "-map", "[v]", "-map", f"{len(segs)}:a", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
     "-c:a", "aac", "-b:a", "192k", "-t", str(total), "-movflags", "+faststart", land])

vert = os.path.join(OUT, "kanopi_vertical_reels_tiktok.mp4")
run(["ffmpeg", "-v", "error", "-y", "-i", land, "-filter_complex",
     "[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.12[bg];"
     "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"
     f"drawtext=fontfile={BLACK}:text='PROSES PASANG':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=330:shadowcolor=black@0.6:shadowx=3:shadowy=3,"
     f"drawtext=fontfile={BLACK}:text='KANOPI':fontsize=130:fontcolor={YEL}:x=(w-text_w)/2:y=440:shadowcolor=black@0.6:shadowx=3:shadowy=3,"
     f"drawtext=fontfile={BOLD}:text='Tonton sampai habis':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=1500:alpha=0.9,"
     "format=yuv420p[v]",
     "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
     "-c:a", "copy", "-movflags", "+faststart", vert])
print("done", total)

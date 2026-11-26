"""Images (Gemini -> Pollinations -> Pexels photo), Ken Burns video via ffmpeg, thumbnail."""
import base64, io, os, re, subprocess, time, random, math, requests
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

STYLE = "Pixar-style 3D animated movie render, vibrant colors, soft sunny lighting, cute, kid-friendly, high detail"
IMG_MODELS = [m.strip() for m in os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image,gemini-2.0-flash-preview-image-generation").split(",") if m.strip()]
PEXELS = os.getenv("PEXELS_API_KEY", "")
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansArabic-Black.ttf")
FONT_URL = "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/NotoSansArabic/hinted/ttf/NotoSansArabic-Black.ttf"


def ensure_font():
    if os.path.exists(FONT) and os.path.getsize(FONT) > 100000:
        return FONT
    sysf = "/usr/share/fonts/truetype/noto/NotoSansArabic-Black.ttf"
    if os.path.exists(sysf):
        return sysf
    os.makedirs(os.path.dirname(FONT), exist_ok=True)
    with open(FONT, "wb") as f:
        f.write(requests.get(FONT_URL, timeout=60).content)
    return FONT
W, H = 1280, 720
_gemini_ok = True
SEED = 0  # per-story seed set by the uploader: same seed + same character text = more consistent look


def _fit_169(img):
    img = img.convert("RGB")
    w, h = img.size
    t = W / H
    if w / h > t:
        nw = int(h * t); img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / t); img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return img.resize((W, H), Image.LANCZOS)


def _gemini_image(prompt):
    global _gemini_ok
    key = os.environ.get("GEMINI_API_KEY")
    if not (_gemini_ok and key):
        return None
    for m in IMG_MODELS:
        try:
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                              params={"key": key}, timeout=120,
                              json={"contents": [{"parts": [{"text": prompt}]}],
                                    "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}})
            if r.status_code != 200:
                print(f"[img:gemini:{m}] HTTP {r.status_code} {r.text[:160]}")
                continue
            for p in r.json()["candidates"][0]["content"]["parts"]:
                d = p.get("inlineData") or p.get("inline_data")
                if d:
                    return Image.open(io.BytesIO(base64.b64decode(d["data"])))
        except Exception as e:
            print(f"[img:gemini:{m}] {e}")
    _gemini_ok = False
    print("[img] Gemini image unavailable, using fallback for the rest of the run")
    return None


def _pollinations(prompt, tries=5):
    for i in range(tries):
        seed = SEED if SEED else random.randint(1, 10**6)
        try:
            r = requests.get("https://image.pollinations.ai/prompt/" + requests.utils.quote(prompt[:900]),
                             params={"width": 1280, "height": 720, "model": "flux", "nologo": "true", "seed": seed, "negative_prompt": "photo, realistic, macro, extreme close-up, creepy, scary, deformed, text"},
                             timeout=150)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                w, h = img.size
                return img.crop((0, 0, w, int(h * 0.93)))  # trim the corner watermark
            m = re.search(r"[Rr]etry after (\d+)", r.text)
            wait = int(m.group(1)) + 2 if m else 20
            print(f"[img:pollinations] HTTP {r.status_code}, waiting {wait}s")
            time.sleep(min(wait, 60))
        except Exception as e:
            print("[img:pollinations]", e); time.sleep(10)
    return None


def _pexels_photo(q):
    try:
        r = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": PEXELS},
                         params={"query": q, "per_page": 8, "orientation": "landscape"}, timeout=30)
        ph = r.json().get("photos", [])
        if ph:
            u = random.choice(ph)["src"]["large2x"]
            return Image.open(io.BytesIO(requests.get(u, timeout=60).content))
    except Exception as e:
        print("[img:pexels]", e)
    return None


def make_image(scene_prompt, character, search, path, fallback=None):
    prompt = (f"Pixar-style 3D animated cartoon character, cartoon not photo, not realistic, big friendly smile, {character + ', ' if character else ''}"
              f"{scene_prompt}. {STYLE}. Medium or wide shot, whole character visible, no macro, no extreme close-up")
    img = _gemini_image(prompt) or _pollinations(prompt)
    if img is None and fallback and os.path.exists(fallback):
        img = Image.open(fallback)  # reuse the previous scene art rather than an unrelated stock photo
    if img is None:
        img = _pexels_photo(search or "cute animals")
    if img is None:
        img = Image.new("RGB", (W, H), (255, 214, 120))
    img = _fit_169(img)
    img.save(path, quality=93)
    return path


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-800:])
    return p.stdout


def audio_duration(path):
    return float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).strip())


def vertical_still(src, dst):
    """9:16 frame: blurred cover background + the 16:9 art centered."""
    im = Image.open(src).convert("RGB")
    bg = im.resize((2276, 1280)).filter(ImageFilter.GaussianBlur(28))
    bg = bg.crop(((bg.width - 720) // 2, 0, (bg.width - 720) // 2 + 720, 1280))
    fg = im.resize((720, 405), Image.LANCZOS)
    bg.paste(fg, (0, (1280 - 405) // 2))
    bg.save(dst, quality=92)


def scene_clip(img, dur, out, size, idx):
    """Slow Ken Burns zoom/pan on a still; dur in seconds."""
    w, h = size
    frames = max(int(dur * 24), 24)
    big = f"scale={w*2}:{h*2}:flags=lanczos"
    z = 0.0007
    if idx % 2 == 0:
        zp = f"zoompan=z='min(1+{z}*on,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps=24"
    else:
        zp = f"zoompan=z='max(1.2-{z}*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps=24"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", img, "-vf", f"{big},{zp},format=yuv420p",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-t", f"{dur:.3f}", out])



# ---------------------------------------------------------------- parallax animation
_rembg_session = None


def cutout(img_path):
    """Split a scene into (background with the subject removed, subject RGBA) or (img, None) if segmentation is unusable."""
    global _rembg_session
    if os.path.exists(img_path + ".fg.png"):  # vector scenes ship their own layers
        return Image.open(img_path + ".bg.png").convert("RGB"), Image.open(img_path + ".fg.png").convert("RGBA")
    im = Image.open(img_path).convert("RGB")
    try:
        from rembg import remove, new_session
        if _rembg_session is None:
            _rembg_session = new_session("u2netp")
        fg = remove(im, session=_rembg_session)
        a = np.array(fg.split()[3]).astype("float32") / 255.0
        cov = float((a > 0.5).mean())
        if cov < 0.03 or cov > 0.75:
            return im, None
        a_img = fg.split()[3].filter(ImageFilter.GaussianBlur(1.2))
        fg.putalpha(a_img)
        # background: fill the subject hole with a mask-aware blur of its surroundings
        m = Image.fromarray((a > 0.1).astype("uint8") * 255).filter(ImageFilter.MaxFilter(15))
        mm = np.array(m).astype("float32")[..., None] / 255.0
        arr = np.array(im).astype("float32")
        keep = 1.0 - mm
        num = np.array(Image.fromarray((arr * keep).astype("uint8")).filter(ImageFilter.GaussianBlur(40))).astype("float32")
        den = np.array(Image.fromarray((keep[..., 0] * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(40))).astype("float32")[..., None] / 255.0
        fill = num / np.maximum(den, 0.02)
        fill = np.clip(fill, 0, 255)
        soft = np.array(m.filter(ImageFilter.GaussianBlur(6))).astype("float32")[..., None] / 255.0
        bg = arr * (1 - soft) + fill * soft
        return Image.fromarray(bg.astype("uint8")), fg
    except Exception as e:
        print("cutout failed:", e)
        return im, None


def _aff(img, size, z, cx, cy, tx, ty, rot=0.0, res=Image.BICUBIC):
    """Zoom z and rotate (radians) about (cx,cy), then shift by (tx,ty)."""
    c, s_ = math.cos(rot), math.sin(rot)
    a, b, d, e = c / z, s_ / z, -s_ / z, c / z
    px, py = cx + tx, cy + ty
    return img.transform(size, Image.AFFINE, (a, b, cx - (a * px + b * py), d, e, cy - (d * px + e * py)), res)


def _title_overlay(title, size):
    w, h = size
    d0 = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    words = title.split()
    lines = [title] if len(words) <= 3 else [" ".join(words[:(len(words) + 1) // 2]), " ".join(words[(len(words) + 1) // 2:])]
    fs = int(h * 0.15)
    while fs > 30:
        f = ImageFont.truetype(ensure_font(), fs, layout_engine=ImageFont.Layout.BASIC)
        if max(d0.textlength(_ar(l), font=f) for l in lines) <= w * 0.86:
            break
        fs -= 4
    lh = int(fs * 1.4)
    bh = lh * len(lines) + int(fs * 0.5)
    ov = Image.new("RGBA", (w, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((int(w * 0.04), 0, int(w * 0.96), bh - 1), radius=int(fs * 0.5), fill=(120, 24, 32, 235), outline=(232, 220, 192, 255), width=6)
    y = int(fs * 0.22)
    for l in lines:
        t = _ar(l); tw = d.textlength(t, font=f)
        d.text(((w - tw) / 2, y), t, font=f, fill=(240, 228, 196), stroke_width=max(5, fs // 12), stroke_fill=(15, 8, 8))
        y += lh
    return ov


def parallax_clip(bg, fg, dur, out, size, idx, title=None, fps=24, caption=None):
    """Animated scene: slow camera move on the background, stronger move + bobbing on the subject, drifting sparkles."""
    w, h = size
    frames = max(int(dur * fps), fps)
    bgp = bg.resize((int(w * 1.25), int(h * 1.25)), Image.LANCZOS)
    fgp = fg.resize(bgp.size, Image.LANCZOS) if fg is not None else None
    BW, BH = bgp.size
    rnd = random.Random(idx * 7919 + 13)
    mode = idx % 4  # camera pattern
    zin = mode in (0, 2)
    pan = [(-1, 0), (1, 0), (0, -1), (0, 1)][mode]
    sp = [(rnd.random() * w, rnd.random() * h, 0.3 + rnd.random() * 0.8, rnd.random() * 6.28, 4 + rnd.random() * 6) for _ in range(14)]
    cxf, cyf = BW / 2, BH / 2
    if fgp is not None:
        ys, xs = np.nonzero(np.array(fgp.split()[3]) > 128)
        if len(xs):
            cxf, cyf = float(xs.mean()), float(ys.mean())
    ov = _title_overlay(title, size) if (title and idx == 0) else None
    cap = _title_overlay(caption, (int(w * 0.8), h)).resize((int(w * 0.8), int(_title_overlay(caption, (int(w * 0.8), h)).height))) if caption else None
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    try:
        for n in range(frames):
            p = n / max(frames - 1, 1)
            t = n / fps
            e = p * p * (3 - 2 * p)
            zb = 1.0 + 0.10 * (e if zin else 1 - e)
            tx, ty = pan[0] * (e - 0.5) * 0.06 * BW, pan[1] * (e - 0.5) * 0.06 * BH
            # window of size (w,h) from the center of the oversized plate
            ox, oy = (BW - w) / 2, (BH - h) / 2
            frame = _aff(bgp, (w, h), zb, BW / 2 - ox, BH / 2 - oy, tx, ty) if False else None
            canvas_bg = _aff(bgp, (BW, BH), zb, BW / 2, BH / 2, tx, ty).crop((int(ox), int(oy), int(ox) + w, int(oy) + h))
            if fgp is not None:
                zf = zb + 0.05 + 0.05 * (1 if zin else -1) * (e - 0.5)
                bob = 9 * math.sin(2 * math.pi * t / 2.0)
                sway = 6 * math.sin(2 * math.pi * t / 3.3)
                rot = math.radians(1.6) * math.sin(2 * math.pi * t / 2.6)
                f2 = _aff(fgp, (BW, BH), zf, cxf, cyf, tx * 1.7 + sway, ty * 1.7 + bob, rot).crop((int(ox), int(oy), int(ox) + w, int(oy) + h))
                canvas_bg.paste(f2.convert("RGB"), mask=f2.split()[3])
            frame = canvas_bg.convert("RGBA")
            sl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            dd = ImageDraw.Draw(sl)
            for (x0, y0, spd, ph, r) in sp:
                x = (x0 + 25 * math.sin(t * 0.9 + ph)) % w
                y = (y0 - spd * 40 * t) % h
                a = int(140 + 100 * math.sin(t * 3 + ph))
                rr = r * (0.7 + 0.3 * math.sin(t * 2.4 + ph))
                dd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 220, max(0, min(255, a))))
            frame = Image.alpha_composite(frame, sl)
            if ov is not None and t < 2.8:
                pop = min(1.0, t / 0.35)
                sc = 0.6 + 0.4 * (1 - (1 - pop) ** 3) + 0.04 * math.sin(t * 9) * (1 - pop)
                al = 1.0 if t < 2.2 else max(0.0, (2.8 - t) / 0.6)
                o2 = ov.resize((max(1, int(ov.width * sc)), max(1, int(ov.height * sc))), Image.LANCZOS)
                if al < 1:
                    o2.putalpha(o2.split()[3].point(lambda v: int(v * al)))
                frame.alpha_composite(o2, ((w - o2.width) // 2, int(h * 0.04)))
            if cap is not None and t > 0.6:
                pc = min(1.0, (t - 0.6) / 0.3)
                sc2 = 0.7 * (0.85 + 0.15 * (1 - (1 - pc) ** 3))
                c2 = cap.resize((max(1, int(cap.width * sc2)), max(1, int(cap.height * sc2))), Image.LANCZOS)
                frame.alpha_composite(c2, ((w - c2.width) // 2, int(h * 0.97) - c2.height))
            ff.stdin.write(frame.convert("RGB").tobytes())
    finally:
        ff.stdin.close(); ff.wait()
    if ff.returncode:
        raise RuntimeError("ffmpeg parallax failed")


def _scene_job(args):
    img, dur, seg, size, idx, title, caption = args
    try:
        bg, fg = cutout(img)
        parallax_clip(bg, fg, dur, seg, size, idx, title, caption=caption)
    except Exception as e:
        print("parallax failed for scene", idx, e, "- falling back to Ken Burns")
        scene_clip(img, dur, seg, size, idx)
    return seg


def assemble(scene_imgs, scene_audios, out, size, max_dur=None, workdir="out", animate=False, title=None, captions=None):
    """scene_audios: mp3 per scene. Image i lasts exactly as long as its narration (+0.5s pause)."""
    segs, auds, total, jobs = [], [], 0.0, []
    for i, (im, au) in enumerate(zip(scene_imgs, scene_audios)):
        d = audio_duration(au) + 0.5
        if max_dur and total >= max_dur:
            break
        seg = f"{workdir}/seg_{size[0]}_{i}.mp4"
        jobs.append((im, d, seg, size, i, title, (captions[i] if captions and i < len(captions) else None)))
        segs.append(seg); auds.append(au); total += d
    if animate:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 2)) as ex:
            list(ex.map(_scene_job, jobs))
    else:
        for (im, d, seg, sz, i, _t, _c) in jobs:
            scene_clip(im, d, seg, sz, i)
    lst = f"{workdir}/list_{size[0]}.txt"
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    vid = f"{workdir}/v_{size[0]}.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    # audio: each narration followed by 0.5s silence
    ins, fl = [], []
    for i, a in enumerate(auds):
        ins += ["-i", a]
        fl.append(f"[{i}:a]aresample=44100,apad=pad_dur=0.5[a{i}]")
    fl.append("".join(f"[a{i}]" for i in range(len(auds))) + f"concat=n={len(auds)}:v=0:a=1[aout]")
    wav = f"{workdir}/a_{size[0]}.m4a"
    _run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "aac", "-b:a", "128k", wav])
    try:
        mus = f"{workdir}/music_{size[0]}.wav"
        make_music(total, mus)
        mixed = f"{workdir}/mix_{size[0]}.m4a"
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-i", mus, "-filter_complex",
              "[1:a]volume=0.13[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0,volume=2,alimiter=limit=0.95[o]",
              "-map", "[o]", "-c:a", "aac", "-b:a", "160k", mixed])
        wav = mixed
    except Exception as e:
        print("music failed:", e)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-shortest"]
    if max_dur:
        cmd += ["-t", str(max_dur)]
    _run(cmd + [out])
    return total


def _ar(s):
    return get_display(arabic_reshaper.reshape(s))


def make_thumbnail(base_img_path, text, out):
    im = Image.open(base_img_path).convert("RGB").resize((W, H), Image.LANCZOS)
    # darken bottom for legibility
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(max(0, (y - H * 0.45) / (H * 0.55)) * 190))
    shade = Image.new("RGB", (W, H), (20, 10, 40))
    im = Image.composite(shade, im, grad.resize((W, H)))
    d = ImageDraw.Draw(im)
    words = text.split()
    lines = [text] if len(words) <= 2 else [" ".join(words[:len(words) // 2 + len(words) % 2]), " ".join(words[len(words) // 2 + len(words) % 2:])]
    size = 125
    while size > 60:
        f = ImageFont.truetype(ensure_font(), size, layout_engine=ImageFont.Layout.BASIC)
        if max(d.textlength(_ar(l), font=f) for l in lines) <= W - 120:
            break
        size -= 6
    lh = int(size * 1.35)
    y = H - 40 - lh * len(lines)
    for l in lines:
        t = _ar(l)
        tw = d.textlength(t, font=f)
        d.text(((W - tw) / 2, y), t, font=f, fill=(240, 228, 196), stroke_width=max(6, size // 12), stroke_fill=(120, 24, 32))
        y += lh
    im.save(out, quality=92)
    return out


def make_music(duration, path, bpm=100):
    """Cheerful original marimba-style loop (C-Am-F-G), synthesized here, so there are no licensing issues."""
    import numpy as np, wave
    sr = 44100
    beat = 60.0 / bpm
    n = int((duration + 1) * sr)
    out = np.zeros(n + sr * 3)
    def hz(semi):  # semitones from C4
        return 261.63 * 2 ** (semi / 12)
    def pluck(f, length, amp):
        t = np.arange(int(length * sr)) / sr
        s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 9) + 0.15 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 14)
        env = np.minimum(t / 0.006, 1) * np.exp(-t * 5.5)
        return amp * s * env
    chords = [(0, [0, 4, 7]), (-3, [-3, 0, 4]), (-7, [-7, -3, 0]), (-5, [-5, -1, 2])]
    motif = [0, 1, 2, 1, 2, 1, 0, 1]  # index into chord tones (+ octave), eight eighth-notes per bar of 4 beats
    pos, bar = 0.0, 0
    total = duration + 1
    while pos < total:
        root, tones = chords[bar % 4]
        for i, k in enumerate(motif):
            st = int((pos + i * beat / 2) * sr)
            semi = tones[k % 3] + (12 if (k + bar) % 5 == 4 else 12 if i % 4 == 3 else 0) + 12
            snd = pluck(hz(semi), 0.7, 0.30)
            if st + len(snd) < len(out): out[st:st + len(snd)] += snd
        for b in range(4):
            st = int((pos + b * beat) * sr)
            snd = pluck(hz(root - 12), 0.9, 0.35 if b in (0, 2) else 0.2)
            if st + len(snd) < len(out): out[st:st + len(snd)] += snd
        pos += 4 * beat; bar += 1
    out = out[:n]
    fade = int(3 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype("<i2").tobytes())
    return path

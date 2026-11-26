"""Case-file scenes (dark noir paper look). Pure PIL, no network, no photos of real people.
Each scene writes path (composite jpg), path+'.bg.png', path+'.fg.png' for the parallax camera (same contract as kids_vector)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import kids_media as km

INK = (28, 24, 22); PAPER = (232, 220, 192); RED = (176, 32, 38); GOLD = (222, 180, 90); NAVY = (14, 20, 34)


def _ar(s):
    return get_display(arabic_reshaper.reshape(s))


def _font(size):
    return ImageFont.truetype(km.ensure_font(), size, layout_engine=ImageFont.Layout.BASIC)


def _bg(idx, W, H):
    rnd = random.Random(7100 + idx)
    im = Image.new("RGBA", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(H):  # slow vertical gradient
        t = y / H
        d.line((0, y, W, y), fill=(int(14 + 22 * t), int(20 + 18 * t), int(34 + 22 * t), 255))
    for _ in range(26):  # faint corkboard strings / pins
        x1, y1 = rnd.randint(0, W), rnd.randint(0, H)
        x2, y2 = rnd.randint(0, W), rnd.randint(0, H)
        d.line((x1, y1, x2, y2), fill=(150, 40, 45, 40), width=2)
    for _ in range(90):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(1, 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rnd.randint(8, 30)))
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * .25, -H * .35, W * 1.25, H * 1.35), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    return Image.composite(im, dark, vig)


def _icon(d, kind, cx, cy, s):
    """simple flat icons, s = size"""
    L = max(6, s // 14)
    if kind == "magnifier":
        d.ellipse((cx - s * .45, cy - s * .5, cx + s * .25, cy + s * .2), outline=INK, width=L * 2, fill=(190, 225, 235))
        d.line((cx + s * .2, cy + s * .15, cx + s * .5, cy + s * .5), fill=INK, width=L * 3)
    elif kind == "clock":
        d.ellipse((cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), outline=INK, width=L * 2, fill=(250, 245, 230))
        d.line((cx, cy, cx, cy - s * .32), fill=INK, width=L); d.line((cx, cy, cx + s * .22, cy + s * .08), fill=RED, width=L)
    elif kind == "pin":
        d.ellipse((cx - s * .3, cy - s * .5, cx + s * .3, cy + s * .1), fill=RED, outline=INK, width=L)
        d.polygon([(cx - s * .22, cy), (cx + s * .22, cy), (cx, cy + s * .5)], fill=RED)
        d.ellipse((cx - s * .1, cy - s * .3, cx + s * .1, cy - s * .1), fill=PAPER)
    elif kind == "scale":
        d.line((cx, cy - s * .5, cx, cy + s * .45), fill=INK, width=L * 2); d.line((cx - s * .5, cy - s * .3, cx + s * .5, cy - s * .3), fill=INK, width=L * 2)
        for sx in (-1, 1):
            x = cx + sx * s * .5
            d.line((x, cy - s * .3, x - s * .22, cy + s * .1), fill=INK, width=L); d.line((x, cy - s * .3, x + s * .22, cy + s * .1), fill=INK, width=L)
            d.pieslice((x - s * .25, cy - s * .05, x + s * .25, cy + s * .3), 0, 180, fill=GOLD, outline=INK, width=L // 2)
        d.rectangle((cx - s * .25, cy + s * .42, cx + s * .25, cy + s * .5), fill=INK)
    elif kind == "dna":
        for i in range(14):
            t = i / 13 * math.pi * 2
            y = cy - s * .5 + i * s / 13
            x1, x2 = cx + math.sin(t) * s * .3, cx - math.sin(t) * s * .3
            d.line((x1, y, x2, y), fill=(120, 120, 130), width=L // 2 + 1)
            d.ellipse((x1 - L, y - L, x1 + L, y + L), fill=(60, 150, 200)); d.ellipse((x2 - L, y - L, x2 + L, y + L), fill=RED)
    elif kind == "document":
        d.rectangle((cx - s * .36, cy - s * .5, cx + s * .36, cy + s * .5), fill=(250, 248, 240), outline=INK, width=L)
        for i in range(5):
            yy = cy - s * .3 + i * s * .15
            d.line((cx - s * .24, yy, cx + s * (.24 if i % 2 == 0 else .1), yy), fill=(90, 90, 100), width=L // 2 + 1)
    elif kind == "handcuffs":
        for sx in (-1, 1):
            d.ellipse((cx + sx * s * .27 - s * .25, cy - s * .25, cx + sx * s * .27 + s * .25, cy + s * .25), outline=INK, width=L * 2)
        d.line((cx - s * .05, cy, cx + s * .05, cy), fill=INK, width=L * 2)
    else:  # folder
        d.rectangle((cx - s * .5, cy - s * .35, cx + s * .5, cy + s * .4), fill=(220, 175, 90), outline=INK, width=L)
        d.rectangle((cx - s * .5, cy - s * .45, cx - s * .1, cy - s * .3), fill=(220, 175, 90), outline=INK, width=L)


def case_scene(idx, on_screen, kind, date_label, path, W=1280, H=720, big=False):
    S = 2; w, h = W * S, H * S
    bg = _bg(idx, W, H).resize((w, h), Image.LANCZOS)
    fg = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(fg)
    # paper card (slightly rotated)
    card = Image.new("RGBA", (int(w * .62), int(h * .56)), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((8, 8, card.width - 8, card.height - 8), radius=26, fill=PAPER + (255,), outline=INK, width=6)
    for y in range(60, card.height - 40, 46):
        cd.line((50, y, card.width - 50, y), fill=(190, 175, 140, 120), width=2)
    # icon left, text right
    _icon(cd, kind, int(card.width * .24), int(card.height * .5), int(card.height * .62))
    f = _font(150 if big else 120)
    txt = _ar(on_screen or "")
    maxw = int(card.width * .5)
    while f.size > 50 and cd.textlength(txt, font=f) > maxw:
        f = _font(f.size - 8)
    cd.text((int(card.width * .5), int(card.height * .5) - f.size // 2 - 30), txt, font=f, fill=INK)
    if date_label:
        f2 = _font(70); t2 = _ar(date_label)
        cd.text((int(card.width * .5), int(card.height * .5) + f.size // 2 + 10), t2, font=f2, fill=RED)
    card = card.rotate(-2.2 if idx % 2 else 1.8, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0)); shadow.paste((0, 0, 0, 140), mask=card.split()[3]); shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    cx, cy = (w - card.width) // 2, int(h * .12)
    fg.alpha_composite(shadow, (cx + 14, cy + 22)); fg.alpha_composite(card, (cx, cy))
    # red CASE FILE 71 stamp
    st = Image.new("RGBA", (int(w * .26), int(h * .12)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((4, 4, st.width - 4, st.height - 4), radius=12, outline=RED + (230,), width=8)
    sf = _font(int(st.height * .55)); t = _ar("الملف 71"); sd.text(((st.width - sd.textlength(t, font=sf)) / 2, st.height * .16), t, font=sf, fill=RED + (230,))
    st = st.rotate(9, resample=Image.BICUBIC, expand=True)
    fg.alpha_composite(st, (int(cx + card.width * .70), int(cy + card.height * .62)))
    inner = fg.resize((int(w * .76), int(h * .76)), Image.LANCZOS); fg = Image.new("RGBA", (w, h), (0, 0, 0, 0)); fg.alpha_composite(inner, (int(w * .12), int(h * .07)))
    comp = bg.copy(); comp.alpha_composite(fg)
    bgS = bg.resize((W, H), Image.LANCZOS); fgS = fg.resize((W, H), Image.LANCZOS); cS = comp.resize((W, H), Image.LANCZOS)
    cS.convert("RGB").save(path, quality=93); bgS.convert("RGB").save(path + ".bg.png"); fgS.save(path + ".fg.png")
    return path

"""File 71: Gemini case script -> edge-tts -> case-file scenes (parallax) -> dark ambient music -> YouTube (unlisted by default).
DRY_RUN=true builds everything, writes preview/, uploads nothing and does not use up a topic."""
import asyncio, json, os, sys, shutil, subprocess
import numpy as np
import edge_tts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kids_media as km
import case_visuals as cv
import case_generator as cg

VOICE = os.getenv("TTS_VOICE", "ar-EG-ShakirNeural")
RATE = os.getenv("TTS_RATE", "-5%")
PRIVACY = os.getenv("PRIVACY_STATUS", "unlisted")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"   # safe default: no upload
MAKE_SHORT = os.getenv("MAKE_SHORT", "false").lower() == "true"
OUT = "out"; os.makedirs(OUT, exist_ok=True)


def dark_music(duration, path):
    """Tense low ambient pad, synthesized (no licensing)."""
    import wave
    sr = 44100; n = int((duration + 1) * sr); t = np.arange(n) / sr
    out = np.zeros(n)
    for f, a in ((55.0, .5), (82.4, .3), (110.0, .2), (130.8, .12)):
        out += a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.1 * t))
    pulse = (np.sin(2 * np.pi * 1.0 * t) > 0.97).astype(float)
    out += 0.25 * np.convolve(pulse, np.exp(-np.arange(sr // 2) / 4000.0) * np.sin(2 * np.pi * 55 * np.arange(sr // 2) / sr), mode="same")
    fade = int(3 * sr); out[-fade:] *= np.linspace(1, 0, fade)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.8
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype("<i2").tobytes())
    return path


km.make_music = dark_music


async def tts_all(scenes):
    paths = []
    for i, s in enumerate(scenes):
        p = f"{OUT}/voice_{i:02d}.mp3"
        for a in range(3):
            try:
                await edge_tts.Communicate(s["narration"], VOICE, rate=RATE).save(p); break
            except Exception as e:
                print("tts retry", i, e)
                if a == 2: raise
                await asyncio.sleep(3)
        paths.append(p)
    return paths


def youtube():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                        scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def upload(yt, path, title, desc, tags):
    from googleapiclient.http import MediaFileUpload
    body = {"snippet": {"title": title[:100], "description": desc, "tags": tags, "categoryId": "25", "defaultLanguage": "ar", "defaultAudioLanguage": "ar"},
            "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": False}}
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(path, chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]


def main():
    d = cg.generate_case(); scenes = d["scenes"]; title = d["title"]
    print("Case:", title, "| scenes:", len(scenes))
    audios = asyncio.run(tts_all(scenes))
    imgs = [cv.case_scene(i, s.get("on_screen"), s.get("kind"), s.get("date_label"), f"{OUT}/scene_{i:02d}.jpg") for i, s in enumerate(scenes)]
    base = cv.case_scene(0, d.get("thumbnail_text") or title, "folder", "", f"{OUT}/thumb_base.jpg", big=True)
    thumb = km.make_thumbnail(base, d.get("thumbnail_text") or title, f"{OUT}/thumb.jpg")
    dur = km.assemble(imgs, audios, f"{OUT}/case.mp4", (1280, 720), workdir=OUT, animate=True, title=d.get("hook_title") or title, captions=None)
    print("video seconds:", round(dur))
    os.makedirs("preview", exist_ok=True); shutil.copy(thumb, "preview/thumb.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/case.mp4", "-vf", "fps=1/8,scale=320:-1,tile=4x3", "-frames:v", "1", "preview/contact.jpg"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/case.mp4", "-vf", "scale=640:-2", "-c:v", "libx264", "-crf", "30", "-c:a", "aac", "-b:a", "64k", "preview/case_small.mp4"], check=True)
    json.dump({k: d[k] for k in ("title", "description", "tags", "sources", "scenes")}, open("preview/script.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if DRY_RUN:
        print("DRY_RUN: skipping upload; topic not used up"); return
    yt = youtube()
    src = "\n".join(f"- {s}" for s in d.get("sources", []))
    desc = d["description"] + "\n\nالمصادر العامة:\n" + src + "\n\nاشترك لقضايا جديدة. #الملف_71"
    vid = upload(yt, f"{OUT}/case.mp4", title, desc, d.get("tags", [])[:12])
    print("Uploaded:", f"https://www.youtube.com/watch?v={vid}")
    cg.record_history(d["_topic"])
    try:
        from googleapiclient.http import MediaFileUpload
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb, mimetype="image/jpeg")).execute(); print("Thumbnail set")
    except Exception as e:
        print("Thumbnail failed:", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAILED:", e); sys.exit(1)

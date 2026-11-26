"""Gemini script writer for 60-90s closed-case videos (Arabic). Public sources only, never accuses unconvicted people."""
import json, os, re, time, requests

TOPICS_FILE = os.getenv("TOPICS_FILE", "topics.json")
HISTORY_FILE = os.getenv("HISTORY_FILE", "history.json")
MODELS = [m.strip() for m in os.getenv("GEMINI_MODEL", "gemini-2.5-flash,gemini-2.5-flash-lite,gemini-flash-latest").split(",") if m.strip()]
KINDS = "folder, magnifier, clock, pin, scale, dna, document, handcuffs"


def load_json(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def next_topic():
    t = load_json(TOPICS_FILE, {"queue": []})
    done = {h.get("id") for h in load_json(HISTORY_FILE, [])}
    if os.getenv("TOPIC_INDEX"):
        return t["queue"][int(os.getenv("TOPIC_INDEX"))], t.get("playlists", [])
    for q in t["queue"]:
        if q["id"] not in done and q.get("status") != "needs-topic":
            return q, t.get("playlists", [])
    raise RuntimeError("topic queue is empty: add topics to topics.json")


def record_history(topic):
    h = load_json(HISTORY_FILE, [])
    h.append({"id": topic["id"], "title": topic["title"]})
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h[-300:], f, ensure_ascii=False, indent=1)


def _call(model, prompt, key):
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", params={"key": key}, timeout=180,
                      json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.6, "responseMimeType": "application/json"}})
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def generate_case():
    key = os.environ["GEMINI_API_KEY"]
    topic, playlists = next_topic()
    prompt = f"""اكتب سكريبت فيديو قصير (60 إلى 90 ثانية) بالعربية الفصحى المبسطة عن قضية جنائية مغلقة وموثقة: {topic['title']}.
القواعد الصارمة: اعتمد فقط على وقائع منشورة علنيا وموثقة في مصادر موثوقة (أحكام قضائية، صحافة معروفة، وثائق رسمية). لا تخترع تفاصيل. إذا لم تكن متأكدا من معلومة فاحذفها أو قل "بحسب التقارير". لا تسمّ أي شخص لم تثبت إدانته بحكم نهائي، ويمكن ذكر المدانين بحكم نهائي والضحايا المعروفين علنا باحترام، بدون وصف مروّع. لا عنف تفصيلي ولا ألفاظ جارحة.
البنية: مشهد 1 هوك قوي في أول 3 ثوان (سؤال أو مفارقة)، ثم ما حدث، ثم اللغز أو العقبة، ثم كيف انكشفت القضية أو اتحلت (الأدلة/التكنولوجيا)، ثم الحكم أو النتيجة، ثم خاتمة قصيرة بسؤال يشجع على التعليق.
8 إلى 10 مشاهد، كل مشهد من 12 إلى 24 كلمة. لكل مشهد: narration، on_screen (نص قصير أقل من 4 كلمات يظهر على الشاشة)، date_label (تاريخ أو سنة إن وجدت وإلا فارغ)، kind (واحد من: {KINDS})، 
رجّع JSON فقط بالمفاتيح: title (عنوان جذاب بدون تضليل)، description (3 أسطر)، tags (8 كلمات)، hook_title (2 إلى 5 كلمات)، thumbnail_text (2 إلى 4 كلمات)، sources (قائمة 2 إلى 4 مصادر عامة بالاسم)، scenes."""
    last = None
    for model in MODELS:
        for t in range(4):
            try:
                data = json.loads(re.sub(r"^```json|```$", "", _call(model, prompt, key).strip()).strip())
                scenes = [s for s in data["scenes"] if s.get("narration", "").strip()]
                if len(scenes) < 7:
                    raise ValueError("too few scenes")
                words = sum(len(s["narration"].split()) for s in scenes)
                if not 110 <= words <= 260:
                    raise ValueError(f"length off: {words} words")
                for s in scenes:
                    if s.get("kind") not in KINDS.replace(" ", "").split(","):
                        s["kind"] = "folder"
                data["scenes"] = scenes; data["_topic"] = topic; data["_playlists"] = playlists
                return data
            except Exception as e:
                last = e; print(f"[gemini:{model}] {e}"); time.sleep(8 * (t + 1))
    raise RuntimeError(f"case generation failed: {last}")

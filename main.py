import os, logging, asyncio, re, sqlite3, time
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Libraries needed to "read" text written inside images (OCR)
import pytesseract
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
IS_TESTING = os.environ.get("TEST_MODE", "false").lower() == "true"

if IS_TESTING:
    SOURCE_CHATS = [int(i.strip()) for i in os.environ.get("SOURCE_TEST_ID", "").split(",") if i.strip()]
    TARGET = int(os.environ.get("TARGET_TEST_ID", "0"))
else:
    SOURCE_CHATS = [int(i.strip()) for i in os.getenv("SOURCE_PUBLIC_ID", "").split(",") if i.strip()]
    TARGET = -1001752144165

DB_FILE = "/data/bot_data.db" if os.path.isdir("/data") else "bot_data.db"

# 🔥 HARD LOCK SYSTEM: Ek message ID ko ek baar mein ek hi baar process karne ke liye
active_locks = set()

# Words to look for INSIDE images (screenshots). Add/remove words here anytime.
OCR_BLOCKED_KEYWORDS = [
    "kapil verma",
    "sg options",
    "sg cash",
    "sebi registered ra",
]

# --- DB FUNCTIONS ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS mapping (src_id INTEGER PRIMARY KEY, tgt_id INTEGER, last_text TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS blocked_msgs (src_id INTEGER PRIMARY KEY)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mapping_src_id ON mapping(src_id)")
    conn.commit()
    conn.close()

def save_mapping(src_id, tgt_id, text):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT OR REPLACE INTO mapping VALUES (?, ?, ?)", (src_id, tgt_id, text))
    conn.commit()
    conn.close()

def save_blocked(src_id):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT OR REPLACE INTO blocked_msgs VALUES (?)", (src_id,))
    conn.commit()
    conn.close()

def is_parent_blocked(src_id):
    if not src_id: return False
    conn = sqlite3.connect(DB_FILE)
    res = conn.execute("SELECT src_id FROM blocked_msgs WHERE src_id = ?", (src_id,)).fetchone()
    conn.close()
    return True if res else False

def get_mapping(src_id):
    conn = sqlite3.connect(DB_FILE)
    res = conn.execute("SELECT tgt_id, last_text FROM mapping WHERE src_id = ?", (src_id,)).fetchone()
    conn.close()
    return res if res else (None, None)

def delete_mapping(src_id):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM mapping WHERE src_id = ?", (src_id,))
    conn.execute("DELETE FROM blocked_msgs WHERE src_id = ?", (src_id,))
    conn.commit()
    conn.close()

init_db()
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# --- SMART CLEANING ---
def clean_text(text):
    if not text: return ""
    lines = text.split('\n')
    unwanted = ["hare krishna", "finance with sunil", "stock gainers", "sebi registered", "prime membership"]
    cleaned = [l for l in lines if not any(p in l.lower() for p in unwanted)]
    text = re.sub(r'@\S+', '', '\n'.join(cleaned))
    return text.strip()

# --- UPDATED BLOCKING ---
# 🆕 CHANGED: Instead of listing every promo domain by name (twitter.com, bit.ly, etc -
# which breaks the moment someone posts a NEW domain like cosmofeed.com or revlu.in),
# this now blocks ANY http:// or https:// link, any t.me/ link, and any wa.me/ link,
# no matter what the domain is. This is future-proof against new domains being used.
def is_blocked(msg):
    if msg.reply_to_msg_id and is_parent_blocked(msg.reply_to_msg_id): return True

    text = (msg.text or "").lower()

    # Catches ANY link starting with http:// or https:// (any domain whatsoever),
    # plus Telegram invite links (t.me/...) and WhatsApp links (wa.me/...) even
    # without the http prefix, plus bare +91 phone numbers.
    promo_patterns = r'(https?://\S+|t\.me/\S+|wa\.me/\S+|\+91[\s\-]?\d{5,})'
    if re.search(promo_patterns, text): return True

    promo_kws = ["advisory", "limited seats", "kapil verma", "sg cash", "discount offer"]
    if any(kw in text for kw in promo_kws): return True

    if msg.forward and msg.forward.chat:
        fwd_title = (msg.forward.chat.title or "").lower()
        if any(x in fwd_title for x in ["sg cash", "sebi", "kapil"]): return True
    return False

# Reads the text written INSIDE a photo and checks it against OCR_BLOCKED_KEYWORDS.
def image_has_blocked_text(path):
    try:
        img = Image.open(path)
        extracted_text = pytesseract.image_to_string(img).lower()
        for keyword in OCR_BLOCKED_KEYWORDS:
            if keyword in extracted_text:
                logging.info(f"🛡️ OCR blocked image - found keyword: '{keyword}'")
                return True
        return False
    except Exception as e:
        logging.error(f"OCR check failed (image was still allowed through): {e}")
        return False

# --- FIXED MIRROR ENGINE ---
async def process_msg(msg, is_edit=False):
    if msg.chat_id not in SOURCE_CHATS: return

    if msg.id in active_locks:
        logging.info(f"🛡️ Duplicate network signal dropped for ID: {msg.id}")
        return

    active_locks.add(msg.id)

    downloaded_path = None
    try:
        tgt_id, last_text = get_mapping(msg.id)

        if not is_edit and tgt_id is not None:
            is_edit = True

        if is_blocked(msg):
            save_blocked(msg.id)
            return

        text = clean_text(msg.text)
        reply_to = None
        if msg.reply_to_msg_id:
            reply_to, _ = get_mapping(msg.reply_to_msg_id)

        if msg.media and msg.photo:
            downloaded_path = await client.download_media(msg)
            if downloaded_path and image_has_blocked_text(downloaded_path):
                save_blocked(msg.id)
                return

        # CASE 1: NAYA MESSAGE
        if tgt_id is None and not is_edit:
            if not text and not msg.media: return

            if msg.media:
                path = downloaded_path or await client.download_media(msg)
                sent = await client.send_file(TARGET, path, caption=text, reply_to=reply_to)
                if path and os.path.exists(path): os.remove(path)
                downloaded_path = None
            else:
                sent = await client.send_message(TARGET, text, link_preview=False, reply_to=reply_to)

            if sent:
                save_mapping(msg.id, sent.id, text)

        # CASE 2: EDIT MESSAGE
        elif tgt_id is not None:
            last_text_str = last_text if last_text is not None else ""
            if last_text_str != text:
                try:
                    await client.edit_message(TARGET, tgt_id, text, link_preview=False)
                    save_mapping(msg.id, tgt_id, text)
                except Exception as e:
                    logging.error(f"Edit Failed: {e}")

    except Exception as e:
        logging.error(f"Error in engine: {e}")
    finally:
        if downloaded_path and os.path.exists(downloaded_path):
            try:
                os.remove(downloaded_path)
            except Exception:
                pass
        await asyncio.sleep(4)
        active_locks.discard(msg.id)

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def h1(event):
    await process_msg(event.message, is_edit=False)

@client.on(events.MessageEdited(chats=SOURCE_CHATS))
async def h2(event):
    await process_msg(event.message, is_edit=True)

@client.on(events.MessageDeleted())
async def delete_handler(event):
    for msg_id in event.deleted_ids:
        tgt_id, _ = get_mapping(msg_id)
        if tgt_id:
            try:
                await client.delete_messages(TARGET, tgt_id)
                delete_mapping(msg_id)
            except: pass

async def main():
    await client.start()
    logging.info("🚀 V91 LINK-BLOCKADE ONLINE")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

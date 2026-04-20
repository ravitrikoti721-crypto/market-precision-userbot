import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

# 1. Dummy Server
def run_dummy_server():
    with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Config - Bilkul saaf tareeke se
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")

# ID handling without any spaces or hidden characters
raw_target = str(os.environ.get("TARGET_CHAT_ID")).strip()
TARGET = int(raw_target)

raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

# Memory limit set kar rahe hain taaki purana kachra na uthaye
app = Client("mp_bot_final", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, in_memory=True)

@app.on_message(filters.chat(SOURCES))
async def copy_handler(client, message):
    try:
        print(f"!!! MATCH !!! Copying message from {message.chat.id}...", flush=True)
        await message.copy(chat_id=TARGET)
        print(f"--- SUCCESS: Copied to {TARGET} ---", flush=True)
    except Exception as e:
        print(f"Copy Error: {e}", flush=True)

async def main():
    await app.start()
    print("--- STARTING SYSTEM ---", flush=True)
    
    # 3. Target Verification (Yahi sabse zaroori hai)
    try:
        target_info = await app.get_chat(TARGET)
        print(f"✅ TARGET IS OK: {target_info.title}", flush=True)
    except Exception as e:
        print(f"❌ TARGET NOT ACCESSIBLE: {e}", flush=True)
        print(f"Check if ID {TARGET} is correct and bot is Admin there.", flush=True)

    print(f"--- WATCHING SOURCES: {SOURCES} ---", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

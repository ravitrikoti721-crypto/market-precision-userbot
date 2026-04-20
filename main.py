import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

# 1. Dummy Server
def run_dummy_server():
    with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(str(os.environ.get("TARGET_CHAT_ID")).strip())

raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

# Bot setup with heavy updates enabled
app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=20)

# 3. Master Logger - Ye har cheez print karega
@app.on_message(filters.all)
async def monitor_all(client, message):
    chat_id = message.chat.id
    print(f"--> [ANY MSG] From: {chat_id} | Name: {message.chat.title or 'Private'}", flush=True)

    if chat_id in SOURCES:
        try:
            print(f"!!! MATCH FOUND !!! Copying from {chat_id}...", flush=True)
            await message.copy(chat_id=TARGET)
            print(f"--- SUCCESS: Copied to {TARGET} ---", flush=True)
        except Exception as e:
            print(f"Copy Error: {e}", flush=True)

async def main():
    await app.start()
    print(f"--- SYSTEM ONLINE ---", flush=True)
    print(f"WATCHING: {SOURCES}", flush=True)
    print(f"TARGET: {TARGET}", flush=True)
    
    # Verify Sources at start
    for s_id in SOURCES:
        try:
            chat = await app.get_chat(s_id)
            print(f"✅ Active Source: {chat.title}", flush=True)
        except:
            print(f"❌ Source Not Found: {s_id}", flush=True)

    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

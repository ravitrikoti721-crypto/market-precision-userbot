import http.server, socketserver, threading, os, asyncio, sys
from pyrogram import Client, filters

# 1. Dummy Server
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")

# TARGET aur SOURCES ko integer mein convert karna zaroori hai
TARGET = int(str(os.environ.get("TARGET_CHAT_ID")).strip())
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=20)

# 3. Handler
@app.on_message()
async def master_handler(client, message):
    try:
        chat_id = message.chat.id
        print(f"!!! MESSAGE DETECTED !!! ID: {chat_id}", flush=True)

        if chat_id in SOURCES:
            # COPY logic (Ye 'Peer ID Invalid' ko avoid karta hai)
            await message.copy(chat_id=TARGET)
            print(f"--- SUCCESS: Copied to {TARGET} ---", flush=True)

    except Exception as e:
        print(f"Error in handler: {e}", flush=True)

async def main():
    await app.start()
    print(f"--- SYSTEM ONLINE | Watching: {SOURCES} | Target: {TARGET} ---", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

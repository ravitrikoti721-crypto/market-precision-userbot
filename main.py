import http.server, socketserver, threading, os, asyncio
from pyrogram import Client

def run_dummy_server():
    with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(str(os.environ.get("TARGET_CHAT_ID")).strip())

# Sources ko handle karne ka smart tarika
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
# Is baar hum handle karenge ki agar koi username (@) dalta hai toh wo crash na ho
SOURCES = []
for i in raw_sources.split(","):
    item = i.strip()
    if item:
        if item.startswith("-100") or item.isdigit() or item.startswith("-"):
            SOURCES.append(int(item))
        else:
            SOURCES.append(item) # Username as string

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=20)

@app.on_message()
async def master_handler(client, message):
    try:
        # Check by ID or Username
        is_source = False
        if message.chat.id in SOURCES:
            is_source = True
        elif message.chat.username and message.chat.username in SOURCES:
            is_source = True
            
        if is_source:
            print(f"!!! MATCH FOUND !!! From: {message.chat.id}", flush=True)
            await message.copy(chat_id=TARGET)
            print(f"--- SUCCESS: Copied to {TARGET} ---", flush=True)

    except Exception as e:
        print(f"Error in handler: {e}", flush=True)

async def main():
    await app.start()
    print(f"--- SYSTEM ONLINE | Watching: {SOURCES} | Target: {TARGET} ---", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

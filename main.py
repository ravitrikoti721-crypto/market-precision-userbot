import http.server, socketserver, threading, os, asyncio
from pyrogram import Client

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

# Sources handling
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = []
for i in raw_sources.split(","):
    item = i.strip()
    if item:
        if item.startswith("-100") or item.isdigit() or item.startswith("-"):
            SOURCES.append(int(item))
        else:
            SOURCES.append(item)

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=20)

# 3. Handler
@app.on_message()
async def master_handler(client, message):
    try:
        chat_id = message.chat.id
        username = message.chat.username
        
        # Check if message is from your specified sources
        is_source = False
        if chat_id in SOURCES:
            is_source = True
        elif username and username in SOURCES:
            is_source = True

        if is_source:
            print(f"!!! MATCH FOUND !!! From: {chat_id}", flush=True)
            # Copy with branding
            text = message.text or message.caption or ""
            full_text = text + "\n\n✅ Via @marketprecision"
            
            if message.photo:
                await client.send_photo(TARGET, message.photo.file_id, caption=full_text)
            elif message.video:
                await client.send_video(TARGET, message.video.file_id, caption=full_text)
            else:
                await client.send_message(TARGET, full_text)
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

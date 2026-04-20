import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

# 1. Dummy Server for Render
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

# Workers kam rakhe hain taaki stability bani rahe
app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=5)

# 3. Master Handler - Is baar filters.all hata diya hai, default pakdega
@app.on_message()
async def master_handler(client, message):
    chat_id = message.chat.id
    # Ye line har halat mein log dikhayegi
    print(f"--> NEW EVENT: From {chat_id}", flush=True)

    if chat_id in SOURCES:
        try:
            print(f"!!! SOURCE MATCH !!! Copying from {chat_id}...", flush=True)
            await message.copy(chat_id=TARGET)
            print(f"--- SUCCESS: Copied to {TARGET} ---", flush=True)
        except Exception as e:
            print(f"Copy Error: {e}", flush=True)

async def main():
    await app.start()
    me = await app.get_me()
    print(f"--- SYSTEM READY: {me.first_name} ---", flush=True)
    
    # Startup check
    await app.send_message("me", "Listening for messages now...")
    print("--- STARTUP TEST SENT ---", flush=True)

    # Idle mode jo updates ko khichta rahega
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

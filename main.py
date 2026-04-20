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

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=20)

# 3. Master Handler
@app.on_message()
async def main_handler(client, message):
    try:
        chat_id = message.chat.id
        # Ye line har message par log degi, chahe source ho ya na ho
        print(f"--> RECEIVED: Message from {chat_id}", flush=True)

        if chat_id in SOURCES:
            print(f"!!! MATCH !!! Copying from {chat_id}...", flush=True)
            await message.copy(chat_id=TARGET)
            print(f"--- DONE: Copied to {TARGET} ---", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

async def main():
    await app.start()
    me = await app.get_me()
    print(f"--- BOT ONLINE: Logged in as {me.first_name} ---", flush=True)
    print(f"WATCHING: {SOURCES}", flush=True)
    
    # Force verification
    for s_id in SOURCES:
        try:
            chat = await app.get_chat(s_id)
            print(f"✅ Verified: {chat.title}", flush=True)
        except:
            print(f"❌ Failed to find: {s_id}", flush=True)

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

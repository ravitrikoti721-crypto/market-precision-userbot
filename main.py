import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

def run_dummy_server():
    with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
# Forcefully handle Target ID
t_id = str(os.environ.get("TARGET_CHAT_ID")).strip()
TARGET = int(t_id)

raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)

@app.on_message()
async def master_handler(client, message):
    try:
        if message.chat.id in SOURCES:
            print(f"!!! MATCH !!! Copying from {message.chat.id} to {TARGET}", flush=True)
            # Use send_message or copy based on peer resolution
            await message.copy(chat_id=TARGET)
            print(f"--- SUCCESS ---", flush=True)
    except Exception as e:
        print(f"Copy Error: {e}", flush=True)

async def main():
    await app.start()
    print("--- ATTEMPTING TARGET RESOLUTION ---", flush=True)
    try:
        # Ye line Target ko bot ki memory mein register kar degi
        target_chat = await app.get_chat(TARGET)
        print(f"✅ TARGET VERIFIED: {target_chat.title}", flush=True)
    except Exception as e:
        print(f"❌ TARGET FAILED: {e}", flush=True)
        print(f"TIP: Make sure you have sent at least one manual message in the Target channel from your account.", flush=True)

    print(f"--- BOT READY | WATCHING {len(SOURCES)} SOURCES ---", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

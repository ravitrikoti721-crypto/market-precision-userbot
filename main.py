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

# Bot setup with extreme logging
app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=5)

@app.on_message()
async def all_messages_handler(client, message):
    # Ye line har halat mein print honi chahiye agar bot "sunn" raha hai
    chat_name = message.chat.title or message.chat.first_name or "Unknown"
    print(f"!!! EVENT DETECTED !!! From: {chat_name} ({message.chat.id})", flush=True)

    if message.chat.id in SOURCES:
        try:
            await message.copy(chat_id=TARGET)
            print(f"✅ SUCCESS: Copied to {TARGET}", flush=True)
        except Exception as e:
            print(f"❌ Copy Error: {e}", flush=True)

async def main():
    print("--- ATTEMPTING STARTUP ---", flush=True)
    await app.start()
    me = await app.get_me()
    print(f"--- BOT ONLINE: {me.first_name} (@{me.username}) ---", flush=True)
    
    # Ye test karne ke liye ki bot khud ko message bhej sakta hai ya nahi
    try:
        await app.send_message("me", "Bot is now active and listening!")
        print("--- STARTUP TEST SENT TO SAVED MESSAGES ---", flush=True)
    except Exception as e:
        print(f"--- STARTUP TEST FAILED: {e} ---", flush=True)

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

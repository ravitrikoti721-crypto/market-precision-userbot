import http.server, socketserver, threading, os, asyncio, sys
from pyrogram import Client, filters

# 1. Dummy Server for Render
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Config from Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(os.environ.get("TARGET_CHAT_ID"))
# IDs ko handle karne ka safe tarika
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)

# 3. All-in-One Monitor & Forwarder
@app.on_message()
async def master_handler(client, message):
    try:
        chat_id = message.chat.id
        chat_name = message.chat.title or message.chat.first_name or "Unknown"
        
        # LOGGING: Ye line aapko har message ki asli ID bata degi
        print(f"!!! MESSAGE DETECTED !!! From: {chat_name} (ID: {chat_id})", flush=True)

        # FORWARDING: Agar ID match hoti hai toh copy karega
        if chat_id in SOURCES:
            text = message.text or message.caption or ""
            
            # Cleaning Logic (Optional: Abhi sirf apna footer add kar rahe hain)
            footer = "\n\n✅ Via @marketprecision"
            full_text = text + footer

            if message.photo:
                await client.send_photo(TARGET, message.photo.file_id, caption=full_text)
            elif message.video:
                await client.send_video(TARGET, message.video.file_id, caption=full_text)
            else:
                await client.send_message(TARGET, full_text)
            
            print(f"--- SUCCESS: Copied from {chat_name} ---", flush=True)

    except Exception as e:
        print(f"Error in handler: {e}", flush=True)

async def main():
    await app.start()
    me = await app.get_me()
    print(f"--- SYSTEM ONLINE: Logged in as {me.first_name} ---", flush=True)
    print(f"--- WATCHING SOURCES: {SOURCES} ---", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

import http.server, socketserver, threading, os, asyncio, sys
from pyrogram import Client, filters

# 1. Dummy Server (Render Health Check)
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Configuration
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(os.environ.get("TARGET_CHAT_ID"))
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

# Bot Client
app = Client(
    "mp_bot", 
    session_string=SESSION, 
    api_id=API_ID, 
    api_hash=API_HASH,
    workers=20
)

# 3. Master Handler (All Messages)
@app.on_message()
async def master_handler(client, message):
    try:
        chat_id = message.chat.id
        chat_name = message.chat.title or message.chat.first_name or "Unknown"
        
        # LOGGING: Har message ko detect karega aur print karega
        print(f"!!! MESSAGE DETECTED !!! From: {chat_name} (ID: {chat_id})", flush=True)

        # FORWARDING: Sirf tab jab ID SOURCES list mein ho
        if chat_id in SOURCES:
            text = message.text or message.caption or ""
            # Niche apna brand name add kar rahe hain
            full_text = text + "\n\n✅ Via @marketprecision"

            if message.photo:
                await client.send_photo(TARGET, message.photo.file_id, caption=full_text)
            elif message.video:
                await client.send_video(TARGET, message.video.file_id, caption=full_text)
            else:
                await client.send_message(TARGET, full_text)
            
            print(f"--- SUCCESS: Copied from {chat_name} ---", flush=True)

    except Exception as e:
        print(f"Error in handler: {e}", flush=True)

# 4. Main Function to start the bot
async def main():
    try:
        await app.start()
        me = await app.get_me()
        print(f"--- SYSTEM ONLINE: Logged in as {me.first_name} ---", flush=True)
        print(f"--- WATCHING SOURCES: {SOURCES} ---", flush=True)
        
        # Ye line bot ko updates receive karne ke liye "Jagaye" rakhti hai
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Startup Error: {e}", flush=True)

if __name__ == "__main__":
    # Python 3.10+ friendly event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

# Dummy Server for Render
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", 8080), handler) as httpd:
            httpd.serve_forever()
    except: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

# Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(os.environ.get("TARGET_CHAT_ID"))
SOURCES = [int(i.strip()) for i in os.environ.get("SOURCE_CHAT_IDS").split(",") if i.strip()]

# Version check karke client setup karna
try:
    # Modern Pyrogram (V2)
    app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)
except TypeError:
    # Older Pyrogram (V1)
    app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCES))
async def forward_msg(client, message):
    try:
        text = message.text or message.caption or ""
        if message.photo:
            await client.send_photo(TARGET, message.photo.file_id, caption=text)
        elif message.video:
            await client.send_video(TARGET, message.video.file_id, caption=text)
        else:
            await client.send_message(TARGET, text)
        print("Done!")
    except Exception as e: print(f"Err: {e}")

async def run_bot():
    async with app:
        print("Market Precision Master Forwarder is live...")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run_bot())

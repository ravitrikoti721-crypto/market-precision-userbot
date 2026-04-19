import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

# 1. Dummy Server (Non-blocking)
def run_dummy_server():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args): return

    with socketserver.TCPServer(("", 8080), QuietHandler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(os.environ.get("TARGET_CHAT_ID"))
SOURCES = [int(i.strip()) for i in os.environ.get("SOURCE_CHAT_IDS").split(",") if i.strip()]

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCES))
async def forward_msg(client, message):
    try:
        # Trade copy logic
        if message.text:
            await client.send_message(TARGET, message.text)
        elif message.photo:
            await client.send_photo(TARGET, message.photo.file_id, caption=message.caption or "")
        elif message.video:
            await client.send_video(TARGET, message.video.file_id, caption=message.caption or "")
        print("Done: Trade Copied!")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await app.start()
    print("--- MASTER FORWARDER IS LIVE AND WATCHING TRADES ---")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

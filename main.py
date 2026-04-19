import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

# Dummy Server to keep Render happy
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", 8080), handler) as httpd:
            httpd.serve_forever()
    except: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

# Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(os.environ.get("TARGET_CHAT_ID"))
SOURCES = [int(i.strip()) for i in os.environ.get("SOURCE_CHAT_IDS").split(",") if i.strip()]

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCES))
async def forward_msg(client, message):
    try:
        # Direct Copying for Restricted Channels
        if message.text:
            await client.send_message(TARGET, message.text)
        elif message.photo:
            await client.send_photo(TARGET, message.photo.file_id, caption=message.caption or "")
        elif message.video:
            await client.send_video(TARGET, message.video.file_id, caption=message.caption or "")
        print("Success: Copied!")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await app.start()
    print("Market Precision Master Forwarder is live...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Python 3.10 friendly loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

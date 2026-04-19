import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

# 1. Background Dummy Server (Render ko khush rakhne ke liye)
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    # Isse logs clean rahenge
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

# Ise thread mein chalana zaroori hai
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
        # Content Copy Logic
        text = message.text or message.caption or ""
        if message.photo:
            await client.send_photo(TARGET, message.photo.file_id, caption=text)
        elif message.video:
            await client.send_video(TARGET, message.video.file_id, caption=text)
        else:
            await client.send_message(TARGET, text)
        print("Done: Trade Copied!")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    # Pehle bot start hoga
    await app.start()
    print("--- MASTER FORWARDER IS LIVE AND WATCHING TRADES ---")
    # Phir ye infinite loop mein chalega
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

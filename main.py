import http.server, socketserver, threading, os, asyncio, sys
from pyrogram import Client, filters

# 1. Dummy Server (Render Health Check ke liye)
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(os.environ.get("TARGET_CHAT_ID"))
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)

@app.on_message()
async def monitor_and_forward(client, message):
    # 1. Ye line har message ki ID logs mein dikhayegi
    print(f"MESSAGE DETECTED! From Chat ID: {message.chat.id}", flush=True)

    # 2. Forwarding Logic (Sirf un chats se jo aapne Render par daali hain)
    if message.chat.id in SOURCES:
        try:
            text = message.text or message.caption or ""
            if message.photo:
                await client.send_photo(TARGET, message.photo.file_id, caption=text)
            elif message.video:
                await client.send_video(TARGET, message.video.file_id, caption=text)
            else:
                await client.send_message(TARGET, text)
            print("Trade Copied!", flush=True)
        except Exception as e:
            print(f"Forwarding Error: {e}", flush=True)
async def main():
    print("--- BOT STARTING ---", flush=True)
    await app.start()
    print("--- MASTER FORWARDER IS LIVE ---", flush=True)
    # Keep alive
    while True:
        await asyncio.sleep(1000)

if __name__ == "__main__":
    asyncio.run(main())

import http.server, socketserver, threading, os
from pyrogram import Client, filters

def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", 8080), handler) as httpd:
            httpd.serve_forever()
    except: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID"))
SOURCE_CHANNELS = [int(i.strip()) for i in os.environ.get("SOURCE_CHAT_IDS").split(",") if i.strip()]

app = Client("mp_userbot", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_CHANNELS))
def forward_restricted(client, message):
    try:
        text = message.text or message.caption or ""
        if message.photo:
            client.send_photo(TARGET_CHAT_ID, message.photo.file_id, caption=text)
        elif message.video:
            client.send_video(TARGET_CHAT_ID, message.video.file_id, caption=text)
        else:
            client.send_message(TARGET_CHAT_ID, text)
        print("Trade Copied!")
    except Exception as e: print(f"Error: {e}")

print("Market Precision Master Forwarder is live...")
app.run()

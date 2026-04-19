import http.server
import socketserver
import threading
import os
from pyrogram import Client, filters

# Dummy Server for Render (Port 8080)
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", 8080), handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Configuration ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID"))
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCE_CHANNELS = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

app = Client("mp_userbot", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_CHANNELS))
def forward_restricted(client, message):
    try:
        text = message.text or message.caption or ""
        # Brand cleaning
        text = text.replace("@OldChannel", "@marketprecision")
        
        if message.photo:
            client.send_photo(TARGET_CHAT_ID, message.photo.file_id, caption=text)
        elif message.video:
            client.send_video(TARGET_CHAT_ID, message.video.file_id, caption=text)
        else:
            client.send_message(TARGET_CHAT_ID, text)
        print("Trade Copied Successfully!")
    except Exception as e:
        print(f"Forwarding Error: {e}")

print("Market Precision Master Forwarder is live (V1.4.16)...")
app.run()

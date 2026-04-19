import http.server
import socketserver
import threading
import os
from pyrogram import Client, filters

# Render ko khush karne ke liye dummy web server
def run_dummy_server():
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", 8080), handler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Market Precision Forwarder Code ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
TARGET_CHAT_ID = int(os.environ.get("TARGET_CHAT_ID"))
SOURCE_CHANNELS = [int(i.strip()) for i in os.environ.get("SOURCE_CHAT_IDS").split(",")]

app = Client("mp_userbot", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_CHANNELS))
async def forward_restricted(client, message):
    try:
        text = message.text or message.caption or ""
        
        # Brand cleaning
        text = text.replace("@OldChannel", "@marketprecision")
        
        if message.photo:
            await client.send_photo(TARGET_CHAT_ID, message.photo.file_id, caption=text)
        elif message.video:
            await client.send_video(TARGET_CHAT_ID, message.video.file_id, caption=text)
        else:
            await client.send_message(TARGET_CHAT_ID, text)
        print(f"Message copied successfully!")
    except Exception as e:
        print(f"Error: {e}")

print("Market Precision Master Forwarder is live...")
app.run()

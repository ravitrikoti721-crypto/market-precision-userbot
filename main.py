import os
import threading
import http.server
import socketserver
from pyrogram import Client, filters

# 1. Render dummy server to keep it alive
def start_server():
    try:
        with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=start_server, daemon=True).start()

# 2. Config from Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(os.environ.get("TARGET_CHAT_ID"))
# Multiple IDs support
SOURCE_LIST = [int(i.strip()) for i in os.environ.get("SOURCE_CHAT_IDS").split(",") if i.strip()]

# 3. Client setup (V1 Syntax)
app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_LIST))
def forwarder(client, message):
    try:
        # Copying content instead of forwarding to bypass restrictions
        if message.text:
            client.send_message(TARGET, message.text)
        elif message.photo:
            client.send_photo(TARGET, message.photo.file_id, caption=message.caption or "")
        elif message.video:
            client.send_video(TARGET, message.video.file_id, caption=message.caption or "")
        print("Successfully Copied Trade!")
    except Exception as e:
        print(f"Copy Error: {e}")

print("--- MARKET PRECISION BOT IS STARTING ---")
app.run()

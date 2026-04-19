import http.server, socketserver, threading, os, asyncio
from pyrogram import Client

# Dummy Server
def run_dummy_server():
    with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")

# Is baar hum simple monitor function likhenge
app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)

@app.on_message()
async def logger(client, message):
    print(f"!!! MESSAGE FOUND !!! From: {message.chat.id} Text: {message.text[:20]}", flush=True)

async def main():
    await app.start()
    me = await app.get_me()
    print(f"--- LOGGED IN AS: {me.first_name} (@{me.username}) ---", flush=True)
    print("--- WAITING FOR ANY MESSAGE ---", flush=True)
    await asyncio.Event().wait()

asyncio.run(main())

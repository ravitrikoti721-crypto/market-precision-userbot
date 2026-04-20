import http.server, socketserver, threading, os, asyncio
from pyrogram import Client, filters

def run_dummy_server():
    with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")

# Target ID ko handle karne ka sabse safe tareeka
t_id = str(os.environ.get("TARGET_CHAT_ID")).strip()
TARGET = int(t_id)

raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

app = Client("mp_bot", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, workers=10)

@app.on_message()
async def master_handler(client, message):
    try:
        chat_id = message.chat.id
        if chat_id in SOURCES:
            print(f"!!! MATCH !!! From {chat_id}. Copying to {TARGET}...", flush=True)
            # Seedha copy karne ki jagah send_message try karte hain agar copy fail ho
            await message.copy(chat_id=TARGET)
            print(f"--- SUCCESS ---", flush=True)
    except Exception as e:
        print(f"Copy Error: {e}", flush=True)
        # Agar copy fail ho, toh manually fetch karke resolve karne ki koshish
        try:
            chat = await client.get_chat(TARGET)
            await message.copy(chat_id=chat.id)
            print("--- SUCCESS AFTER RESOLVING PEER ---", flush=True)
        except Exception as e2:
            print(f"Fatal Target Error: {e2}", flush=True)

async def main():
    await app.start()
    # Startup par Target ko "Jagana"
    try:
        target_chat = await app.get_chat(TARGET)
        print(f"--- TARGET VERIFIED: {target_chat.title} ---", flush=True)
    except Exception as e:
        print(f"--- TARGET ERROR: Bot cannot see Target Channel {TARGET} | {e} ---", flush=True)
    
    print(f"--- BOT READY | WATCHING {len(SOURCES)} SOURCES ---", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

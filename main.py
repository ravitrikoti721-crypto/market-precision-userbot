import os, asyncio
from pyrogram import Client, filters

# Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION_STRING")
TARGET = int(str(os.environ.get("TARGET_CHAT_ID")).strip())
raw_sources = os.environ.get("SOURCE_CHAT_IDS", "")
SOURCES = [int(i.strip()) for i in raw_sources.split(",") if i.strip()]

# Naya session name aur in_memory use kar rahe hain taaki cache ka naam-o- निशान mit jaye
app = Client("market_precision_final_v3", session_string=SESSION, api_id=API_ID, api_hash=API_HASH, in_memory=True)

@app.on_message(filters.chat(SOURCES))
async def copy_handler(client, message):
    try:
        print(f"!!! MATCH FOUND !!! Copying from {message.chat.id}...", flush=True)
        await message.copy(chat_id=TARGET)
        print(f"✅ SUCCESS: Copied to {TARGET}", flush=True)
    except Exception as e:
        print(f"❌ Copy Error: {e}", flush=True)

async def main():
    await app.start()
    print("--- SYSTEM STARTING FRESH ---", flush=True)
    
    # Forceful Resolution
    try:
        chat = await app.get_chat(TARGET)
        print(f"✅ TARGET VERIFIED: {chat.title} ({chat.id})", flush=True)
    except Exception as e:
        print(f"❌ TARGET STILL NOT RESOLVED: {e}", flush=True)
        print(f"Action: Apne account se Target channel mein 1 manual message turant bhejo!", flush=True)

    print(f"WATCHING SOURCES: {SOURCES}", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

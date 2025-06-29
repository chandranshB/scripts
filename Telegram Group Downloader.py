import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError, FloodWaitError
from telethon.tl.types import MessageMediaDocument
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables or prompt user
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OUT_DIR = ""  # Will be dynamically set based on group/channel name


async def download_media(msg, idx):
    """Download a single media message and organize it into the correct folder."""
    folder = determine_folder(msg)
    os.makedirs(folder, exist_ok=True)

    try:
        file_path = await msg.download_media(file=folder)
        print(f"[{idx:03d}] Downloaded: {file_path}")
    except RPCError as e:
        print(f"[Error @{msg.id}] {e}")


def determine_folder(msg):
    """Determine the folder for saving media based on its type."""
    if msg.media is None:
        return os.path.join(OUT_DIR, "other")
    if msg.photo:
        return os.path.join(OUT_DIR, "images")
    if isinstance(msg.media, MessageMediaDocument):
        mime_type = msg.media.document.mime_type or ""
        if "video" in mime_type:
            return os.path.join(OUT_DIR, "videos")
        elif "audio" in mime_type:
            return os.path.join(OUT_DIR, "audio")
        elif "text/vcard" in mime_type:
            return os.path.join(OUT_DIR, "vcards")
        elif "application" in mime_type or "document" in mime_type:
            return os.path.join(OUT_DIR, "documents")
    return os.path.join(OUT_DIR, "other")


def prompt_user():
    """Prompt the user for input values."""
    global API_ID, API_HASH

    if not (API_ID and API_HASH):
        print("API credentials not found. Please enter them below:")
        API_ID = input("Enter your API_ID: ").strip()
        API_HASH = input("Enter your API_HASH: ").strip()

    group_link = input("Enter the Telegram group/channel link: ").strip()

    while True:
        try:
            parallel_downloads = int(input("Enter the number of parallel downloads (1-10): ").strip())
            if 1 <= parallel_downloads <= 10:
                break
            else:
                print("Please enter a value between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    return group_link, parallel_downloads


async def resolve_group_link(client, group_link):
    """Resolve a Telegram group/channel link to its corresponding entity."""
    if "t.me/c/" in group_link:
        try:
            numeric_id = int(group_link.split("/")[4])
            return int(f"-100{numeric_id}")
        except (IndexError, ValueError):
            print("❌ Invalid private group link format.")
            sys.exit(1)
    elif "t.me/+" in group_link or "t.me/" in group_link:
        try:
            return await client.get_entity(group_link)
        except Exception as e:
            print(f"❌ Error resolving link: {e}")
            sys.exit(1)
    else:
        print("❌ Invalid Telegram link format.")
        sys.exit(1)


async def main():
    global OUT_DIR

    group_link, parallel_downloads = prompt_user()
    group_name = group_link.split("/")[-1].split("?")[0]
    OUT_DIR = f"{group_name}_media"
    os.makedirs(OUT_DIR, exist_ok=True)

    async with TelegramClient("session", API_ID, API_HASH) as client:
        entity = await resolve_group_link(client, group_link)
        tasks = []
        idx = 0

        async for msg in client.iter_messages(entity):
            if not msg.media:
                continue
            idx += 1
            tasks.append(asyncio.create_task(download_media(msg, idx)))

            if len(tasks) >= parallel_downloads:
                try:
                    await asyncio.gather(*tasks)
                except FloodWaitError as e:
                    print(f"Rate limit hit. Sleeping for {e.seconds} seconds.")
                    await asyncio.sleep(e.seconds)
                finally:
                    tasks = []

        if tasks:
            await asyncio.gather(*tasks)

    print(f"\n✅ All media saved in '{OUT_DIR}'.")


if __name__ == "__main__":
    asyncio.run(main())

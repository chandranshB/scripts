import os
import sys
import json
import hashlib
import asyncio
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, DocumentAttributeFilename
from telethon.tl.functions.channels import GetForumTopicsRequest
from collections import defaultdict
from tqdm.asyncio import tqdm

# --- CONFIGURATION ---
SESSION_NAME = 'telegram_cleaner'
CACHE_FILE_NAME = 'progress_cache.json'
PARTIAL_HASH_THRESHOLD_MB = 10
PARTIAL_HASH_CHUNK_SIZE = 1024 * 1024
TEMP_FILE_PATH = 'temp_download_for_hash'
# ---------------------

def save_cache(data):
    with open(CACHE_FILE_NAME, 'w') as f: json.dump(data, f, indent=2)

def load_cache(group_id):
    if not os.path.exists(CACHE_FILE_NAME): return None
    with open(CACHE_FILE_NAME, 'r') as f:
        try:
            data = json.load(f)
            if data.get('group_id') == group_id: return data
            else: print("⚠️ Cache file for a different group found. Starting fresh."); return None
        except json.JSONDecodeError: return None

def clean_generated_files(clean_session=True):
    print("🧹 Starting cleanup...")
    files_to_clean = [TEMP_FILE_PATH + ".tmp", CACHE_FILE_NAME]
    if clean_session: files_to_clean.append(SESSION_NAME + ".session")
    cleaned_count = 0
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  - Deleted: {file_path}")
                cleaned_count += 1
            except OSError as e: print(f"  - Error deleting {file_path}: {e}")
    if cleaned_count == 0: print("✨ No generated files to clean.")
    else: print("✅ Cleanup complete.")

def get_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data: break
            sha256.update(data)
    return sha256.hexdigest()

async def get_partial_hash(client, media):
    sha256 = hashlib.sha256()
    async for chunk in client.iter_download(media, request_size=PARTIAL_HASH_CHUNK_SIZE):
        sha256.update(chunk)
        break
    return sha256.hexdigest()

async def select_topic(client, group_entity):
    if not isinstance(group_entity, Channel) or not group_entity.forum: return None
    print(f"\n'{group_entity.title}' has Topics enabled.")
    try:
        result = await client(GetForumTopicsRequest(channel=group_entity, offset_date=None, offset_id=0, offset_topic=0, limit=100))
        topics = result.topics
    except Exception as e: print(f"Could not fetch topics: {e}"); return 0
    if not topics: print("No topics found. Scanning the entire group."); return 0
    print("Select a topic to scan, or scan the entire group:")
    print("  0: ✨ Scan Entire Group (All Topics)")
    for i, topic in enumerate(topics): print(f"  {i + 1}: {topic.title}")
    while True:
        try:
            choice = int(input("\n➡️  Enter your choice: "))
            if 0 <= choice <= len(topics): return topics[choice - 1].id if choice > 0 else 0
            else: print("Invalid number.")
        except ValueError: print("Invalid input.")

async def process_files_in_group(client, group_entity, files, size, threshold, executor, loop):
    """Async generator that processes a group of same-sized files and yields results."""
    if size > threshold:
        # Simple I/O path for large files (partial hash)
        for file_info_orig in files:
            file_info = file_info_orig.copy()
            try:
                message = await client.get_messages(group_entity, ids=file_info['id'])
                if not message or not message.media: continue
                file_info['hash'] = await get_partial_hash(client, message.media)
                file_info['name'] = next((attr.file_name for attr in message.document.attributes if isinstance(attr, DocumentAttributeFilename)), 'N/A')
                file_info['date'] = datetime.fromisoformat(file_info['date'])
                if file_info['hash']: yield file_info
            except Exception as e:
                tqdm.write(f"  ⚠️  Error on msg {file_info.get('id', 'N/A')}: {e}")
    else:
        # Parallel CPU+I/O path for smaller files (full hash)
        download_path, hash_task, processed_info = None, None, None
        for i, file_info_orig in enumerate(files):
            file_info = file_info_orig.copy()
            try:
                message = await client.get_messages(group_entity, ids=file_info['id'])
                if not message or not message.media: continue
                current_download_path = f"{TEMP_FILE_PATH}_{i}.tmp"
                await client.download_media(message.media, file=current_download_path)
                if hash_task:
                    processed_info['hash'] = await hash_task
                    msg_for_name = await client.get_messages(group_entity, ids=processed_info['id'])
                    processed_info['name'] = next((attr.file_name for attr in msg_for_name.document.attributes if isinstance(attr, DocumentAttributeFilename)), 'N/A') if msg_for_name and msg_for_name.document else 'N/A'
                    processed_info['date'] = datetime.fromisoformat(processed_info['date'])
                    if processed_info['hash']: yield processed_info
                    os.remove(download_path)
                download_path, processed_info = current_download_path, file_info
                hash_task = loop.run_in_executor(executor, get_file_hash, download_path)
            except Exception as e:
                tqdm.write(f"  ⚠️  Error on msg {file_info.get('id', 'N/A')}: {e}")
                hash_task = None
                if download_path and os.path.exists(download_path): os.remove(download_path)
        if hash_task:
            try:
                processed_info['hash'] = await hash_task
                msg_for_name = await client.get_messages(group_entity, ids=processed_info['id'])
                processed_info['name'] = next((attr.file_name for attr in msg_for_name.document.attributes if isinstance(attr, DocumentAttributeFilename)), 'N/A') if msg_for_name and msg_for_name.document else 'N/A'
                processed_info['date'] = datetime.fromisoformat(processed_info['date'])
                if processed_info['hash']: yield processed_info
                os.remove(download_path)
            except Exception as e:
                tqdm.write(f"  ⚠️  Error on final hash: {e}")

async def find_and_delete_duplicates(client, group_entity, topic_id, mode):
    scan_target = group_entity.title
    scan_args = {'entity': group_entity}
    if topic_id:
        scan_args['reply_to'] = topic_id
        scan_target += f" (Topic ID: {topic_id})"

    cache_data = load_cache(group_entity.id)
    if cache_data:
        print("✅ Resuming from previously saved progress...")
        last_message_id = cache_data.get('last_message_id', 0)
        files_by_size = defaultdict(list, {int(k): v for k, v in cache_data.get('files_by_size', {}).items()})
        hashes = cache_data.get('hashes', {})
        pass1_complete = cache_data.get('pass1_complete', False)
    else:
        print("🚀 Starting a new scan.")
        last_message_id, files_by_size, hashes, pass1_complete = 0, defaultdict(list), {}, False
    
    cache = {'group_id': group_entity.id, 'last_message_id': last_message_id, 'files_by_size': files_by_size, 'hashes': hashes, 'pass1_complete': pass1_complete}
    
    if not pass1_complete:
        print(f"\n🔍 Starting Pass 1: Indexing files in '{scan_target}'...")
        if last_message_id:
            print(f"  ...resuming from message ID {last_message_id}")
        
        with tqdm(total=None, desc="Scanning messages", unit=" msg") as pbar:
            async for message in client.iter_messages(**scan_args):
                pbar.update(1)
                cache['last_message_id'] = message.id
                file_obj = getattr(message, 'document', getattr(message, 'photo', None))
                if file_obj and hasattr(file_obj, 'size'):
                    files_by_size[file_obj.size].append({'id': message.id, 'date': message.date.isoformat()})
                if pbar.n > 0 and pbar.n % 200 == 0:
                    pbar.set_postfix_str("Saving progress...")
                    cache['files_by_size'] = {str(k): v for k, v in files_by_size.items()}
                    save_cache(cache)
        
        cache['pass1_complete'] = True
        cache['files_by_size'] = {str(k): v for k, v in files_by_size.items()}
        print("\n✅ Pass 1 Complete. Saving final index.")
        save_cache(cache)
    else:
        print("✅ Pass 1 was already complete. Skipping to verification.")

    potential_duplicates = {size: files for size, files in files_by_size.items() if len(files) > 1}
    if not potential_duplicates:
        print("\n🎉 No potential duplicates found. All good!"); return

    print(f"\n🔍 Starting Pass 2: Verifying potential duplicates...")
    duplicates_to_delete = []
    threshold_bytes = PARTIAL_HASH_THRESHOLD_MB * 1024 * 1024
    
    # --- NEW: Create a single, unified progress bar for all of Pass 2 ---
    total_files_to_verify = sum(len(files) for files in potential_duplicates.values())
    with tqdm(total=total_files_to_verify, desc="Verifying Duplicates", unit="file") as pbar:
        with ProcessPoolExecutor(max_workers=1) as executor:
            loop = asyncio.get_running_loop()
            for size, files in potential_duplicates.items():
                async for file_info in process_files_in_group(client, group_entity, files, size, threshold_bytes, executor, loop):
                    try:
                        original_file = hashes.get(file_info['hash'])
                        
                        if not original_file:
                            hashes[file_info['hash']] = {'id': file_info['id'], 'date': file_info['date'].isoformat()}
                        else:
                            is_current_file_duplicate = file_info['date'] > datetime.fromisoformat(original_file['date'])
                            
                            if is_current_file_duplicate:
                                if mode == 'delete_immediately':
                                    await client.delete_messages(group_entity, [file_info['id']])
                                    pbar.write(f"  - Deleted duplicate: {file_info['name']} (ID: {file_info['id']})")
                                else:
                                    duplicates_to_delete.append(file_info)
                            else:
                                if mode == 'delete_immediately':
                                    await client.delete_messages(group_entity, [original_file['id']])
                                    pbar.write(f"  - Deleted older duplicate (ID: {original_file['id']}) to keep newer one: {file_info['name']}")
                                else:
                                    duplicates_to_delete.append(original_file)
                                hashes[file_info['hash']] = {'id': file_info['id'], 'date': file_info['date'].isoformat()}
                        
                        cache['hashes'] = hashes
                        save_cache(cache)
                    except Exception as e:
                        pbar.write(f"  ⚠️  Error processing hash for msg {file_info.get('id', 'N/A')}: {e}")
                    
                    # --- NEW: Update the single progress bar after one file is fully processed ---
                    pbar.update(1)

    if mode != 'delete_immediately':
        if not duplicates_to_delete:
            print("\n🎉 Verification complete. No true duplicates found!")
            return
        
        unique_duplicates_to_delete = {d['id']: d for d in duplicates_to_delete}.values()
        print(f"\n🚨 Found {len(unique_duplicates_to_delete)} duplicate files.")

        if mode == 'list_only': return
            
        confirm = input("\n➡️  Do you want to delete them all? (yes/no): ").lower()
        if confirm == 'yes':
            print("\nDeleting files...")
            message_ids_to_delete = [f['id'] for f in unique_duplicates_to_delete]
            tasks = [client.delete_messages(group_entity, message_ids_to_delete[i:i+100]) for i in range(0, len(message_ids_to_delete), 100)]
            if tasks: await asyncio.gather(*tasks)
            print(f"\n✅ Successfully deleted {len(message_ids_to_delete)} duplicate files.")
        else:
            print("\nAborted. No files were deleted.")
    else:
        print("\n✅ On-the-fly deletion complete.")

async def main():
    print("--- Telegram Duplicate File Cleaner ---")
    while True:
        try: api_id = int(input("Please enter your API ID: ")); break
        except ValueError: print("❌ Invalid input. Must be a number.")
    api_hash = input("Please enter your API Hash: ")
    async with TelegramClient(SESSION_NAME, api_id, api_hash) as client:
        print("\n🚀 Login successful. Script starting...")
        group_link = input("➡️  Please enter the group link (e.g., t.me/groupname or https://t.me/+...): ")
        try:
            group = await client.get_entity(group_link)
            print(f"✅ Successfully found group: '{group.title}'")
            has_permission = group.creator or (group.admin_rights and group.admin_rights.delete_messages)
            if not has_permission: print("❌ You do not have permission to delete messages."); return
            print("✅ You have the required permissions.")
        except Exception as e: print(f"❌ An error occurred: {e}"); return
        
        print("\nPlease select an action:")
        print("  1: Find and delete duplicates immediately (on-the-fly)")
        print("  2: Find all duplicates, then ask for confirmation to delete (Recommended)")
        print("  3: Just find and list all duplicates (No deletion)")
        
        mode_map = {'1': 'delete_immediately', '2': 'confirm_at_end', '3': 'list_only'}
        while True:
            choice = input("\n➡️  Enter your choice (1-3): ")
            if choice in mode_map:
                mode = mode_map[choice]
                break
            else:
                print("Invalid choice. Please try again.")

        topic_id = await select_topic(client, group)
        if topic_id is None: topic_id = 0 
        await find_and_delete_duplicates(client, group, topic_id if topic_id != 0 else None, mode)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--clean':
        clean_generated_files(clean_session=True)
        sys.exit(0)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Script interrupted by user. Progress has been saved. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)
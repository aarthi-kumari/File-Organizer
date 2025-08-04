import os
import shutil
import json

LOG_FILE = "organizer.log.json"

FILE_TYPES = {
    "Images" : [".jpg", ".jpeg", ".png", ".gif",".bmp"],
    "Documents" : [".pdf", ".docx",".txt","doc",".pptx",".xlsx"],
    "Videos" : [".mp4",".mkv",".avi",".mov"],
    "Music" : [".mp3", ".wav", ".flac"],
    "Archives" : [".zip", ".rar", ".tar", ".gz"],
}

def get_category(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return "Others"

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r" ) as f:
            return json.load(f)
    return []

def save_log(log_data):
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=4)

def organize_folder(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Invalid folder: {folder_path}")
        return 
    
    log_data = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path,file_name)
        if os.path.isdir(file_path):
            continue

        category = get_category(file_name)
        target_dir = os.path.join(folder_path, category)
        os.makedirs(target_dir,exist_ok = True)

        new_path = os.path.join(target_dir, file_name)
        shutil.move(file_path,new_path)

        log_data.append({"original" : file_path, "moved" :new_path})
        print(f"Moved {file_name} -> {category}/")

    save_log(log_data)
    print(f"\n✅ Organization complete. You can undo this using: `python organizer.py undo`")

def undo_organization():
    log_data = load_log()
    if not log_data:
        print("⚠️ No actions to undo.")
        return
    
    for entry in log_data:
        moved = entry["moved"]
        original = entry["original"]
        try:
            os.makedirs(os.path.dirname(original), exist_ok=True)
            shutil.move(moved, original)
            print(f"Restored {os.path.basename(moved)} <- {original}")
        except Exception as e:
            print(f"Failed to move {moved} back to {original}: {e}")


    #Clean up empty folders
    moved_dirs = set(os.path.dirname(entry["moved"]) for entry in log_data)
    for d in moved_dirs:
        try:
            if not os.listdir(d):
                os.rmdir(d)
        except Exception:
            pass
    os.remove(LOG_FILE)
    print("\n✅ Undo complete.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "undo":
        undo_organization()
    else:
        folder = input("Enter the path of the folder to organize: ")
        organize_folder(folder.strip())

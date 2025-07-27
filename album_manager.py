# album_manager.py
import os
import json
from config import DATA_FILE

# Load or initialize albums
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        albums = json.load(f)
else:
    albums = {}

def save_albums():
    with open(DATA_FILE, "w") as f:
        json.dump(albums, f, indent=4)

def create_album(name):
    name = name.strip()
    if not name:
        return False
    if name not in albums:
        albums[name] = []
        save_albums()
        return True
    return False

def delete_album(name):
    if name in albums:
        albums.pop(name)
        save_albums()
        return True
    return False

def add_files_to_album(album_name, files):
    if album_name not in albums:
        return
    for f in files:
        if f not in albums[album_name]:
            albums[album_name].append(f)
    save_albums()

def get_albums():
    return list(albums.keys())

def get_files(album_name):
    return albums.get(album_name, [])

def file_exists(path):
    return os.path.exists(path)

def open_file(path):
    if file_exists(path):
        os.startfile(path)
        return True
    return False

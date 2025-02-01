import json
import os
from .teacher import Teacher
from .room import Room
from .group import Group

DATA_DIR = os.path.join(os.path.expanduser("~"), ".schedule_ai_project_data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

TEACHERS_FILE = os.path.join(DATA_DIR, "teachers.json")
ROOMS_FILE = os.path.join(DATA_DIR, "rooms.json")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")

def save_teachers(teachers):
    data = [t.to_dict() for t in teachers]
    with open(TEACHERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_teachers():
    if not os.path.exists(TEACHERS_FILE):
        return []
    with open(TEACHERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Teacher.from_dict(item) for item in data]

def save_rooms(rooms):
    data = [r.to_dict() for r in rooms]
    with open(ROOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return []
    with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Room.from_dict(item) for item in data]

def save_groups(groups):
    data = [g.to_dict() for g in groups]
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return []
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Group.from_dict(item) for item in data]

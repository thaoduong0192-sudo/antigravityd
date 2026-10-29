import json
import os

DEFAULT_STATE_FILE = "output_factory/factory_state.json"

def load_state(state_path=None):
    path = state_path or DEFAULT_STATE_FILE
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "notebook_id": None,
        "notebook_url": None,
        "topic": "",
        "long_topics": [],      # List of dict: {"id": "L01", "title": "...", "note_created": False, "video_id": None, "video_downloaded": False}
        "short_topics": [],     # List of dict: {"id": "S01_1", "parent_id": "L01", "title": "...", "video_id": None, "video_downloaded": False}
        "ebook_created": False,
        "upload_queue": []
    }

def save_state(state, state_path=None):
    path = state_path or DEFAULT_STATE_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

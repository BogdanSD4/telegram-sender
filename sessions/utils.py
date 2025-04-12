import os
from pathlib import Path


def session_path(name: str):
    return os.path.join(Path(__file__).parent, name)


def get_session():
    files = [
        f.replace('.session', '')
        for f in os.listdir(Path(__file__).parent) if f.endswith("session")
    ]
    return files


def delete_session(name: str):
    path = f"{session_path(name)}.session"
    if os.path.exists(path):
        os.remove(path)

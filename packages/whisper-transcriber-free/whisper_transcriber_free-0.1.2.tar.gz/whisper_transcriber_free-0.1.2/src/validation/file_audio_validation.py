import os

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".webm", ".aac", ".flac", ".ogg"}

def validate_audio_file(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported audio format: {ext}. Allowed formats: {ALLOWED_EXTENSIONS}")

import os

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

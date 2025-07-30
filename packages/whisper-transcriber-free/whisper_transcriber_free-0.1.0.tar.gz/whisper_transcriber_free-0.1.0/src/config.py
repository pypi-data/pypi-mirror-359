import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# HuggingFace configuration
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/spaces/raedrdhaounia/whisper-transcriber-free"


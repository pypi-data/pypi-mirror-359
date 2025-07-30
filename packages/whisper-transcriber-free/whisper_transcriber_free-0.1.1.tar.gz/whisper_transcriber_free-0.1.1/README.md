# Whisper Transcriber SDK

A Python SDK for audio transcription using OpenAI's Whisper model.

## Installation

```bash
pip install whisper-transcriber
```

## Usage

```python
from whisper_transcriber import WhisperTranscriber

# Initialize the transcriber
transcriber = WhisperTranscriber(model_size="base", device="cpu")

# Transcribe from local file
result = await transcriber.transcribe_file("path/to/audio.mp3")

# Transcribe from URL
result = await transcriber.transcribe_url("https://example.com/audio.mp3")

if result.status:
    print("Transcription:", result.data)
else:
    print("Error:", result.message)
```

## Features

- Support for multiple Whisper model sizes (base, small, medium, large)
- Transcription from local files and URLs
- Async/await support
- Comprehensive error handling
- CPU and GPU support

## Requirements

- Python 3.8+
- PyTorch 2.0+
- NumPy 1.24+

## License

MIT License

import pytest
import asyncio
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_audio_file():
    """Return path to test audio file"""
    test_dir = Path(__file__).parent
    return test_dir / "test_audio.mp3"

@pytest.fixture(scope="session")
def client():
    """Return a WhisperTranscriber client instance"""
    from whisper_transcriber import WhisperTranscriber
    return WhisperTranscriber(model_size="base", device="cpu")

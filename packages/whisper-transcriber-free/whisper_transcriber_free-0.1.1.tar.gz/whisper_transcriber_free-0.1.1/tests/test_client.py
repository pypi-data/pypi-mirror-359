import pytest
import asyncio

@pytest.mark.asyncio
async def test_transcribe_file(client, test_audio_file):
    """Test transcribing a local audio file"""
    result = await client.transcribe_file(test_audio_file)
    assert result.status is True
    assert result.code == 200
    assert isinstance(result.data, dict)
    assert "text" in result.data

@pytest.mark.asyncio
async def test_transcribe_nonexistent_file(client):
    """Test transcribing a non-existent file"""
    result = await client.transcribe_file("nonexistent_file.mp3")
    assert result.status is False
    assert result.code == 404
    assert "File not found" in result.message

@pytest.mark.asyncio
async def test_transcribe_invalid_file(client):
    """Test transcribing an invalid file type"""
    result = await client.transcribe_file("test.txt")
    assert result.status is False
    assert result.code == 400
    assert "Invalid audio file" in result.message

@pytest.mark.asyncio
async def test_transcribe_url(client):
    """Test transcribing audio from URL"""
    # Using a public test audio URL
    test_url = "https://file-examples.com/storage/fe67a925770449a899196c3/2017/11/file_example_MP3_700KB.mp3"
    result = await client.transcribe_url(test_url)
    assert result.status is True
    assert result.code == 200
    assert isinstance(result.data, dict)
    assert "text" in result.data

@pytest.mark.asyncio
async def test_transcribe_invalid_url(client):
    """Test transcribing from invalid URL"""
    result = await client.transcribe_url("invalid_url")
    assert result.status is False
    assert result.code == 400
    assert "Failed to download audio file" in result.message

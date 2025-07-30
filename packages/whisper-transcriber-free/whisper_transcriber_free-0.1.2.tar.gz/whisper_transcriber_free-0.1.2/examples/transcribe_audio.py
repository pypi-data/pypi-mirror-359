import asyncio
from whisper_transcriber import WhisperTranscriber

async def main():
    # Initialize the transcriber with base model and CPU
    transcriber = WhisperTranscriber(model_size="base", device="cpu")
    
    # Example 1: Transcribe from local file
    local_file = "path/to/your/audio.mp3"
    print(f"\nTranscribing local file: {local_file}")
    result = await transcriber.transcribe_file(local_file)
    
    if result.status:
        print("\nTranscription:")
        print(result.data["text"])
    else:
        print(f"Error: {result.message}")
    
    # Example 2: Transcribe from URL
    audio_url = "https://file-examples.com/storage/fe67a925770449a899196c3/2017/11/file_example_MP3_700KB.mp3"
    print(f"\nTranscribing from URL: {audio_url}")
    result = await transcriber.transcribe_url(audio_url)
    
    if result.status:
        print("\nTranscription:")
        print(result.data["text"])
    else:
        print(f"Error: {result.message}")
    
    # Example 3: Using different model size
    print("\nTranscribing with medium model...")
    transcriber = WhisperTranscriber(model_size="medium", device="cpu")
    result = await transcriber.transcribe_file(local_file)
    
    if result.status:
        print("\nTranscription:")
        print(result.data["text"])
    else:
        print(f"Error: {result.message}")

if __name__ == "__main__":
    asyncio.run(main())

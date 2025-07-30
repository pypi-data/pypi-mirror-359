from typing import Optional, Union
from pathlib import Path
import aiohttp
from .service.transcription_service import transcribe_audio
from .service.upload_file_service import save_upload_file
from .service.delete_audio_file_service import delete_file
from .models.transcript_request_model import TranscriptRequest
from .models.response_model import ResponseModel

class WhisperTranscriber:
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        """
        Initialize the Whisper transcriber client.
        
        Args:
            model_size: Size of the Whisper model to use (base, small, medium, large)
            device: Device to run the model on (cpu or cuda)
        """
        self.model_size = model_size
        self.device = device

    async def transcribe_file(self, file_path: Union[str, Path]) -> ResponseModel:
        """
        Transcribe audio from a local file.
        
        Args:
            file_path: Path to the audio file
        
        Returns:
            ResponseModel containing the transcription result
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return ResponseModel(
                status=False,
                code=404,
                message=f"File not found: {file_path}",
                data=None
            )
        
        try:
            result = await transcribe_audio(str(file_path), self.model_size, self.device)
            return ResponseModel(
                status=True,
                code=200,
                message="Transcription successful",
                data=result
            )
        except Exception as e:
            return ResponseModel(
                status=False,
                code=500,
                message=f"Transcription failed: {str(e)}",
                data=None
            )

    async def transcribe_url(self, audio_url: str) -> ResponseModel:
        """
        Transcribe audio from a URL.
        
        Args:
            audio_url: URL of the audio file
        
        Returns:
            ResponseModel containing the transcription result
        """
        try:
            # Download file from URL
            temp_file = await save_upload_file(audio_url)
            if not temp_file:
                return ResponseModel(
                    status=False,
                    code=400,
                    message="Failed to download audio file",
                    data=None
                )
            
            # Transcribe the downloaded file
            result = await transcribe_audio(str(temp_file), self.model_size, self.device)
            
            # Clean up temporary file
            await delete_file(str(temp_file))
            
            return ResponseModel(
                status=True,
                code=200,
                message="Transcription successful",
                data=result
            )
        except Exception as e:
            return ResponseModel(
                status=False,
                code=500,
                message=f"Transcription failed: {str(e)}",
                data=None
            )

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from src    .service.upload_file_service import save_upload_file, download_file_from_url
from src    .service.transcription_service import transcribe_audio
from src    .service.delete_audio_file_service import delete_file
from src    .validation.file_audio_validation import validate_audio_file
from src    .models.transcript_request_model import TranscriptRequest
from src    .models.response_model import ResponseModel
from src    .models.response_model import ResponseModel
import os

transcription_router = APIRouter()

@transcription_router.post("/", response_model=ResponseModel[ResponseModel])
async def transcribe(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    if not file and not url:
        return JSONResponse(
            status_code=400,
            content=ResponseModel[None](
                status=False,
                code=400,
                message="No file or URL provided",
                data=None
            ).dict()
        )

    temp_file_path = None
    try:
        if file:
            try:
                validate_audio_file(file.filename)
            except ValueError as ve:
                return JSONResponse(
                    status_code=400,
                    content=ResponseModel[None](
                        status=False,
                        code=400,
                        message=str(ve),
                        data=None
                    ).dict()
                )
            temp_file_path = await save_upload_file(file)
        else:
            try:
                validate_audio_file(url)
            except ValueError as ve:
                return JSONResponse(
                    status_code=400,
                    content=ResponseModel[None](
                        status=False,
                        code=400,
                        message=str(ve),
                        data=None
                    ).dict()
                )
            temp_file_path = await download_file_from_url(url)

        transcription = transcribe_audio(temp_file_path)
        return ResponseModel(
            status=True,
            code=200,
            message="Success",
            data=ResponseModel(text=transcription)
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ResponseModel[None](
                status=False,
                code=500,
                message=f"Internal server error: {str(e)}",
                data=None
            ).dict()
        )

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            delete_file(temp_file_path)

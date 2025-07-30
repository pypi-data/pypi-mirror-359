from fastapi import APIRouter
from src.models.response_model import ResponseModel
from src.models.message_data import MessageData

root_router = APIRouter()

@root_router.get("/", response_model=ResponseModel[MessageData])
async def root():
    return ResponseModel(
        status=True,
        code=200,
        message="Success",
        data=MessageData(message="API is live.")
    )
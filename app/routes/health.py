from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.api_route("/ping", methods=["GET", "HEAD"])
async def ping():
    return PlainTextResponse("pong", status_code=200)

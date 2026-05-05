from fastapi import FastAPI, Request, HTTPException, status, Query
from app.services.whatsapp_service import get_media_url, download_media
from app.services.storage_service import upload_file_to_minio
from app.utils.helpers import build_storage_path
from app.logger import logger
from app.config import settings
from app.schemas.webhook import WebhookPayload
from mimetypes import guess_extension

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(payload: WebhookPayload):
    try:
        for entry in payload.entry or []:
            for change in entry.changes or []:
                messages = (change.value.messages or []) if change.value else []
                for msg in messages:
                    msg_type = msg.type
                    if msg_type in ["image", "document", "video", "audio"]:
                        media = getattr(msg, msg_type)
                        if media:
                            media_id = media.id
                            mime_type = media.mime_type or "application/octet-stream"
                            ext = (mime_type.split('/')[-1] if '/' in mime_type else mime_type)
                            from_number = msg.from_
                            timestamp = msg.timestamp
                            msg_id = msg.id
                            folder, filename = build_storage_path(from_number, timestamp, msg_id, ext)
                            media_url = get_media_url(media_id)
                            content, content_type = download_media(media_url)
                            upload_file_to_minio(folder, filename, content, content_type)
    except Exception as ex:
        logger.error(f"Error procesando webhook: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
    return {"status": "ok"}

@app.get("/webhook")
async def verify_whatsapp(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    return HTTPException(status_code=403, detail="Verification failed")
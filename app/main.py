from fastapi import FastAPI, Request, HTTPException, status, Query
from app.services.whatsapp_service import get_media_url, download_media
from app.services.storage_service import upload_file_to_minio
from app.utils.helpers import build_storage_path
from app.logger import logger
from app.config import settings
from app.schemas.webhook import WebhookPayload
from app.schemas.messages import IncomingMessage
from app.services.providers import get_provider
from app.services.dedup import message_dedup
from mimetypes import guess_extension

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Evolution API endpoint ──────────────────────────────────────────────────

@app.post("/webhook/evolution")
async def evolution_webhook(request: Request):
    """Recibe eventos de Evolution API y almacena los medios en MinIO."""
    # Loguear si se recibió apikey (Evolution envía el token de instancia, no la clave global)
    apikey = request.headers.get("apikey")
    logger.debug(f"webhook/evolution apikey={'present' if apikey else 'missing'}")

    # Validar secreto propio si está configurado (header x-webhook-secret)
    if settings.WEBHOOK_SECRET:
        received_secret = request.headers.get("x-webhook-secret")
        if received_secret != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="x-webhook-secret inválido")

    payload = await request.json()
    provider = get_provider()

    try:
        messages = provider.parse_incoming(payload)
    except Exception as ex:
        logger.error(f"Error parseando payload de Evolution: {ex}")
        return {"status": "ok", "processed": 0}

    processed = 0
    for msg in messages:
        # Idempotencia
        if message_dedup.contains(msg.message_id):
            logger.info(
                f"provider={msg.provider} instance={msg.instance} "
                f"message_id={msg.message_id} DUPLICADO — omitido"
            )
            continue

        logger.info(
            f"provider={msg.provider} instance={msg.instance} "
            f"message_id={msg.message_id} from={msg.from_number} "
            f"media_type={msg.media_type} — procesando"
        )

        try:
            content, content_type = provider.download_media(msg)
        except Exception as ex:
            logger.error(
                f"Error descargando media message_id={msg.message_id}: {ex}"
            )
            continue

        try:
            folder, filename = build_storage_path(
                from_number=msg.from_number,
                timestamp=str(msg.timestamp),
                msg_id=msg.message_id,
                ext="bin",
                mime_type=msg.mime_type,
                original_filename=msg.filename,
            )
            upload_file_to_minio(
                folder=folder,
                filename=filename,
                content=content,
                content_type=content_type,
                from_number=msg.from_number,
                msg_id=msg.message_id,
                provider=msg.provider,
            )
        except Exception as ex:
            logger.error(
                f"Error subiendo media message_id={msg.message_id}: {ex}"
            )
            continue

        message_dedup.add(msg.message_id)
        processed += 1

    return {"status": "ok", "processed": processed}


# ── WhatsApp Cloud API endpoints (activos solo si WHATSAPP_PROVIDER=cloud) ──

@app.post("/webhook")
async def whatsapp_webhook(payload: WebhookPayload):
    if settings.WHATSAPP_PROVIDER != "cloud":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint Cloud API no activo. Usa WHATSAPP_PROVIDER=cloud",
        )
    provider = get_provider()
    raw_payload = payload.model_dump(by_alias=True)

    try:
        messages = provider.parse_incoming(raw_payload)
    except Exception as ex:
        logger.error(f"Error parseando payload Cloud API: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))

    for msg in messages:
        if message_dedup.contains(msg.message_id):
            logger.info(
                f"provider={msg.provider} message_id={msg.message_id} DUPLICADO — omitido"
            )
            continue

        logger.info(
            f"provider={msg.provider} message_id={msg.message_id} "
            f"from={msg.from_number} media_type={msg.media_type} — procesando"
        )

        try:
            content, content_type = provider.download_media(msg)
            folder, filename = build_storage_path(
                from_number=msg.from_number,
                timestamp=str(msg.timestamp),
                msg_id=msg.message_id,
                ext="bin",
                mime_type=msg.mime_type,
                original_filename=msg.filename,
            )
            upload_file_to_minio(
                folder=folder,
                filename=filename,
                content=content,
                content_type=content_type,
                from_number=msg.from_number,
                msg_id=msg.message_id,
                provider=msg.provider,
            )
            message_dedup.add(msg.message_id)
        except Exception as ex:
            logger.error(f"Error procesando mensaje {msg.message_id}: {ex}")
            continue

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
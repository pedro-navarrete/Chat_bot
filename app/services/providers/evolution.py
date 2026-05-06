import base64
from typing import Optional
import httpx
from app.config import settings
from app.logger import logger
from app.schemas.messages import IncomingMessage
from app.services.providers.base import WhatsAppProvider

# Mapeo de claves de mensaje a media_type normalizado
MEDIA_KEY_MAP = {
    "imageMessage": "image",
    "documentMessage": "document",
    "videoMessage": "video",
    "audioMessage": "audio",
}


def _extract_media_info(message_obj: dict) -> Optional[tuple[str, str, dict, Optional[str]]]:
    """
    Devuelve (media_type, mime_type, media_block, filename) o None si no es media.
    Soporta también documentWithCaptionMessage.
    """
    # Caso: documentWithCaptionMessage wrapping a documentMessage
    doc_with_caption = message_obj.get("documentWithCaptionMessage", {})
    if doc_with_caption:
        inner = doc_with_caption.get("message", {}).get("documentMessage")
        if inner:
            return (
                "document",
                inner.get("mimetype", "application/octet-stream"),
                inner,
                inner.get("fileName"),
            )

    for key, media_type in MEDIA_KEY_MAP.items():
        block = message_obj.get(key)
        if block:
            return (
                media_type,
                block.get("mimetype", "application/octet-stream"),
                block,
                block.get("fileName"),
            )
    return None


class EvolutionProvider(WhatsAppProvider):
    """Proveedor para Evolution API (basado en Baileys/WhatsApp Web)."""

    def parse_incoming(self, payload: dict) -> list[IncomingMessage]:
        messages: list[IncomingMessage] = []

        event = payload.get("event", "")
        if event not in ("messages.upsert", "MESSAGES_UPSERT"):
            return messages

        instance = payload.get("instance", settings.EVOLUTION_INSTANCE)
        data = payload.get("data", {})

        # Evolution puede enviar un único objeto o una lista en "data"
        items = data if isinstance(data, list) else [data]

        for item in items:
            key = item.get("key", {})
            if key.get("fromMe", False):
                continue

            remote_jid: str = key.get("remoteJid", "")
            from_number = remote_jid.split("@")[0]

            message_obj = item.get("message", {})
            # Procesar mensajes de texto simples
            if "conversation" in message_obj:
                msg_id = key.get("id", "")
                timestamp = int(item.get("messageTimestamp", 0))
                messages.append(
                    IncomingMessage(
                        provider="evolution",
                        instance=instance,
                        message_id=msg_id,
                        from_number=from_number,
                        timestamp=timestamp,
                        media_type="text",
                        mime_type="text/plain",
                        filename=None,
                        raw={
                            "key": key,
                            "message": message_obj,
                            "instance": instance,
                            "text": message_obj["conversation"],
                        },
                    )
                )
                continue

            extracted = _extract_media_info(message_obj)
            if extracted is None:
                continue

            media_type, mime_type, media_block, filename = extracted
            msg_id = key.get("id", "")
            timestamp = int(item.get("messageTimestamp", 0))

            messages.append(
                IncomingMessage(
                    provider="evolution",
                    instance=instance,
                    message_id=msg_id,
                    from_number=from_number,
                    timestamp=timestamp,
                    media_type=media_type,
                    mime_type=mime_type,
                    filename=filename,
                    raw={
                        "key": key,
                        "message": message_obj,
                        "instance": instance,
                    },
                )
            )

        return messages

    def download_media(self, message: IncomingMessage) -> tuple[bytes, str]:
        instance = message.raw.get("instance", settings.EVOLUTION_INSTANCE)
        url = (
            f"{settings.EVOLUTION_URL}/chat/getBase64FromMediaMessage/{instance}"
        )
        headers = {"apikey": settings.EVOLUTION_API_KEY or ""}
        body = {
            "message": {
                "key": message.raw["key"],
                "message": message.raw["message"],
            },
            "convertToMp4": False,
        }
        with httpx.Client(timeout=60) as client:
            r = client.post(url, json=body, headers=headers)
            r.raise_for_status()

        data = r.json()
        raw_b64 = data.get("base64", "")
        content = base64.b64decode(raw_b64)
        mime = data.get("mimetype") or message.mime_type
        return content, mime

    def verify_webhook(self, params: dict) -> Optional[str]:
        # Evolution no necesita verificación GET; la seguridad se hace
        # validando el header apikey en el POST /webhook/evolution.
        return None

    def send_text(self, to: str, text: str) -> dict:
        instance = settings.EVOLUTION_INSTANCE
        url = f"{settings.EVOLUTION_URL}/message/sendText/{instance}"
        headers = {
            "apikey": settings.EVOLUTION_API_KEY or "",
            "Content-Type": "application/json",
        }
        body = {"number": to, "text": text}
        with httpx.Client(timeout=30) as client:
            r = client.post(url, json=body, headers=headers)
            r.raise_for_status()
        return r.json()

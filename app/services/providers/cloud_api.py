import requests
from typing import Optional
from app.config import settings
from app.logger import logger
from app.schemas.messages import IncomingMessage
from app.services.providers.base import WhatsAppProvider

MEDIA_TYPES = {"image", "document", "video", "audio"}


class CloudApiProvider(WhatsAppProvider):
    """Proveedor para WhatsApp Cloud API (graph.facebook.com)."""

    def parse_incoming(self, payload: dict) -> list[IncomingMessage]:
        messages: list[IncomingMessage] = []
        for entry in payload.get("entry") or []:
            for change in entry.get("changes") or []:
                value = change.get("value") or {}
                for msg in value.get("messages") or []:
                    msg_type = msg.get("type", "")
                    if msg_type not in MEDIA_TYPES:
                        continue
                    media = msg.get(msg_type) or {}
                    mime_type = media.get("mime_type", "application/octet-stream")
                    messages.append(
                        IncomingMessage(
                            provider="cloud",
                            instance=None,
                            message_id=msg["id"],
                            from_number=msg["from"],
                            timestamp=int(msg.get("timestamp", 0)),
                            media_type=msg_type,
                            mime_type=mime_type,
                            filename=media.get("filename"),
                            raw={
                                "media_id": media.get("id"),
                                "mime_type": mime_type,
                            },
                        )
                    )
        return messages

    def download_media(self, message: IncomingMessage) -> tuple[bytes, str]:
        media_id = message.raw.get("media_id")
        token = settings.WHATSAPP_TOKEN
        url_metadata = (
            f"https://graph.facebook.com/v19.0/{media_id}"
            f"?access_token={token}"
        )
        r = requests.get(url_metadata, timeout=30)
        r.raise_for_status()
        media_url = r.json().get("url")
        r2 = requests.get(
            media_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        r2.raise_for_status()
        return r2.content, r2.headers.get("Content-Type", "application/octet-stream")

    def verify_webhook(self, params: dict) -> Optional[str]:
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return challenge
        return None

    def send_text(self, to: str, text: str) -> dict:
        url = (
            f"https://graph.facebook.com/v19.0/"
            f"{settings.PHONE_NUMBER_ID}/messages"
        )
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        body = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        r = requests.post(url, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()

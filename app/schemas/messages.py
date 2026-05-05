from pydantic import BaseModel
from typing import Optional


class IncomingMessage(BaseModel):
    provider: str            # "evolution" | "cloud"
    instance: Optional[str] = None   # nombre de la instancia (Evolution)
    message_id: str          # id único del mensaje (para idempotencia)
    from_number: str         # número del remitente sin sufijos (@s.whatsapp.net)
    timestamp: int           # epoch seconds
    media_type: str          # "image" | "document" | "video" | "audio"
    mime_type: str
    filename: Optional[str] = None   # nombre original si aplica (documentos)
    # Datos crudos para descarga, dependientes del proveedor:
    raw: dict

from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.messages import IncomingMessage


class WhatsAppProvider(ABC):
    """Interfaz común para todos los proveedores de WhatsApp."""

    @abstractmethod
    def parse_incoming(self, payload: dict) -> list[IncomingMessage]:
        """Normaliza el payload del webhook a una lista de IncomingMessage."""
        ...

    @abstractmethod
    def download_media(self, message: IncomingMessage) -> tuple[bytes, str]:
        """Descarga el binario del medio. Devuelve (content, content_type)."""
        ...

    @abstractmethod
    def verify_webhook(self, params: dict) -> Optional[str]:
        """
        Verifica el webhook.
        - Cloud API: devuelve hub.challenge si el token es válido.
        - Evolution: valida el header apikey y devuelve None.
        """
        ...

    def send_text(self, to: str, text: str) -> dict:
        """Envía un mensaje de texto (opcional, por defecto no implementado)."""
        raise NotImplementedError("send_text no implementado para este proveedor")

from app.config import settings
from app.services.providers.base import WhatsAppProvider


def get_provider() -> WhatsAppProvider:
    """
    Devuelve la instancia del proveedor de WhatsApp configurado.
    Controla con la variable de entorno WHATSAPP_PROVIDER.
    """
    provider = (settings.WHATSAPP_PROVIDER or "evolution").lower()
    if provider == "cloud":
        from app.services.providers.cloud_api import CloudApiProvider
        return CloudApiProvider()
    # Por defecto: Evolution API
    from app.services.providers.evolution import EvolutionProvider
    return EvolutionProvider()

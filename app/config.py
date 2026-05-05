import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

class Settings:
    # Proveedor activo: "evolution" (default) | "cloud"
    WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "evolution")

    # ── WhatsApp Cloud API ──────────────────────────────────────────────────
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

    # ── Evolution API ───────────────────────────────────────────────────────
    EVOLUTION_URL = os.getenv("EVOLUTION_URL", "http://evolution-api:8080")
    EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
    EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "default")

    # ── MinIO ───────────────────────────────────────────────────────────────
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "whatsapp-files")

settings = Settings()
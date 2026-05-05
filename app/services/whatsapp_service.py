import requests
from app.config import settings
from app.logger import logger

def get_media_url(media_id: str):
    url_metadata = f"https://graph.facebook.com/v19.0/{media_id}?access_token={settings.WHATSAPP_TOKEN}"
    r = requests.get(url_metadata)
    r.raise_for_status()
    return r.json().get("url")

def download_media(media_url: str):
    r = requests.get(media_url, headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"})
    r.raise_for_status()
    return r.content, r.headers.get("Content-Type", "application/octet-stream")
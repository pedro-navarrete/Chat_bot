from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MediaPayload(BaseModel):
    id: str
    mime_type: Optional[str]

class MessagePayload(BaseModel):
    from_: str
    id: str
    timestamp: str
    type: str
    image: Optional[MediaPayload] = None
    document: Optional[MediaPayload] = None
    video: Optional[MediaPayload] = None
    audio: Optional[MediaPayload] = None

    class Config:
        fields = {
            'from_': 'from'
        }

class ValuePayload(BaseModel):
    messages: Optional[List[MessagePayload]] = []

class ChangePayload(BaseModel):
    value: ValuePayload

class EntryPayload(BaseModel):
    changes: Optional[List[ChangePayload]] = []

class WebhookPayload(BaseModel):
    entry: Optional[List[EntryPayload]] = []
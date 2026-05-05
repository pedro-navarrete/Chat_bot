"""Tests del provider de Evolution API."""
import pytest
from app.services.providers.evolution import EvolutionProvider


@pytest.fixture
def provider():
    return EvolutionProvider()


# ── Fixtures de payloads ──────────────────────────────────────────────────────

DOCUMENT_PAYLOAD = {
    "event": "messages.upsert",
    "instance": "mi-instancia",
    "data": {
        "key": {
            "remoteJid": "521555123456@s.whatsapp.net",
            "fromMe": False,
            "id": "MSG001",
        },
        "messageTimestamp": 1735689600,
        "pushName": "Pedro",
        "message": {
            "documentMessage": {
                "fileName": "factura.pdf",
                "mimetype": "application/pdf",
                "fileLength": "12345",
                "mediaKey": "key123",
                "url": "https://example.com/file",
            }
        },
        "messageType": "documentMessage",
    },
}

IMAGE_PAYLOAD = {
    "event": "messages.upsert",
    "instance": "mi-instancia",
    "data": {
        "key": {
            "remoteJid": "521555000001@s.whatsapp.net",
            "fromMe": False,
            "id": "MSG002",
        },
        "messageTimestamp": 1735689601,
        "message": {
            "imageMessage": {
                "mimetype": "image/jpeg",
                "fileLength": "98765",
            }
        },
        "messageType": "imageMessage",
    },
}

AUDIO_PAYLOAD = {
    "event": "messages.upsert",
    "instance": "mi-instancia",
    "data": {
        "key": {
            "remoteJid": "521555000002@s.whatsapp.net",
            "fromMe": False,
            "id": "MSG003",
        },
        "messageTimestamp": 1735689602,
        "message": {
            "audioMessage": {
                "mimetype": "audio/ogg; codecs=opus",
                "fileLength": "5000",
            }
        },
        "messageType": "audioMessage",
    },
}

DOC_WITH_CAPTION_PAYLOAD = {
    "event": "messages.upsert",
    "instance": "mi-instancia",
    "data": {
        "key": {
            "remoteJid": "521555000003@s.whatsapp.net",
            "fromMe": False,
            "id": "MSG004",
        },
        "messageTimestamp": 1735689603,
        "message": {
            "documentWithCaptionMessage": {
                "message": {
                    "documentMessage": {
                        "fileName": "contrato.docx",
                        "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "fileLength": "30000",
                    }
                }
            }
        },
        "messageType": "documentWithCaptionMessage",
    },
}

FROM_ME_PAYLOAD = {
    "event": "messages.upsert",
    "instance": "mi-instancia",
    "data": {
        "key": {
            "remoteJid": "521555000004@s.whatsapp.net",
            "fromMe": True,
            "id": "MSG005",
        },
        "messageTimestamp": 1735689604,
        "message": {
            "imageMessage": {
                "mimetype": "image/png",
            }
        },
    },
}

TEXT_ONLY_PAYLOAD = {
    "event": "messages.upsert",
    "instance": "mi-instancia",
    "data": {
        "key": {
            "remoteJid": "521555000005@s.whatsapp.net",
            "fromMe": False,
            "id": "MSG006",
        },
        "messageTimestamp": 1735689605,
        "message": {
            "conversation": "Hola!",
        },
    },
}

# ── Tests ─────────────────────────────────────────────────────────────────────

def test_parse_document(provider):
    msgs = provider.parse_incoming(DOCUMENT_PAYLOAD)
    assert len(msgs) == 1
    m = msgs[0]
    assert m.provider == "evolution"
    assert m.instance == "mi-instancia"
    assert m.message_id == "MSG001"
    assert m.from_number == "521555123456"
    assert m.timestamp == 1735689600
    assert m.media_type == "document"
    assert m.mime_type == "application/pdf"
    assert m.filename == "factura.pdf"


def test_parse_image(provider):
    msgs = provider.parse_incoming(IMAGE_PAYLOAD)
    assert len(msgs) == 1
    m = msgs[0]
    assert m.message_id == "MSG002"
    assert m.from_number == "521555000001"
    assert m.media_type == "image"
    assert m.mime_type == "image/jpeg"
    assert m.filename is None


def test_parse_audio(provider):
    msgs = provider.parse_incoming(AUDIO_PAYLOAD)
    assert len(msgs) == 1
    m = msgs[0]
    assert m.message_id == "MSG003"
    assert m.media_type == "audio"
    assert m.mime_type == "audio/ogg; codecs=opus"


def test_parse_document_with_caption(provider):
    msgs = provider.parse_incoming(DOC_WITH_CAPTION_PAYLOAD)
    assert len(msgs) == 1
    m = msgs[0]
    assert m.message_id == "MSG004"
    assert m.media_type == "document"
    assert m.filename == "contrato.docx"


def test_fromme_ignored(provider):
    """Mensajes enviados por mí (fromMe=True) deben ignorarse."""
    msgs = provider.parse_incoming(FROM_ME_PAYLOAD)
    assert msgs == []


def test_text_ignored(provider):
    """Mensajes de texto sin media deben ignorarse."""
    msgs = provider.parse_incoming(TEXT_ONLY_PAYLOAD)
    assert msgs == []


def test_non_upsert_event_ignored(provider):
    payload = {**DOCUMENT_PAYLOAD, "event": "connection.update"}
    msgs = provider.parse_incoming(payload)
    assert msgs == []


def test_raw_contains_key_and_message(provider):
    msgs = provider.parse_incoming(DOCUMENT_PAYLOAD)
    m = msgs[0]
    assert "key" in m.raw
    assert "message" in m.raw
    assert m.raw["key"]["id"] == "MSG001"

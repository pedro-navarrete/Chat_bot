"""Tests de build_storage_path."""
import pytest
from app.utils.helpers import build_storage_path


TIMESTAMP = "1735689600"  # 2025-01-01


def test_basic_ext():
    folder, filename = build_storage_path("5215551234", TIMESTAMP, "MSGABC", "pdf")
    assert folder == "5215551234/2025-01-01"
    assert filename == "MSGABC.pdf"


def test_mime_type_pdf():
    folder, filename = build_storage_path(
        "5215551234", TIMESTAMP, "MSGABC", "bin",
        mime_type="application/pdf"
    )
    assert folder == "5215551234/2025-01-01"
    assert filename.startswith("MSGABC")
    assert filename.endswith(".pdf")


def test_mime_type_jpeg():
    folder, filename = build_storage_path(
        "5215551234", TIMESTAMP, "MSGABC", "bin",
        mime_type="image/jpeg"
    )
    assert filename.endswith(".jpg")


def test_mime_type_png():
    folder, filename = build_storage_path(
        "5215551234", TIMESTAMP, "MSGABC", "bin",
        mime_type="image/png"
    )
    assert filename.endswith(".png")


def test_mime_type_ogg():
    folder, filename = build_storage_path(
        "5215551234", TIMESTAMP, "MSGABC", "bin",
        mime_type="audio/ogg"
    )
    assert "MSGABC" in filename


def test_original_filename_preserved():
    folder, filename = build_storage_path(
        "5215551234", TIMESTAMP, "MSGABC", "bin",
        mime_type="application/pdf",
        original_filename="factura.pdf",
    )
    assert "MSGABC" in filename
    assert "factura.pdf" in filename


def test_original_filename_sanitized():
    folder, filename = build_storage_path(
        "5215551234", TIMESTAMP, "MSGABC", "bin",
        original_filename="../../../etc/passwd",
    )
    # werkzeug secure_filename removes path traversal
    assert ".." not in filename
    assert "/" not in filename


def test_folder_date_format():
    folder, _ = build_storage_path("123", TIMESTAMP, "X", "txt")
    parts = folder.split("/")
    assert len(parts) == 2
    assert parts[1] == "2025-01-01"

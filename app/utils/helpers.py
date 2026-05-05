import mimetypes
from datetime import datetime
from typing import Optional
from werkzeug.utils import secure_filename

# Normalización de extensiones que mimetypes puede devolver con variantes menores
_EXT_NORMALIZE = {
    ".jpe": "jpg",
    ".jpeg": "jpg",
    ".jfif": "jpg",
}


def build_storage_path(
    from_number: str,
    timestamp: str,
    msg_id: str,
    ext: str,
    mime_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> tuple[str, str]:
    """
    Devuelve (folder, filename) para almacenar el archivo en MinIO.

    Ruta: {from_number}/{YYYY-MM-DD}/{msg_id}[_{original_filename}].{ext}

    Si se proporciona mime_type, se deriva la extensión desde él
    (con fallback a la parte final del mime_type).
    Si se proporciona original_filename, se añade como sufijo al msg_id.
    """
    date_folder = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

    # Determinar la extensión
    if mime_type:
        guessed = mimetypes.guess_extension(mime_type)
        if guessed:
            ext = _EXT_NORMALIZE.get(guessed, guessed.lstrip("."))
        else:
            # Fallback: parte final del mime_type
            ext = mime_type.split("/")[-1].split(";")[0].strip()

    if original_filename:
        safe_original = secure_filename(original_filename)
        filename = secure_filename(f"{msg_id}_{safe_original}")
    else:
        filename = secure_filename(f"{msg_id}.{ext}")

    return f"{from_number}/{date_folder}", filename
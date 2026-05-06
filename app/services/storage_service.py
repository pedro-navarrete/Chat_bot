import boto3
from botocore.client import Config
from app.config import settings
from app.logger import logger
import json


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )


def upload_file_to_minio(
    folder: str,
    filename: str,
    content: bytes,
    content_type: str,
    from_number: str = "",
    msg_id: str = "",
    provider: str = "",
) -> bool:
    s3 = get_s3_client()
    key = f"{folder}/{filename}"
    metadata = {}
    if from_number:
        metadata["from"] = from_number
    if msg_id:
        metadata["message-id"] = msg_id
    if provider:
        metadata["provider"] = provider
    try:
        s3.put_object(
            Bucket=settings.MINIO_BUCKET,
            Key=key,
            Body=content,
            ContentType=content_type,
            Metadata=metadata,
        )
        logger.info(f"Archivo subido a {key}")
        return True
    except Exception as ex:
        logger.error(f"Error subiendo archivo a MinIO - {ex}")
        return False


def upload_metadata_json_to_minio(
    folder: str,
    base_filename: str,
    nombre: str,
    dui: str,
    from_number: str = "",
    msg_id: str = "",
    provider: str = "",
) -> bool:
    """
    Sube un archivo JSON con los metadatos (nombre y dui) junto al archivo principal en MinIO.
    El archivo se llamará igual que el archivo principal pero con extensión .json
    """
    metadata = {
        "nombre": nombre,
        "dui": dui,
    }
    json_bytes = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
    json_filename = base_filename.rsplit(".", 1)[0] + ".json"
    return upload_file_to_minio(
        folder=folder,
        filename=json_filename,
        content=json_bytes,
        content_type="application/json",
        from_number=from_number,
        msg_id=msg_id,
        provider=provider,
    )

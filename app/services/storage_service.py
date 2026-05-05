import boto3
from botocore.client import Config
from app.config import settings
from app.logger import logger


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
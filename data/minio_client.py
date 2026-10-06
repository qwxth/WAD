import uuid
import re
import json
from io import BytesIO
from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "root"
MINIO_SECRET_KEY = "rootpassword"
MINIO_BUCKET = "load-patterns"
MINIO_PUBLIC_URL = "http://localhost:9000"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


def _public_read_policy(bucket_name: str) -> str:
    """Политика публичного чтения для анонимных пользователей"""
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
            }
        ]
    })


def ensure_bucket():
    """Создаёт bucket (если не существует) и делает его публично читаемым"""
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"✅ Bucket '{MINIO_BUCKET}' создан")

        # Всегда применяем публичную политику (идемпотентно)
        policy = _public_read_policy(MINIO_BUCKET)
        minio_client.set_bucket_policy(MINIO_BUCKET, policy)
        print(f"✅ Bucket '{MINIO_BUCKET}' сделан публичным для чтения")

    except S3Error as e:
        print(f"⚠️ MinIO bucket error: {e}")


def generate_latin_filename(original_filename: str) -> str:
    """Генерирует латинское имя файла"""
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[-1].lower()
        ext = re.sub(r'[^a-z0-9.]', '', ext)
    unique_id = uuid.uuid4().hex[:12]
    return f"pattern_{unique_id}{ext}"


def upload_file(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Загружает файл в MinIO, возвращает публичный URL"""
    ensure_bucket()
    data = BytesIO(file_bytes)
    minio_client.put_object(
        MINIO_BUCKET,
        filename,
        data,
        length=len(file_bytes),
        content_type=content_type,
    )
    return f"{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{filename}"

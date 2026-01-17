from minio import Minio
import os

client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="password123",
    secure=False
)

bucket_name = "wiki-images"

if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

image_dir = "data/images"

for img in os.listdir(image_dir):
    file_path = os.path.join(image_dir, img)
    client.fput_object(
        bucket_name,
        img,
        file_path
    )
    print(f"Uploaded {img}")

print("✅ Images uploaded to MinIO")

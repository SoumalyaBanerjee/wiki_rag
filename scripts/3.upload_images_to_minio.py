from minio import Minio
import os

client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="password123",
    secure=False
)

bucket_name = "wiki-images"
image_dir = "data/demo_images"

if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)
    print("Created bucket:", bucket_name)

for img in os.listdir(image_dir):
    file_path = os.path.join(image_dir, img)

    if not os.path.isfile(file_path):
        continue

    client.fput_object(
        bucket_name,
        img,
        file_path,
        content_type="image/jpeg"
    )

    print(f"Uploaded {img}")

print("✅ Images uploaded to MinIO")

from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def make_image(
    name: str = "test.jpg",
    size: tuple[int, int] = (100, 100),
    color: tuple[int, int, int] = (255, 0, 0),
    format: str = "JPEG",
):
    buffer = BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buffer, format=format)
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")

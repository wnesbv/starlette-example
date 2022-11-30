
from pathlib import Path

from starlette_files.constants import MB
from starlette_files.fields import ImageAttachment
from starlette_files.storages import FileSystemStorage


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
root_directory = BASE_DIR / "static/upload"


class FileType(ImageAttachment):
    storage = FileSystemStorage(root_directory)
    directory = "img"
    allowed_content_types = ["image/jpeg", "image/png"]
    max_length = MB * 2

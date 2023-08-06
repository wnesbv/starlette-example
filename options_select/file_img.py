
import os
from pathlib import Path, PurePosixPath

from PIL import Image

from sqlalchemy import func, and_
from sqlalchemy.future import select

from starlette.exceptions import HTTPException

from db_config.settings import settings


def img_creat(
    request, file, mdl
):

    save_path = f"./static/upload/{mdl}/{request.user.email}"
    file_path = f"{save_path}/{file.filename}"

    ext = PurePosixPath(file.filename).suffix
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=400,
            detail="Format files: png, jpg, jpeg ..!",
        )
    if Path(file_path).exists():
        raise HTTPException(
            status_code=400,
            detail="Error..! File exists..!"
        )

    os.makedirs(save_path, exist_ok=True)

    with open(f"{file_path}", "wb") as fle:
        fle.write(file.file.read())

    return file_path.replace(".", "", 1)


def img_url(
    request, file, mdl
):

    save_path = f"./static/upload/{mdl}/{request.user.email}"
    file_path = f"{save_path}/{file.filename}"

    return file_path


def img_size(
    request, file, mdl, basewidth
):
    url = img_url(request, file, mdl)
    img = Image.open(f"{url}")
    # ..
    wpercent = basewidth/float(img.size[0])
    hsize = int((float(img.size[1])*float(wpercent)))
    # ..
    img_resize = img.resize((basewidth,hsize), Image.Resampling.LANCZOS)
    img_resize.save(f"{url}")

    return img_resize

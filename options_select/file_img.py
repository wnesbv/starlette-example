
import os
from pathlib import Path, PurePosixPath

from PIL import Image

from starlette.exceptions import HTTPException


async def img_creat(
    request, file, mdl, basewidth
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

        img = Image.open(file_path)
        # ..
        wpercent = basewidth/float(img.size[0])
        hsize = int((float(img.size[1])*float(wpercent)))
        # ..
        img_resize = img.resize((basewidth,hsize), Image.Resampling.LANCZOS)
        img_resize.save(file_path)

    return file_path.replace(".", "", 1)

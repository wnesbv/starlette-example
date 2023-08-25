
from datetime import datetime, timedelta
import os, shutil
from pathlib import Path, PurePosixPath

from PIL import Image

from starlette.exceptions import HTTPException
from config.settings import BASE_DIR


async def img_creat(file, mdl, email, id_fle, basewidth):
    # ..
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{mdl}/{email}/{id_fle}"
    # ..
    ext = PurePosixPath(file.filename).suffix
    file_path = f"{save_path}/{name}{ext}"
    # ..
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=400,
            detail="Format files: png, jpg, jpeg ..!",
        )
    if Path(file_path).exists():
        raise HTTPException(status_code=400, detail="Error..! File exists..!")
    os.makedirs(save_path, exist_ok=True)

    with open(file_path, "wb") as fle:
        fle.write(file.file.read())

        img = Image.open(file_path)
        # ..
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        # ..
        img_resize = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
        img_resize.save(file_path)

    return file_path.replace(".", "", 1)


async def sl_img_creat(
    request, file, mdl, id_sl, basewidth
):
    # ..
    user = request.user.email
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{mdl}/{user}/{id_sl}"
    # ..
    ext = PurePosixPath(file.filename).suffix
    file_path = f"{save_path}/{name}{ext}"
    #..
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

    with open(file_path, "wb") as fle:
        fle.write(file.file.read())

        img = Image.open(file_path)
        # ..
        wpercent = basewidth/float(img.size[0])
        hsize = int((float(img.size[1])*float(wpercent)))
        # ..
        img_resize = img.resize((basewidth,hsize), Image.Resampling.LANCZOS)
        img_resize.save(file_path)

    return file_path.replace(".", "", 1)


async def id_fle_delete_user(email):
    # ..
    directory = [
        (BASE_DIR / f"static/upload/user/{email}"),
        (BASE_DIR / f"static/upload/item/{email}"),
        (BASE_DIR / f"static/upload/rent/{email}"),
        (BASE_DIR / f"static/upload/service/{email}"),
    ]
    for i in directory:
        if Path(i).exists():
            shutil.rmtree(i)

async def id_fle_delete_tm(mdl, email, id_fle):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{mdl}/{email}/{id_fle}"
    )
    if Path(directory).exists():
        shutil.rmtree(directory)

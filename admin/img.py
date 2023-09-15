
from datetime import datetime, timedelta
import os, shutil
from pathlib import Path, PurePosixPath

from PIL import Image

from starlette.exceptions import HTTPException
from config.settings import BASE_DIR

from auth_privileged.opt_slc import get_privileged_user, privileged, owner_prv, get_owner_prv, id_and_owner_prv


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
    request, session, file, mdl, id_sl, basewidth
):
    # ..
    prv = await get_privileged_user(request, session)
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{mdl}/{prv}/{id_sl}"
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


# ..


async def item_img(name, save_path, file, basewidth):
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


async def user_img_creat(file, email, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/user/{email}"
    obj = await item_img(name, save_path, file, basewidth)
    return obj

async def item_img_creat(file, email, id, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{email}/item/{id}_tm"
    obj = await item_img(name, save_path, file, basewidth)
    return obj


async def rent_img_creat(file, email, tm_id, id, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{email}/item/{tm_id}_tm/rent/{id}"
    obj = await item_img(name, save_path, file, basewidth)
    return obj


async def service_img_creat(file, email, tm_id, id, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{email}/item/{tm_id}_tm/service/{id}"
    obj = await item_img(name, save_path, file, basewidth)
    return obj


async def del_user(email):
    # ..
    directory = [
        (BASE_DIR / f"static/upload/user/{email}"),
        (BASE_DIR / f"static/upload/{email}"),
    ]
    for i in directory:
        if Path(i).exists():
            shutil.rmtree(i)


async def del_tm(email, id):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{email}/item/{id}_tm"
    )
    if Path(directory).exists():
        shutil.rmtree(directory)


async def del_rent(email, tm_id, id):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{email}/item/{tm_id}_tm/rent/{id}"
    )
    if Path(directory).exists():
        shutil.rmtree(directory)


async def del_service(email, tm_id, id):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{email}/item/{tm_id}_tm/service/{id}"
    )
    if Path(directory).exists():
        shutil.rmtree(directory)

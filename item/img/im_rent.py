
from datetime import datetime

from admin.img import item_img


async def im_creat(file, email, tm_id, id, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{email}/item/{tm_id}_tm/rent/{id}"
    obj = await item_img(name, save_path, file, basewidth)
    return obj


from datetime import datetime

from admin.img import item_img


async def im_creat(file, email, id, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{email}/item/{id}_tm"
    obj = await item_img(name, save_path, file, basewidth)
    return obj

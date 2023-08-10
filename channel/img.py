
from datetime import datetime

import io, os, base64, json

from PIL import Image

from . import views


def update_file(user, file):

    basewidth = 800
    f_time = datetime.now()

    save_path = f"./static/upload/chat/{user}/"
    os.makedirs(save_path, exist_ok=True)

    with Image.open(io.BytesIO(base64.decodebytes(bytes(file, "utf-8")))) as fle:
        save_img = (
            f"{save_path}"
            + f"{f_time.strftime('%Y-%m-%d-%H-%M-%S')}.{(fle.format).lower()}"
        )
        fle.save(save_img)

    img = Image.open(save_img)
    # ..
    wpercent = basewidth / float(img.size[0])
    hsize = int((float(img.size[1]) * float(wpercent)))
    # ..
    img_resize = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
    img_resize.save(save_img)

    return save_img.replace(".", "", 1)

from datetime import datetime
from pathlib import Path

import tempfile, csv, uuid


async def import_csv(request, model, session):
    # ..
    form = await request.form()
    # ..
    url_f = form["url_f"]
    # ..
    temp = tempfile.NamedTemporaryFile(delete=False)
    print("temp name..", temp.name)

    contents = url_f.file.read()

    with temp as csvf:
        csvf.write(contents)
    url_f.file.close()

    with open(temp.name, "r", encoding="utf-8") as csvfile:
        session.add_all(
            [
                model(
                    **{
                        "title": i["title"],
                        "description": i["description"],
                        "item_owner": request.user.user_id,
                        "created_at": datetime.now(),
                    }
                )
                for i in csv.DictReader(csvfile)
            ]
        )

        csvfile.close()
        Path.unlink(f"{temp.name}")

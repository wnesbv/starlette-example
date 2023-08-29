
from datetime import datetime, timedelta

import os, csv
from config.settings import BASE_DIR


async def export_csv(request, result):
    user = request.user.email
    directory = (
        BASE_DIR
        / f"static/csv/{user}"
    )
    os.makedirs(directory, exist_ok=True)
    # ..
    with open(f"{directory}/export_csv.csv", "w", encoding="utf-8") as csvfile:
        fle = csv.writer(csvfile)
        fle.writerow(
            [
                "id",
                "title",
                "description",
                "file",
                "created_at",
                "modified_at",
                "item_owner",
            ]
        )
        for i in result:
            fle.writerow(
                [
                    i.id,
                    i.title,
                    i.description,
                    i.file,
                    i.created_at,
                    i.modified_at,
                    i.item_owner,
                ]
            )

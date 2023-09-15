
from datetime import datetime, timedelta

import os, csv
from config.settings import BASE_DIR


async def export_csv(result, prv):
    directory = (
        BASE_DIR
        / f"static/csv/{prv}"
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
                "owner",
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
                    i.owner,
                ]
            )

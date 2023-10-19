
import io, csv, datetime

from starlette.responses import Response

from auth_privileged.opt_slc import (
    get_privileged_user,
    privileged,
    owner_prv,
)

from item.models import Item, Service, Rent


async def export_csv(request, session):

    prv = await get_privileged_user(request, session)
    result = await owner_prv(session, Item, prv)
    output = io.StringIO()
    fle = csv.writer(output)
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

    content = output.getvalue()
    headers = {"Content-Disposition": f"attachment;filename=or_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"}

    return Response(content, headers=headers)

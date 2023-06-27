
from sqlalchemy import delete
from sqlalchemy.future import select

from starlette.authentication import requires
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from options_select.opt_slc import in_person_participant, person_participant

from .models import PersonParticipant


templates = Jinja2Templates(directory="templates")


@requires("authenticated", redirect="user_login")
# ...
async def participant_create(
    request
):
    id = request.path_params["id"]
    template = "/participant/create.html"

    async with async_session() as session:
        # ...
        if request.method == "GET":
            #..
            double = await in_person_participant(request, session)
            if not double:
                return templates.TemplateResponse(
                    template, {"request": request,}
                )
            return RedirectResponse(
                f"/chat/group/{id}",
                status_code=302,
            )
        # ...
        if request.method == "POST":
            #..
            form = await request.form()
            #..
            group_participant = id
            participant = request.user.user_id
            explanations_person = form["explanations_person"]
            #..
            new = PersonParticipant()
            new.participant = participant
            new.group_participant = group_participant
            new.explanations_person = explanations_person
            new.created_at = datetime.now()

            session.add(new)
            session.refresh(new)
            await session.commit()

            response = RedirectResponse(
                f"/chat/group/{id}",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def participant_list(
    request
):

    id = request.path_params["id"]
    template = "/participant/list.html"

    async with async_session() as session:
        #..
        odj_admin = person_participant(request, session)
        if odj_admin:
            stmt = await session.execute(
                select(PersonParticipant)
                .where(
                    PersonParticipant.group_participant == id
                )
            )
            odj_list = stmt.scalars().all()
            context = {
                "request": request,
                "odj_list": odj_list,
            }
            return templates.TemplateResponse(
                template, context
            )
        return PlainTextResponse("Or, you don't have viewing rights. Or, there are no applications")
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def participant_add(
    request
):
    id = request.path_params["id"]

    async with async_session() as session:
        #..
        odj_admin = person_participant(request, session)
        if odj_admin:
            stmt = await session.execute(
                select(PersonParticipant)
                .where(
                    PersonParticipant.id == id,
                )
            )
            detail = stmt.scalars().first()
            # ..
            detail.permission = True
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@requires("authenticated", redirect="user_login")
# ...
async def participant_delete(
    request
):
    id = request.path_params["id"]

    async with async_session() as session:
        #..
        odj_admin = person_participant(request, session)
        if odj_admin:
            # ..
            query = (
                delete(PersonParticipant)
                .where(
                    PersonParticipant.id == id
                )
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()


from datetime import datetime

from sqlalchemy import delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from account.opt_slc import auth
from channel.models import GroupChat

from db_config.storage_config import engine, async_session

from options_select.opt_slc import for_id
from auth_privileged.opt_slc import get_privileged_user

from .models import PersonParticipant
from .opt_slc import person_participant, all_true, all_false, stop_double


templates = Jinja2Templates(directory="templates")


@auth()
# ...
async def participant_create(request):
    # ..
    id = request.path_params["id"]
    template = "/participant/create.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            # ..
            if prv:
                double = await stop_double(
                    session, PersonParticipant, prv.id, id
                )
            # ..
            if request.cookies.get("visited"):
                double = await stop_double(
                    session, PersonParticipant, request.user.user_id, id
                )
            # ...
            if not double:
                return templates.TemplateResponse(
                    template, {"request": request},
                )
            return RedirectResponse(
                f"/chat/group/{ id }",
                status_code=302,
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            if prv:
                owner = prv.id

            if request.cookies.get("visited"):
                owner = request.user.user_id
            # ..
            community = id
            explanatory_note = form["explanatory_note"]
            # ..
            new = PersonParticipant()
            new.owner = owner
            new.community = community
            new.explanatory_note = explanatory_note
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            return RedirectResponse(
                f"/chat/group/{id}",
                status_code=302,
            )
    await engine.dispose()


@auth()
# ...
async def participant_list(request):
    id = request.path_params["id"]
    template = "/participant/list.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        in_true = await all_true(session, id)
        in_false = await all_false(session, id)
        # ..
        context = {"request": request}
        # ..
        if prv:
            obj_prv = await person_participant(session, GroupChat, prv.id)
            if obj_prv:
                context["in_true"] = in_true
                context["in_false"] = in_false
        # ..
        if request.cookies.get("visited"):
            obj_user = await person_participant(session, GroupChat, request.user.user_id)
            if obj_user:
                context["in_true"] = in_true
                context["in_false"] = in_false
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@auth()
# ...
async def participant_add(request):
    # ..
    id = request.path_params["id"]

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if prv:
            obj_prv = await person_participant(session, GroupChat, prv.id)
        # ..
        if request.cookies.get("visited"):
            obj_user = await person_participant(session, GroupChat, request.user.user_id)
        #...
        if obj_prv or obj_user:
            i = await for_id(session, PersonParticipant, id)
            # ..
            i.permission = True
            await session.commit()
            # ..
            return RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
    await engine.dispose()


@auth()
# ...
async def participant_delete(request):
    # ..
    id = request.path_params["id"]

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if prv:
            obj_prv = await person_participant(session, GroupChat, prv.id)
        # ..
        if request.cookies.get("visited"):
            obj_user = await person_participant(session, GroupChat, request.user.user_id)
        if obj_prv or obj_user:
            # ..
            query = delete(PersonParticipant).where(PersonParticipant.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()

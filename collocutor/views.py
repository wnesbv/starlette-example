from datetime import datetime

from sqlalchemy import delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from account.opt_slc import auth

from db_config.storage_config import engine, async_session

from options_select.opt_slc import left_right_first

from channel.models import OneOneChat

from auth_privileged.opt_slc import get_random_string, get_privileged_user

from .models import PersonCollocutor
from .opt_slc import (
    stop_double,
    owner_true,
    owner_false,
    to_user_true,
    to_user_false,
    person_collocutor,
)


templates = Jinja2Templates(directory="templates")


@auth()
# ...
async def collocutor_create(request):
    # ..
    template = "/collocutor/create.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            # ..
            if prv:
                obj_list = await stop_double(session, prv.id)
            # ..
            if request.cookies.get("visited"):
                obj_list = await stop_double(session, request.user.user_id)
                # ..
            return templates.TemplateResponse(
                template, {"request": request, "obj_list": obj_list}
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            if prv:
                owner = prv.id
            # ..
            if request.cookies.get("visited"):
                owner = request.user.user_id
            # ..
            community = form["community"]
            explanatory_note = form["explanatory_note"]
            # ..
            new = PersonCollocutor()
            new.owner = owner
            new.community = community
            new.explanatory_note = explanatory_note
            new.created_at = datetime.now()

            session.add(new)
            await session.commit()

            response = RedirectResponse(
                "/collocutor/owner-list",
                status_code=302,
            )
            return response
    await engine.dispose()


@auth()
# ...
async def collocutor_add(request):
    # ..
    id = request.path_params["id"]

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if prv:
            obj_prv = await person_collocutor(session, prv.id, id)
            # ...
            if obj_prv:
                # ..
                i = await left_right_first(session, PersonCollocutor, PersonCollocutor.id, id)
                i.permission = True
                i.ref_num = await get_random_string()
                # ..
                await session.commit()
                # ..
                new = OneOneChat()
                new.owner = prv.id
                new.one_one = i.id
                new.message = "message"
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/chat/user/{ i.ref_num }",
                    status_code=302,
                )
        if request.cookies.get("visited"):
            obj_user = await person_collocutor(session, request.user.user_id, id)
            # ...
            if obj_user:
                # ..
                i = await left_right_first(session, PersonCollocutor, PersonCollocutor.id, id)
                i.permission = True
                i.ref_num = await get_random_string()
                # ..
                await session.commit()
                # ..
                new = OneOneChat()
                new.owner = request.user.user_id
                new.one_one = i.id
                new.message = "message"
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
                # ..
                return RedirectResponse(
                    f"/chat/user/{ i.ref_num }",
                    status_code=302,
                )
    await engine.dispose()


@auth()
# ...
async def collocutor_delete(request):
    # ..
    id = request.path_params["id"]

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if prv:
            obj_prv = await person_collocutor(session, prv.id, id)
        # ..
        if request.cookies.get("visited"):
            obj_user = await person_collocutor(session, request.user.user_id, id)
        #...
        if obj_prv or obj_user:
            # ..
            query = delete(PersonCollocutor).where(PersonCollocutor.id == id)
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            return RedirectResponse(
                "/chat/collocutor/list",
                status_code=302,
            )
    await engine.dispose()


@auth()
# ...
async def call_owner(request):
    # ..
    template = "/collocutor/list.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        context = {"request": request, "prv": prv}
        # ..
        if prv:
            i_true = await owner_true(session, prv.id)
            i_false = await owner_false(session, prv.id)
            # ..
            context["i_true"] = i_true
            context["i_false"] = i_false
        # ..
        if request.cookies.get("visited"):
            i_true = await owner_true(session, request.user.user_id)
            i_false = await owner_false(session, request.user.user_id)
            # ..
            context["i_true"] = i_true
            context["i_false"] = i_false
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@auth()
# ...
async def call_to_user(request):
    # ..
    template = "/collocutor/list.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        context = {"request": request, "prv": prv}
        # ..
        if prv:
            i_true = await to_user_true(session, prv.id)
            i_false = await to_user_false(session, prv.id)
            context["i_true"] = i_true
            context["i_false"] = i_false
        # ..
        if request.cookies.get("visited"):
            i_true = await to_user_true(session, request.user.user_id)
            i_false = await to_user_false(session, request.user.user_id)
            context["i_true"] = i_true
            context["i_false"] = i_false
        return templates.TemplateResponse(template, context)
    await engine.dispose()

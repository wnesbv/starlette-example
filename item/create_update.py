
from pathlib import Path
from datetime import datetime

from sqlalchemy import update as sqlalchemy_update

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from mail.send import send_mail
from account.models import User

from options_select.opt_slc import for_id

from auth_privileged.opt_slc import get_privileged_user, id_and_owner_prv, owner_prv


templates = Jinja2Templates(directory="templates")


async def parent_create(request, model, obj, img):
    # ..
    basewidth = 800
    template = f"/{obj}/create.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            return templates.TemplateResponse(
                template, {"request": request},
            )
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            owner = prv.id
            # ..
            if file.filename == "":
                new = model()
                new.title = title
                new.description = description
                new.owner = owner
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
                # ..
                await send_mail(f"A new object has been created - {new}: {title}")
                # ..
                return RedirectResponse(
                    f"/item/{obj}/details/{ new.id }",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, owner)
            new = model()
            new.title = title
            new.description = description
            new.owner = owner
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            # ..
            new.file = await img.item_img_creat(file, email.email, new.id, basewidth)
            session.add(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}: {title}")
            # ..
            return RedirectResponse(
                f"/item/{obj}/details/{ new.id }",
                status_code=302,
            )

    await engine.dispose()


async def child_img_create(
    request, form, belongs, model, new, item, re_item, img
):
    # ..
    basewidth = 800
    template = f"/{item}/create.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            # ..
            obj_item = await owner_prv(session, model, prv)
            # ..
            if obj_item:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "obj_item": obj_item,
                    },
                )
            return RedirectResponse(f"/{re_item}/create")
        # ...
        if request.method == "POST":
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            # ..
            if file.filename == "":
                # ..
                new.title = title
                new.description = description
                new.owner = prv.id
                new.created_at = datetime.now()
                # ..
                session.add(new)
                await session.commit()
                # ..
                await send_mail(f"A new object has been created - {new}: {title}")
                # ..
                return RedirectResponse(
                    f"/item/{item}/details/{ new.id }",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, prv.id)
            # ..
            new.title = title
            new.description = description
            new.owner = prv.id
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            new.file = await img.im_creat(
                file, email.email, belongs, new.id, basewidth
            )
            session.add(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}: {title}")
            # ..
            return RedirectResponse(
                f"/item/{item}/details/{ new.id }",
                status_code=302,
            )

    await engine.dispose()


async def child_img_update(request, model, id, item, img):
    # ..
    basewidth = 800
    template = f"/{item}/update.html"

    async with async_session() as session:
        # ..
        i = await id_and_owner_prv(request, session, model, id)
        # ..
        if request.method == "GET":
            if i:
                context = {
                    "request": request,
                    "i": i,
                }
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            file = form["file"]
            del_obj = form.get("del_bool")
            # ..
            if file.filename == "":
                query = (
                    sqlalchemy_update(model)
                    .where(model.id == id)
                    .values(
                        title=title,
                        description=description,
                        file=i.file,
                        modified_at=datetime.now(),
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(query)
                await session.commit()

                if del_obj:
                    if Path(f".{i.file}").exists():
                        Path.unlink(f".{i.file}")

                    fle_not = (
                        sqlalchemy_update(model)
                        .where(model.id == id)
                        .values(file=None, modified_at=datetime.now())
                        .execution_options(synchronize_session="fetch")
                    )
                    await session.execute(fle_not)
                    await session.commit()
                    # ..
                    await send_mail(
                        f"changes were made at the facility - {i}: {i.title}"
                    )
                    # ..
                    return RedirectResponse(
                        f"/item/{item}/details/{id}",
                        status_code=302,
                    )
                return RedirectResponse(
                    f"/item/{item}/details/{id}",
                    status_code=302,
                )
            # ..
            email = await for_id(session, User, i.owner)
            file_query = (
                sqlalchemy_update(model)
                .where(model.id == id)
                .values(
                    title=title,
                    description=description,
                    file=await img.im_creat(file, email.email, id, basewidth),
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(file_query)
            await session.commit()
            # ..
            await send_mail(f"changes were made at the facility - {i}: {i.title}")
            # ..
            return RedirectResponse(
                f"/item/{item}/details/{id}",
                status_code=302,
            )
    await engine.dispose()



async def child_create(
    request, context, form, model, new, item, re_item
):
    # ..
    template = f"/{item}/create.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        # ..
        if request.method == "GET":
            # ..
            obj_list = await owner_prv(session, model, prv)
            # ..
            if obj_list:
                context["request"] = request
                context["obj_list"] = obj_list
                return templates.TemplateResponse(
                    template, context
                )
            return RedirectResponse(f"/item/{re_item}/create")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            # ...
            new.title = title
            new.description = description
            new.owner = prv.id
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.commit()
            # ..
            await send_mail(f"A new object has been created - {new}: {title}")
            # ..
            response = RedirectResponse(
                f"/item/{item}/details/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


async def child_update(request, context, model, id, form, item):
    # ..
    template = f"/{item}/update.html"

    async with async_session() as session:
        # ..
        i = await id_and_owner_prv(request, session, model, id)
        # ..
        if request.method == "GET":
            if i:
                context["request"] = request
                context["i"] = i
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = (
                sqlalchemy_update(model)
                .where(model.id == id)
                .values(
                    **form,
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            await send_mail(f"changes were made at the facility - {i}: {i.title}")
            # ..
            response = RedirectResponse(
                f"/item/{item}/details/{ id }",
                status_code=302,
            )
            return response
    await engine.dispose()


from sqlalchemy import select, insert, update as sqlalchemy_update, delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from db_config.storage_config import engine, async_session

from auth_privileged.opt_slc import get_privileged_user
from account.views import auth

from .opt_slc import one_one_select, one_one_group


templates = Jinja2Templates(directory="templates")


@auth()
#...
async def user_details(request):
    # ..
    ref_num = request.path_params["ref_num"]
    template = "/one_one/details.html"

    if request.method == "GET":
        async with async_session() as session:
            # ..
            prv = await get_privileged_user(request, session)
            # ..
            context = {
                "request": request,
                "prv": prv,
                "ref_num": ref_num,
            }
            # ..
            if prv:
                user = await one_one_select(session, ref_num, prv.id)
                if user:
                    obj_list = await one_one_group(session, ref_num)
                    # ..
                    context["user"] = user
                    context["obj_list"] = obj_list
                    return templates.TemplateResponse(template, context)
                return RedirectResponse("/")
            # ..
            if request.cookies.get("visited"):
                user = await one_one_select(session, ref_num, request.user.user_id)
                if user:
                    obj_list = await one_one_group(session, ref_num)
                    # ..
                    context["user"] = user
                    context["obj_list"] = obj_list
                    return templates.TemplateResponse(template, context)
                return RedirectResponse("/")
        await engine.dispose()

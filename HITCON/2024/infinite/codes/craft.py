from fastapi import APIRouter
import httpx

from ..db import db
from ..config import config
from ..model import Query
from ..ratelimit import RateLimitMiddleware

from koh_infinite_craft.client import crafting, get_logograph


router = APIRouter(
    prefix="/craft",
    tags=["craft"],
)


@router.post("/")
@RateLimitMiddleware.limit(config["rate_limit"]["craft"])
async def craft(query: Query):
    """
    `material*` should contain the `english_name` of the materials.
    """
    if await query.team_id() is None:
        return {"error": "invalid team token"}

    try:
        result = await db.craft(query)
        if result is not None and len(result) == 2:
            return {"english_name": result[0], "symbol": result[1]}
    except ValueError as e:
        return {"error": str(e)}
    except IndexError as e:
        print(e, result)
        return {"error": str(e)}

    try:
        # TODO: fix race condition
        if config["backend_llm"]["enabled"]:
            api_key = config["backend_llm"]["novita_key"]
            element_english_name = await crafting(query.sorted_materials, api_key)
            if element_english_name is None:
                return {"error": "these elements can't be combined"}
            element_symbol = await db.element_exist(element_english_name)
            if element_symbol is None:
                element_symbol = await get_logograph(element_english_name, api_key)
            data = {
                "english_name": element_english_name,
                "symbol": element_symbol,
            }

        else:
            tmp = "".join(query.sorted_materials)[:10]
            data = {
                "english_name": tmp,
                "symbol": f"元素_{tmp}",
            }

        await db.insert_item(
            data["english_name"], data["symbol"], query.sorted_materials, await query.team_id()
        )
        return data

    except Exception as e:
        return {"error": str(e)}


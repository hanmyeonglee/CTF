from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import db
from .ratelimit import RateLimitMiddleware
from .route.craft import router as craft_router
from .route.bounty import router as bounty_router
from .config import config
from .team import token2team_id


logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init()
    try:
        yield
    finally:
        return


app = FastAPI(lifespan=lifespan)
app.add_middleware(RateLimitMiddleware)
app.include_router(craft_router)
app.include_router(bounty_router)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/")
async def homepage():
    return FileResponse("frontend/index.html")


@app.get("/my_inventory")
@RateLimitMiddleware.limit(config["rate_limit"]["get_inventory"])
async def get_inventory(team_token: str):
    if (team_id := await token2team_id(team_token)) is None:
        return {"error": "invalid team token"}

    return await db.get_inventory(team_id)


@app.get("/current_round")
async def get_current_round() -> int | None:
    return await db.get_current_round()


@app.get("/round_info")
async def get_round_info(round_id: int):
    return await db.get_round_info(round_id)


@app.get("/G1v3_m3_soUr5e_C0dE")
@RateLimitMiddleware.limit(config["rate_limit"]["get_source_code"])
async def get_source_code(team_token: str):
    if (team_id := await token2team_id(team_token)) is None:
        return {"error": "invalid team token"}

    unlocked_elements = [pair[0] for pair in await db.get_inventory(team_id)]
    condition = config["get_source_code_condition"]

    if not all(elem in unlocked_elements for elem in condition):
        return {"success": False, "need": condition}

    source = {}
    for file in Path(__file__).parent.glob("**/*.py"):
        if file.name == "test.py":
            continue
        with open(file) as f:
            source[file.name] = f.read()
    return {"success": True, "source": source}


@app.get("/get_recipe", include_in_schema=False)
@RateLimitMiddleware.limit(config["rate_limit"]["get_recipe"])
async def get_recipe(team_token: str, element: str):
    if (team_id := await token2team_id(team_token)) is None:
        return {"error": "invalid team token"}

    try:
        recipe = await db.get_recipe(team_id, element)
    except Exception as e:
        return {"error": str(e)}

    result = []
    for element in recipe:
        element_id, english_name, *materials = element
        result.append(
            {"id": element_id, "english_name": english_name, "materials": materials}
        )

    return {"success": True, "recipe": result}


# debugging endpoints
if config["debug"]["enable_endpoint"]:

    @app.get("/debug")
    async def debug():
        await db.debug()

    @app.get("/debug_clear_bounty")
    async def debug_clear_bounty():
        await db.debug_clear_bounty()

    @app.get("/debug_clear_round")
    async def debug_clear_round():
        await db.debug_clear_round()

    @app.get("/debug_incr_round")
    async def debug_incr_round():
        prev_round_id = await db.get_current_round()
        await db.insert_round_and_set_prev_round_end()
        from .round import RoundManager

        async with RoundManager() as rm:
            await rm.calculate_round_rank(prev_round_id)

    @app.get("/debug_clear_recipe")
    async def debug_clear_recipe():
        await db.debug_clear_recipe()


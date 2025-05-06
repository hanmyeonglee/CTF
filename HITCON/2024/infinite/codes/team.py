import httpx

from .config import config

scoreboard_base_url = config["scoreboard"]["scoreboard_uri"].rstrip("/")

__token2team_id_cache = None
async def token2team_id(token: str) -> int | None:
    global __token2team_id_cache

    # for local testing
    if not config["scoreboard"]["use_scoreboard_to_auth_team"]:
        if __token2team_id_cache is None:
            __token2team_id_cache = {team['token']: team['team_id'] for team in config['teams']}

        return __token2team_id_cache.get(token)

    # for production
    if __token2team_id_cache is None:
        __token2team_id_cache = {}

    if token in __token2team_id_cache:
        return __token2team_id_cache[token]

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{scoreboard_base_url}/team/my", headers={"Authorization": token})
        if resp.status_code == 200:
            team_id = resp.json()["id"]
            __token2team_id_cache[token] = team_id
            return team_id
        else:
            return None


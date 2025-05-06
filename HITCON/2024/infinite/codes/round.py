import asyncio
from datetime import datetime
import math
import json

from fastapi import FastAPI

from .db import DB
from .config import config


class RoundManager:
    def __init__(self, polling_interval=1):
        self.db = None
        self.polling_interval = polling_interval

    async def __aenter__(self):
        try:
            self.db = DB()
            # await self.db.init()
            return self
        except ConnectionRefusedError as e:
            raise ConnectionRefusedError(
                f"Cannot connect to database (maybe db not ready yet?): {e}"
            )

    async def __aexit__(self, exc_type, exc, tb):
        return

    async def handler_job_KoHInit(self, round_id: int):
        # a round starts when the KoHInit job of next round is received
        # that is, the last round of every day should be end by manually sending an excessive KoHInit job

        prev_round_id = await self.db.get_current_round()

        await self.db.insert_round_and_set_prev_round_end(round_id)

        if prev_round_id is not None:
            await self.calculate_round_rank(prev_round_id)

    async def calculate_round_rank(self, round_id: int):
        bounty = await self.db.get_bounty_for_calculating_score(round_id)
        if bounty is None:
            raise ValueError("bounty is None, maybe the round is not ended yet")

        # calculate every team's score
        score = {team["team_id"]: 0 for team in config["teams"]}
        for team_id in score.keys():
            if team_id not in bounty or bounty[team_id] is None:
                continue

            # calculate score of setting bounty
            _, (set_bounty_length, set_bounty_round_id), other_team = bounty[team_id]
            threshold = config["scoreboard"]["set_bounty_round_threshold"]
            score[team_id] += int(
                min(round_id - set_bounty_round_id, threshold)
                / threshold
                * math.sqrt(set_bounty_length)
            )

            # calculate score of other team submitting the bounty
            for team_id_, length_ in other_team.items():
                score[team_id_] += set_bounty_length - length_

        # generate rank like [{team:1,rank:1},{team:2,rank:2},{team:4,rank:2},{team:5,rank:4}]
        sorted_score = sorted(score.items(), key=lambda x: x[1], reverse=True)
        rank = []
        r, prev_score = 1, math.inf
        for team_id, _ in sorted_score:
            if score[team_id] != prev_score:
                r = len(rank) + 1
                prev_score = score[team_id]
            rank.append({"team": team_id, "rank": r})

        # store rank to db (it will be sent on KoHScore job)
        await self.db.set_rank(round_id, json.dumps(rank))

    async def handler_job_KoHScore(self, round_id: int):
        return await self.db.get_rank(round_id)


app = FastAPI()


@app.get("/kohinit")
async def on_event_kohinit(round_id: int):
    async with RoundManager() as rm:
        await rm.handler_job_KoHInit(round_id)


@app.get("/kohscore")
async def on_event_kohscore(round_id) -> str | None:
    async with RoundManager() as rm:
        # workaround: for testing
        if not await rm.db.check_round_exist(round_id):
            return "workaround: for testing"

        return await rm.handler_job_KoHScore(round_id)


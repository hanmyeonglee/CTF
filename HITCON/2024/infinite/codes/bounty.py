from fastapi import APIRouter

from ..db import db
from ..model import Bounty
from ..config import config
from ..ratelimit import RateLimitMiddleware
from ..team import token2team_id


router = APIRouter(
    prefix='/bounty',
    tags=['bounty'],
)


@router.post('/set')
async def set_bounty(bounty: Bounty):
    try:
        await bounty.validate(config['initial_items'], db.check_recipe)
    except ValueError as e:
        return {'error': str(e)}

    await db.insert_bounty(bounty, is_submitted=False)
    return {'success': True}


@router.post('/clear')
async def clear_bounty(team_token: str):
    if (team_id := await token2team_id(team_token)) is None:
        return {'error': 'invalid team token'}

    await db.clear_bounty(team_id)
    return {'success': True}


@router.post('/submit')
async def submit_bounty(target_team_id: int, bounty: Bounty):
    if await bounty.team_id() == target_team_id:
        return {'error': 'self submission'}

    # check if bounty exists
    if (tmp := await db.get_bounty(target_team_id)) is None:
        return {'error': 'bounty not found'}

    target_product, (length, _), _ = tmp
    if bounty.target_product != target_product:
        return {'error': 'target product mismatch'}
    if bounty.length >= length:
        return {'error': 'useless submission'}

    try:
        await bounty.validate(config['initial_items'], db.check_recipe)
    except ValueError as e:
        return {'error': str(e)}

    await db.insert_bounty(bounty, is_submitted=True)
    return {'success': True}


@router.post('/get')
@RateLimitMiddleware.limit(config['rate_limit']['get_bounty'])
async def get_bounty(target_team_id: int):
    if (bounty := await db.get_bounty(target_team_id)) is None:
        return {'error': 'bounty not found'}

    target_product, (length, uploaded_round_id), submitted = bounty
    return {
        'target_product': target_product,
        'uploaded_round_id': uploaded_round_id,
        'length': length,
        'submitted': submitted,
    }


@router.post('/my_history')
@RateLimitMiddleware.limit(config['rate_limit']['get_my_bounty_history'])
async def get_my_bounty(team_token: str):
    if (team_id := await token2team_id(team_token)) is None:
        return {'error': 'invalid team token'}

    return await db.get_my_bounty_history(team_id)


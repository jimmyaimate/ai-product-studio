from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from api.deps import CreditsDep, SettingsDep

router = APIRouter()


@router.get("")
async def get_credits(settings: SettingsDep) -> dict:
    from core.credits.tracker import CreditTracker
    tracker = CreditTracker(settings)
    return tracker.summary()


class ReloadRequest(BaseModel):
    additional_tokens: int = 10000


@router.post("/reload")
async def reload_credits(req: ReloadRequest, settings: SettingsDep) -> dict:
    from core.credits.tracker import CreditTracker
    tracker = CreditTracker(settings)
    tracker.reset()
    return {"message": f"Credits reset. New budget: {tracker.tokens_remaining} tokens."}

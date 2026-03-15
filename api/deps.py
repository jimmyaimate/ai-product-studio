from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings, get_settings
from core.credits.tracker import CreditTracker
from core.database import get_db_session
from memory.learning_system.learning import LearningSystem
from memory.vector_memory.factory import get_vector_store
from memory.vector_memory.base import VectorStoreBase


def get_credit_tracker(settings: Annotated[Settings, Depends(get_settings)]) -> CreditTracker:
    return CreditTracker(settings)


def get_vector_store_dep(settings: Annotated[Settings, Depends(get_settings)]) -> VectorStoreBase:
    return get_vector_store(settings)


def get_learning_system(settings: Annotated[Settings, Depends(get_settings)]) -> LearningSystem:
    return LearningSystem(settings)


SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
CreditsDep = Annotated[CreditTracker, Depends(get_credit_tracker)]
VectorStoreDep = Annotated[VectorStoreBase, Depends(get_vector_store_dep)]
LearnDep = Annotated[LearningSystem, Depends(get_learning_system)]

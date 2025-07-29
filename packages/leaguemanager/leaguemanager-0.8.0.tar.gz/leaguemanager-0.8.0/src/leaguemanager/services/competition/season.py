from __future__ import annotations

from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Season
from leaguemanager.repository import SeasonSyncRepository
from leaguemanager.repository._async import SeasonAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["SeasonService", "SeasonAsyncService"]


class SeasonService(SQLAlchemySyncRepositoryService):
    """Handles database operations for roles data."""

    repository_type = SeasonSyncRepository


class SeasonAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for roles data."""

    repository_type = SeasonAsyncRepository

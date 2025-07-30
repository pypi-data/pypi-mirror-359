"""Data models for Recallio API requests and responses."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class MemoryWriteRequest:
    """Request body for `/api/Memory/write`."""

    userId: str
    projectId: str
    content: str
    consentFlag: bool
    tags: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryRecallRequest:
    """Request body for `/api/Memory/recall`."""

    projectId: str
    userId: str
    query: str
    scope: str
    tags: Optional[List[str]] = None
    limit: Optional[int] = None
    similarityThreshold: Optional[float] = None
    summarized: Optional[bool] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryDeleteRequest:
    """Request body for `/api/Memory/delete`."""

    scope: str
    userId: Optional[str] = None
    projectId: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemoryDto:
    """Response body for memory objects."""

    id: Optional[str] = None
    userId: Optional[str] = None
    projectId: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    createdAt: Optional[str] = None
    expiresAt: Optional[str] = None


@dataclass
class MemoryWithScoreDto(MemoryDto):
    """Memory object returned from search with similarity information."""

    similarityScore: Optional[float] = None
    similarityLevel: Optional[str] = None


@dataclass
class ErrorReturnClass:
    """Error response returned by the API."""

    error: str

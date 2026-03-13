from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel

from shared.schemas import (
    AdversarialResult,
    ClaimCategory,
    FreshnessStatus,
    VerificationStatus,
)


class Source(BaseModel):
    id: UUID
    title: str
    source_type: str
    url: str
    fetched_at: datetime
    last_checked: Optional[datetime]
    hash: Optional[str]
    metadata: Optional[dict[str, Any]]


class Chunk(BaseModel):
    id: UUID
    source_id: UUID
    content: str
    embedding: Optional[list[float]]
    chunk_index: int
    metadata: Optional[dict[str, Any]]


class Claim(BaseModel):
    id: UUID
    source_url: str
    claim_text: str
    category: Optional[ClaimCategory]
    extracted_at: datetime
    extracted_by: Optional[str]
    fact_check_score: Optional[float]
    adversarial_result: Optional[AdversarialResult]
    consistency_score: Optional[float]
    freshness_status: Optional[FreshnessStatus]
    overall_confidence: Optional[float]
    legal_suggestion: Optional[str]
    draft_suggestion: Optional[str]
    ux_suggestion: Optional[str]
    action_required: Optional[bool]
    metadata: Optional[dict[str, Any]]


class Report(BaseModel):
    id: UUID
    created_at: datetime
    report_type: str
    source_url: str
    total_claims: int
    verified_claims: int
    issues_found: int
    report_data: dict[str, Any]
    status: Optional[VerificationStatus]

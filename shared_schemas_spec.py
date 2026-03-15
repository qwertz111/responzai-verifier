# shared/schemas.py
# ZENTRALE DATENTYPEN - Alle Module importieren von hier.
# Diese Datei wird VOR allen anderen erstellt.
# Jeder Subagent bekommt die für ihn relevanten Schemas als Kontext.

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────

class ClaimCategory(str, Enum):
    LEGAL_CLAIM = "LEGAL_CLAIM"
    PRODUCT_CLAIM = "PRODUCT_CLAIM"
    MARKET_CLAIM = "MARKET_CLAIM"
    TARGET_GROUP = "TARGET_GROUP"


class Verifiability(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNCERTAIN = "uncertain"
    CONTRADICTED = "contradicted"


class AdversarialResult(str, Enum):
    SURVIVED = "survived"
    WEAKENED = "weakened"
    REFUTED = "refuted"


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    OUTDATED = "outdated"
    EXPIRING = "expiring"


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    NONE = "none"


class ChangeType(str, Enum):
    UPDATE = "update"
    CORRECTION = "correction"
    ADDITION = "addition"
    REMOVAL = "removal"


# ─── Simon (SCOUT) ───────────────────────────────────

class Claim(BaseModel):
    id: str
    claim_text: str
    category: ClaimCategory
    verifiability: Verifiability
    original_text: str
    source_url: str
    implicit_assumptions: List[str] = []


class SimonOutput(BaseModel):
    claims: List[Claim]
    summary: dict


# ─── Vera (VERIFY) ───────────────────────────────────

class SupportingPassage(BaseModel):
    chunk_id: int
    text: str
    source: str
    relevance: float


class VeraOutput(BaseModel):
    claim_id: str
    score: float = Field(ge=0.0, le=1.0)
    status: VerificationStatus
    reasoning: str
    supporting_passages: List[SupportingPassage]
    gaps: List[str] = []


# ─── Conrad (CONTRA) ─────────────────────────────────

class StrategyFinding(BaseModel):
    strategy: str
    finding: str
    evidence: str
    severity: Severity


class ConradOutput(BaseModel):
    claim_id: str
    result: AdversarialResult
    strategies_applied: List[StrategyFinding]
    overall_assessment: str
    suggested_refinement: Optional[str] = None


# ─── Sven (SYNC) ─────────────────────────────────────

class Contradiction(BaseModel):
    claim_a_id: str
    claim_b_id: str
    type: str  # INTERN, KANALÜBERGREIFEND, SEMANTISCH, IMPLIZIT
    severity: Severity
    description: str
    source_a: str
    source_b: str
    suggested_resolution: Optional[str] = None


class Duplicate(BaseModel):
    claims: List[str]
    similarity: float
    note: str


class SvenOutput(BaseModel):
    contradictions: List[Contradiction]
    duplicates: List[Duplicate]
    consistency_score: float = Field(ge=0.0, le=1.0)


# ─── Pia (PULSE) ─────────────────────────────────────

class PiaOutput(BaseModel):
    claim_id: str
    time_references: List[str]
    freshness: FreshnessStatus
    source_last_updated: Optional[str] = None
    latest_version_available: Optional[str] = None
    days_since_update: Optional[int] = None
    upcoming_deadlines: List[str] = []
    update_suggestion: Optional[str] = None


# ─── Lena (LEGAL) ────────────────────────────────────

class SourceReference(BaseModel):
    hash: str
    source: str
    passage: str


class LenaOutput(BaseModel):
    claim_id: str
    change_type: ChangeType
    current_text: str
    suggested_text: str
    sources_used: List[SourceReference]
    coverage: float = Field(ge=0.0, le=1.0)
    gaps: List[str] = []
    reasoning: str


# ─── Davina (DRAFT) ──────────────────────────────────

class TextChange(BaseModel):
    current_text: str
    suggested_text: str
    reason: str
    category: str  # readability, nominalstil, passive, fachsprache


class DavinaOutput(BaseModel):
    changes: List[TextChange]
    readability_score_before: int
    readability_score_after: int
    summary: str


# ─── Uma (UX) ────────────────────────────────────────

class UxIssue(BaseModel):
    section: str
    criterion: str  # ORIENTIERUNG, REIHENFOLGE, AUSFÜLLHILFEN, GRUPPIERUNG, ZUSTÄNDIGKEIT, VOLLSTÄNDIGKEIT, ÜBERFORDERUNG
    severity: str  # gut, verbesserungswürdig, problematisch, kritisch
    issue: str
    suggestion: str
    effort: str  # niedrig, mittel, hoch


class UmaOutput(BaseModel):
    overall_usability: str
    issues: List[UxIssue]
    quick_wins: List[str]
    priority_order: List[str]


# ─── Document Ingestion ──────────────────────────────

class DocumentSection(BaseModel):
    heading: str = ""
    text: str
    level: Optional[int] = None


class DocumentMetadata(BaseModel):
    file_size_bytes: int = 0
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None


class IngestedDocument(BaseModel):
    filename: str
    format: str
    pages: int = 1
    text: str
    sections: List[DocumentSection] = []
    metadata: DocumentMetadata = DocumentMetadata()
    raw_length: int = 0
    cleaned_length: int = 0
    ocr_used: bool = False
    ocr_confidence: Optional[float] = None


# ─── Pipeline State ──────────────────────────────────

class PipelineInput(BaseModel):
    source_url: str = ""
    source_text: str = ""
    source_document: Optional[IngestedDocument] = None


class VerificationReport(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    source_url: str
    total_claims: int
    verified_claims: int
    issues_found: int
    report_data: dict


class ImprovementReport(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    legal_updates: int
    text_improvements: int
    ux_issues: int
    changes: List[dict]

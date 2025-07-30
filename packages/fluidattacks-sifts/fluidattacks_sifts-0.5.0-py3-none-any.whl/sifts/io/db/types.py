from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import Literal

from pydantic import BaseModel, Field


class SnippetFacet(BaseModel):
    group_name: str = Field(..., min_length=1)
    root_id: str = Field(..., min_length=1)
    file_path: str = Field(..., min_length=1)
    snippet_hash: str = Field(..., min_length=1)
    line_start: int = Field(..., ge=0)
    line_end: int = Field(..., ge=0)
    column_start: int = Field(..., ge=0)
    column_end: int = Field(..., ge=0)
    snippet_content: str = Field(..., min_length=1)
    hash_type: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)
    last_seen_at: str = Field(..., min_length=1)
    byte_start: int = Field(..., ge=0)
    byte_end: int = Field(..., ge=0)
    name: str | None = Field(None, min_length=1)


class _BaseFacet(BaseModel):
    group_name: str
    root_id: str
    version: str
    commit: str
    snippet_hash: str
    analyzed_at: datetime
    file_path: str
    path: str
    cost: float

    candidate_index: int | None = None
    trace_id: str | None = None


class VulnerableFacet(_BaseFacet):
    vulnerable: Literal[True] = True

    vulnerability_id_candidates: list[str]
    vulnerable_lines: list[int]
    ranking_score: float
    reason: str
    input_tokens: int
    output_tokens: int
    total_tokens: int

    suggested_criteria_code: str | None = None
    suggested_finding_title: str | None = None


class SafeFacet(_BaseFacet):
    vulnerable: Literal[False] = False
    input_tokens: int
    output_tokens: int
    total_tokens: int
    reason: str
    vulnerability_id_candidates: list[str]

    vulnerable_lines: list[int] | None = None
    ranking_score: float | None = None
    suggested_criteria_code: str | None = None
    suggested_finding_title: str | None = None


AnalysisFacet = VulnerableFacet | SafeFacet

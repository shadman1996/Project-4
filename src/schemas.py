"""
Project 4 — Pydantic schemas for agent outputs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Search Agent outputs ---

class SearchFinding(BaseModel):
    """A single search finding from a research query."""
    title: str = Field(description="Title or headline of the finding")
    source: str = Field(description="Source URL or reference")
    summary: str = Field(description="Brief summary of the finding (2-3 sentences)")
    relevance_score: float = Field(description="Relevance score 0.0-1.0", ge=0, le=1)


class SearchResult(BaseModel):
    """Complete output from a Search Agent."""
    agent_name: str = Field(description="Name of the search agent that produced this")
    query_used: str = Field(description="The actual search query executed")
    findings: list[SearchFinding] = Field(description="List of search findings")
    search_metadata: str = Field(description="Notes about the search process")


# --- Verification Agent output ---

class VerifiedFinding(BaseModel):
    """A finding after verification."""
    original_title: str
    verified: bool = Field(description="Whether this finding was verified as accurate")
    confidence: float = Field(description="Confidence score 0.0-1.0", ge=0, le=1)
    verification_notes: str = Field(description="How/why this was verified or flagged")
    cross_references: list[str] = Field(description="Other sources that confirm/deny this", default_factory=list)


class VerificationResult(BaseModel):
    """Complete output from the Verification Agent."""
    total_findings: int
    verified_count: int
    rejected_count: int
    findings: list[VerifiedFinding]
    overall_assessment: str


# --- Ranking Agent output ---

class RankedFinding(BaseModel):
    """A verified finding with a final rank."""
    rank: int
    title: str
    relevance: float = Field(description="Final relevance score after ranking", ge=0, le=1)
    credibility: float = Field(description="Source credibility score", ge=0, le=1)
    recency_score: float = Field(description="How recent/current the info is", ge=0, le=1)
    composite_score: float = Field(description="Weighted composite of all scores", ge=0, le=1)
    summary: str


class RankedResults(BaseModel):
    """Complete output from the Ranking Agent."""
    total_ranked: int
    top_findings: list[RankedFinding]
    ranking_methodology: str


# --- Synthesis Agent output ---

class SynthesisReport(BaseModel):
    """Final synthesized research report."""
    title: str = Field(description="Report title")
    executive_summary: str = Field(description="2-3 paragraph executive summary")
    key_findings: list[str] = Field(description="Bullet-point key findings")
    detailed_analysis: str = Field(description="Detailed analysis section")
    recommendations: list[str] = Field(description="Actionable recommendations")
    limitations: str = Field(description="Limitations of the research")
    references: list[str] = Field(description="Sources used")


# --- Data Agent output ---

class DataResult(BaseModel):
    """Output from a Data Agent file operation."""
    operation: str = Field(description="What operation was performed (read/write/list)")
    success: bool
    file_path: str = Field(description="Path of the file operated on", default="")
    content: str = Field(description="File content or operation result", default="")
    error: str = Field(description="Error message if failed", default="")


# --- Coordinator output ---

class AgentTask(BaseModel):
    """A task assignment from the Coordinator to a specialist agent."""
    target_agent: str = Field(description="Which agent to dispatch to: Search-A, Search-B, Verification, Ranking, Synthesis, Data")
    task_description: str = Field(description="Detailed task description for the agent")
    priority: int = Field(description="Priority 1(highest) to 5(lowest)", ge=1, le=5)


class CoordinatorPlan(BaseModel):
    """The Coordinator's plan for handling a user query."""
    understanding: str = Field(description="Coordinator's understanding of the user's request")
    strategy: str = Field(description="High-level strategy for answering")
    tasks: list[AgentTask] = Field(description="Ordered list of agent tasks to execute")
    estimated_steps: int = Field(description="Estimated number of pipeline steps")

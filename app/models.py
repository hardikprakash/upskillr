"""
Pydantic models for structured LLM responses.
These ensure type safety and automatic validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ResumeData(BaseModel):
    """
    Structured data extracted from a resume.
    """
    name: Optional[str] = Field(
        None,
        description="Full name of the individual"
    )
    job_role: Optional[str] = Field(
        None,
        description="Most recent or primary job title"
    )
    education: List[str] = Field(
        default_factory=list,
        description="List of education entries with degree, institution, location, and years"
    )
    experience: List[str] = Field(
        default_factory=list,
        description="List of professional or academic experiences with role, organization, time period, and responsibilities"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of technical and soft skills"
    )


class SkillRecommendations(BaseModel):
    """
    Recommended skills for career development.
    """
    recommended_skills: List[str] = Field(
        default_factory=list,
        description="List of skills the user should learn to become a stronger candidate (max 9 skills)"
    )

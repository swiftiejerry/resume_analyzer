from pydantic import BaseModel
from typing import Optional, List

# Basic Info Model
class BasicInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

# Full Extract Result
class ResumeData(BaseModel):
    basic_info: BasicInfo
    job_intention: Optional[str] = None
    work_years: Optional[str] = None
    education_background: Optional[str] = None
    raw_text_summary: Optional[str] = None # Or extracted key skills

class ResumeAnalyzeResponse(BaseModel):
    resume_id: str
    data: ResumeData
    message: str = "Success"

class JobDescriptionRequest(BaseModel):
    resume_id: str
    job_description: str

class MatchResult(BaseModel):
    score: int # 0-100
    skills_match_rate: str
    experience_relevance: str
    comment: str

class ResumeMatchResponse(BaseModel):
    resume_id: str
    match_result: MatchResult
    message: str = "Success"

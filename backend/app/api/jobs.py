from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/jobs")


class JobCreate(BaseModel):
    type: str
    payload: dict = Field(default_factory=dict)


@router.post("")
def create_job(_: JobCreate):
    raise HTTPException(status_code=501, detail="job execution wired post-M0 (ADR-0009)")


@router.get("/{job_id}")
def get_job(job_id: str):
    raise HTTPException(status_code=501, detail="job execution wired post-M0 (ADR-0009)")

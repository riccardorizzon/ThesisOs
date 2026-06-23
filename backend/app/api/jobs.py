from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/jobs")


class JobCreate(BaseModel):
    type: str
    payload: dict = {}


@router.post("", status_code=501)
def create_job(_: JobCreate):
    raise HTTPException(status_code=501, detail="job execution wired post-M0 (ADR-0009)")


@router.get("/{job_id}", status_code=501)
def get_job(job_id: str):
    raise HTTPException(status_code=501, detail="job execution wired post-M0 (ADR-0009)")

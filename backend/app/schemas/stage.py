from pydantic import BaseModel


class StageResponse(BaseModel):
    stage_id: int
    title: str
    cleared: bool
    locked: bool = False

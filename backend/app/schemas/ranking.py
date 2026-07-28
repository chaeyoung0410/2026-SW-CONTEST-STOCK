from pydantic import BaseModel


class RankingResponse(BaseModel):
    rank: int
    nickname: str
    score: int
    cleared_stage_count: int

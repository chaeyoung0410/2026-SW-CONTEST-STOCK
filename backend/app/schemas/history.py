from pydantic import BaseModel


class HistoryResponse(BaseModel):
    stage: str
    score: int
    accuracy: float

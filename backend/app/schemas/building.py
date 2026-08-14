from pydantic import BaseModel


class BuildingResponse(BaseModel):
    level: int
    image: str
    progress: int
    next_features: list[str]
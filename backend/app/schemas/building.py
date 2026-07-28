from pydantic import BaseModel


class BuildingResponse(BaseModel):
    level: int
    image: str

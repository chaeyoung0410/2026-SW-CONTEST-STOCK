from pydantic import BaseModel


class LearningPageResponse(BaseModel):
    learning_id: int
    title: str
    content: str
    image: str | None
    page_order: int


class LearningResponse(BaseModel):
    stage_id: int
    title: str
    content: str
    pages: list[LearningPageResponse]

from pydantic import BaseModel


class NewsItemResponse(BaseModel):
    title: str
    link: str
    published: str
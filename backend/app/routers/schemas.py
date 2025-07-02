from pydantic import BaseModel
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    link: str
    originallink: str | None = None
    description: str | None = None
    pub_date: datetime

class NewsCreate(NewsBase):
    pass

class NewsRead(NewsBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
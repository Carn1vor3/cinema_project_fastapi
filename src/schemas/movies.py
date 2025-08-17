from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class MovieBaseSchema(BaseModel):
    uuid: UUID
    name: str = Field(max_length=250)
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: Optional[Decimal]
    certification_id: int


class MovieListSchema(MovieBaseSchema):
    id: int
    stars_ids: List[int] = Field(default_factory=list)
    genres_ids: List[int] = Field(default_factory=list)
    directors_ids: List[int] = Field(default_factory=list)

    class Config:
        orm_mode = True

from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class CertificateSchema(BaseModel):
    id: int
    name: str


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


class MovieListSchema(BaseModel):
    id: int
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

    stars_ids: List[int] = Field(default_factory=list)
    genres_ids: List[int] = Field(default_factory=list)
    directors_ids: List[int] = Field(default_factory=list)

    class Config:
        orm_mode = True



class MovieCreateSchema(BaseModel):
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
    stars_ids: Optional[List[int]] = Field(default_factory=list)
    genres_ids: Optional[List[int]] = Field(default_factory=list)
    directors_ids: Optional[List[int]] = Field(default_factory=list)

    class Config:
        orm_mode = True

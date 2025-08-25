from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, conint


class GenresBaseSchema(BaseModel):
    name: str


class GenresListSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GenresWithCountSchema(BaseModel):
    id: int
    name: str
    movies_count: int


class GenresCreateSchema(GenresBaseSchema):
    pass


class GenresUpdateSchema(GenresBaseSchema):
    pass


class StarsBaseSchema(BaseModel):
    name: str


class StarsListSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class StarsCreateSchema(StarsBaseSchema):
    pass


class StarsUpdateSchema(StarsBaseSchema):
    pass


class DirectorsListSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


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
    stars_ids: Optional[List[int]] = Field(default_factory=list)
    genres_ids: Optional[List[int]] = Field(default_factory=list)
    directors_ids: Optional[List[int]] = Field(default_factory=list)


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

    stars: List[StarsListSchema] = Field(default_factory=list)
    genres: List[GenresListSchema] = Field(default_factory=list)
    directors: List[DirectorsListSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class MovieCreateSchema(MovieBaseSchema):
    pass

    class Config:
        from_attributes = True


class MovieUpdateSchema(BaseModel):
    uuid: Optional[UUID] = None
    name: Optional[str] = Field(None, max_length=250)
    year: Optional[int] = None
    time: Optional[int] = None
    imdb: Optional[float] = None
    votes: Optional[int] = None
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    certification_id: Optional[int] = None

    stars_ids: Optional[List[int]] = None
    genres_ids: Optional[List[int]] = None
    directors_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True


class MovieInGenreSchema(BaseModel):
    id: int
    name: str
    year: int

    class Config:
        from_attributes = True


class GenresDetailSchema(BaseModel):
    id: int
    name: str
    movies: List[MovieInGenreSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class MovieLikeCreate(BaseModel):
    movie_id: int


class MovieCommentCreate(BaseModel):
    movie_id: int
    content: str


class MovieCommentOut(BaseModel):
    id: int
    user_id: int
    movie_id: int
    content: str

    class Config:
        from_attributes = True


class MovieRatingCreate(BaseModel):
    rating: conint(ge=1, le=10)

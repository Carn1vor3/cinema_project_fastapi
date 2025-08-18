import decimal
from uuid import UUID

from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


movies_stars = Table(
    "movies_stars",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("star_id", ForeignKey("stars.id"), primary_key=True),
)

movies_genres = Table(
    "movies_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)

movies_directors = Table(
    "movies_directors",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("director_id", ForeignKey("directors.id"), primary_key=True),
)


class Movies(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    time: Mapped[int] = mapped_column(nullable=False)
    imdb: Mapped[float] = mapped_column(nullable=False)
    votes: Mapped[int] = mapped_column(nullable=False)
    meta_score: Mapped[float] = mapped_column(nullable=True)
    gross: Mapped[float] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(nullable=True)
    certification_id: Mapped[int] = mapped_column(
        ForeignKey("certifications.id"), nullable=False
    )
    certification: Mapped["Certifications"] = relationship(back_populates="movies")

    stars: Mapped[list["Stars"]] = relationship(
        secondary=movies_stars, back_populates="movies"
    )
    genres: Mapped[list["Genres"]] = relationship(
        secondary=movies_genres, back_populates="movies"
    )
    directors: Mapped[list["Directors"]] = relationship(
        secondary=movies_directors, back_populates="movies"
    )


class Certifications(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    movies: Mapped[list["Movies"]] = relationship(back_populates="certification")


class Stars(Base):
    __tablename__ = "stars"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    movies: Mapped[list["Movies"]] = relationship(
        secondary=movies_stars, back_populates="stars"
    )


class Genres(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    movies: Mapped[list["Movies"]] = relationship(
        secondary=movies_genres, back_populates="genres"
    )


class Directors(Base):
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    movies: Mapped[list["Movies"]] = relationship(
        secondary=movies_directors, back_populates="directors"
    )

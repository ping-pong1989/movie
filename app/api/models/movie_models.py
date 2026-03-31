from pydantic import BaseModel, Field
from typing import Optional


class MovieResponse(BaseModel):
    """Public-facing movie model returned by the API."""
    title: str = Field(..., description="Movie title")
    rating: Optional[float] = Field(None, description="Average user rating (0–10)")
    release_date: Optional[str] = Field(None, description="Release date (YYYY-MM-DD)")
    overview: Optional[str] = Field(None, description="Short plot summary")
    popularity: Optional[float] = Field(None, description="TMDB popularity score")
    poster_url: Optional[str] = Field(None, description="URL to poster image")

    model_config = {"json_schema_extra": {
        "example": {
            "title": "Tenet",
            "rating": 7.3,
            "release_date": "2020-08-22",
            "overview": "Armed with only one word, Tenet, and fighting for the survival of the entire world...",
            "popularity": 98.5,
            "poster_url": "https://image.tmdb.org/t/p/w500/k68nPLbIST6NP96JmTxmZijWarw.jpg",
        }
    }}


class TopMoviesResponse(BaseModel):
    """Wrapper response for top-movies endpoint."""
    year: int
    count: int
    movies: list[MovieResponse]

from fastapi import APIRouter, Query, HTTPException
from app.api.models.movie_models import TopMoviesResponse
from app.services.movie_service import MovieService

router = APIRouter()
_service = MovieService()


@router.get(
    "/top",
    response_model=TopMoviesResponse,
    summary="Get top 5 movies by year",
    description="Returns the top 5 most popular movies for the given year, sorted by popularity.",
)
async def get_top_movies(
    year: int = Query(..., ge=1888, description="The release year to query (e.g. 2020)")
):
    """
    Fetch and return the top 5 most popular movies for a given year.

    - **year**: Four-digit year (must not be in the future, minimum 1888)
    """
    try:
        movies = await _service.get_top_movies(year)
        return TopMoviesResponse(year=year, count=len(movies), movies=movies)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

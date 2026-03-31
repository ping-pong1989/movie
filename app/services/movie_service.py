from datetime import date
from app.clients.movie_client import MovieClient
from app.repositories.movie_repository import MovieRepository
from app.api.models.movie_models import MovieResponse

TOP_N = 5


class MovieService:
    """
    Business logic layer.

    Responsibilities:
    - Validate the requested year
    - Delegate data fetching to MovieClient (via cache-aware MovieRepository)
    - Sort by popularity and return the top N results
    """

    def __init__(self):
        self._client = MovieClient()
        self._repo = MovieRepository()

    async def get_top_movies(self, year: int) -> list[MovieResponse]:
        """Return the top 5 most popular movies for *year*."""
        self._validate_year(year)

        # 1. Check the cache first
        cached = self._repo.get(year)
        if cached:
            return cached

        # 2. Fetch from external API
        raw_movies = await self._client.fetch_movies_by_year(year)

        if not raw_movies:
            return []

        # 3. Sort by popularity (descending) and slice top N
        sorted_movies = sorted(raw_movies, key=lambda m: m.popularity or 0, reverse=True)
        top_movies = sorted_movies[:TOP_N]

        # 4. Persist in cache
        self._repo.set(year, top_movies)

        return top_movies

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_year(year: int) -> None:
        current_year = date.today().year
        if year > current_year:
            raise ValueError(
                f"Year {year} is in the future. Please provide a year up to {current_year}."
            )
        if year < 1888:
            raise ValueError("Year must be 1888 or later (first film was made in 1888).")

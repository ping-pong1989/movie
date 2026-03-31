import os
import httpx
from app.api.models.movie_models import MovieResponse
import requests
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
_PAGE_LIMIT = 3  # Fetch up to 3 pages (~60 movies) to ensure a good Top-5


class MovieClient:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise EnvironmentError("TMDB_API_KEY not set in .env")
        self.base_url = "https://api.themoviedb.org/3"

    def get_popular_movies(self, year: int):
        """
        Returns a list of movie titles for the given year, sorted by popularity.
        """
        url = f"{self.base_url}/discover/movie"
        params = {
            "api_key": self.api_key,
            "sort_by": "popularity.desc",
            "primary_release_year": year,
            "language": "en-US",
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"TMDB API error: {response.status_code} {response.text}")

        data = response.json()
        return [movie["title"] for movie in data.get("results", [])]

    async def fetch_movies_by_year(self, year: int) -> list[MovieResponse]:
        """
        Fetch all discover/movie results for *year* (up to _PAGE_LIMIT pages)
        and return a flat list of MovieResponse objects.
        """
        movies: list[MovieResponse] = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for page in range(1, _PAGE_LIMIT + 1):
                data = await self._fetch_page(client, year, page)
                results = data.get("results", [])
                if not results:
                    break
                movies.extend(self._parse_results(results))

                # Stop early if we've consumed all pages
                if page >= data.get("total_pages", 1):
                    break

        return movies

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _fetch_page(self, client: httpx.AsyncClient, year: int, page: int) -> dict:
        params = {
            "api_key": self._api_key,
            "primary_release_year": year,
            "sort_by": "popularity.desc",
            "page": page,
        }
        try:
            response = await client.get(f"{TMDB_BASE_URL}/discover/movie", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"TMDB returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Network error while contacting TMDB: {exc}") from exc

    @staticmethod
    def _parse_results(results: list[dict]) -> list[MovieResponse]:
        movies = []
        for item in results:
            poster_path = item.get("poster_path")
            movies.append(
                MovieResponse(
                    title=item.get("title", "Unknown"),
                    rating=item.get("vote_average"),
                    release_date=item.get("release_date"),
                    overview=item.get("overview"),
                    popularity=item.get("popularity"),
                    poster_url=f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None,
                )
            )
        return movies

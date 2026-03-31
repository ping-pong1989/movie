from datetime import datetime, timedelta
from app.api.models.movie_models import MovieResponse

_DEFAULT_TTL_HOURS = 24


class _CacheEntry:
    def __init__(self, data: list[MovieResponse], ttl_hours: int = _DEFAULT_TTL_HOURS):
        self.data = data
        self.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

    @property
    def is_valid(self) -> bool:
        return datetime.utcnow() < self.expires_at


class MovieRepository:
    """
    Repository layer: in-memory cache to reduce repeated TMDB API calls.

    Responsibilities:
    - Store top-movie results keyed by year
    - Return cached results if still fresh (within TTL)
    - Expose a simple get / set / invalidate interface

    In production this could be swapped out for a Redis or database-backed
    repository without touching any other layer.
    """

    def __init__(self, ttl_hours: int = _DEFAULT_TTL_HOURS):
        self._store: dict[int, _CacheEntry] = {}
        self._ttl_hours = ttl_hours

    def get(self, year: int) -> list[MovieResponse] | None:
        """Return cached movies for *year*, or None if absent / expired."""
        entry = self._store.get(year)
        if entry and entry.is_valid:
            return entry.data
        if entry:
            # Evict stale entry
            del self._store[year]
        return None

    def set(self, year: int, movies: list[MovieResponse]) -> None:
        """Store movies for *year* with the configured TTL."""
        self._store[year] = _CacheEntry(movies, self._ttl_hours)

    def invalidate(self, year: int) -> None:
        """Remove the cache entry for *year* (if present)."""
        self._store.pop(year, None)

    def clear(self) -> None:
        """Flush the entire cache."""
        self._store.clear()

    @property
    def cached_years(self) -> list[int]:
        """Return all years currently held in the cache."""
        return [y for y, e in self._store.items() if e.is_valid]

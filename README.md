#  Movie Explorer API

A clean, modular REST API that returns the **top 5 most popular movies** for any given year, powered by [TMDB](https://www.themoviedb.org/).

---

## Architecture

```
app/
├── api/
│   ├── routers/movies_router.py   ← HTTP routes & input validation
│   └── models/movie_models.py     ← Pydantic response models
├── services/movie_service.py      ← Business logic & year validation
├── clients/movie_client.py        ← TMDB API communication
└── repositories/movie_repository.py ← In-memory caching (TTL: 24h)
main.py                            ← FastAPI app + CORS
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd movie-explorer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set your TMDB_API_KEY
```

Get a free API key at <https://www.themoviedb.org/settings/api>.

### 3. Run the server

```bash
uvicorn main:app --reload
```

The API is now live at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## Usage

### GET `/movies/top?year=<year>`

Returns the top 5 most popular movies for the given year.

**Example request:**

```
GET http://localhost:8000/movies/top?year=2020
```

**Example response:**

```json
{
  "year": 2020,
  "count": 5,
  "movies": [
    {
      "title": "Tenet",
      "rating": 7.3,
      "release_date": "2020-08-22",
      "overview": "Armed with only one word...",
      "popularity": 98.5,
      "poster_url": "https://image.tmdb.org/t/p/w500/k68nPL..."
    }
  ]
}
```

### Error responses

| Status | Cause |
|--------|-------|
| `400`  | Year is in the future or before 1888 |
| `502`  | TMDB API unreachable or returned an error |

---

## Optional enhancements (ideas)

- **Redis cache** — swap `MovieRepository` for a Redis-backed one
- **Genre filter** — add `?genre=action` query param in the router
- **Pagination** — expose `?page=` and `?per_page=` params
- **Async batch requests** — fetch multiple TMDB pages concurrently with `asyncio.gather`

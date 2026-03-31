from dotenv import load_dotenv
load_dotenv()  # This loads the .env file



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.movies_router import router as movies_router

app = FastAPI(
    title="🎬 Movie Explorer API",
    description="Retrieve the top 5 most popular movies for any given year.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router, prefix="/movies", tags=["Movies"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Movie Explorer API is running 🎬"}


from fastapi import HTTPException
from app.clients.movie_client import MovieClient  # your TMDB client

# Initialize TMDB client (reads TMDB_API_KEY from .env)
client = MovieClient()

@app.get("/test-movies/{year}", tags=["Movies"])
def test_movies(year: int):
    """
    Returns top 5 most popular movies for a given year.
    """
    try:
        print("Fetching movies for year:", year)
        movies = client.get_popular_movies(year)
        print("Movies fetched:", movies)
        return {"year": year, "top_5_movies": movies[:5]}
    except Exception as e:
        print("ERROR:", e)  # <-- This will show the real error in terminal
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pathlib import Path
from typing import List

import sqlite3
import bcrypt
import requests

#connecting to DB
# Use absolute path based on backend directory
DB_PATH = Path(__file__).parent.parent / "RotNRecsDB.db"
conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
# Enable foreign key constraints
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

#API key for TMDB
TMDB_API_KEY = "3a5fa2cd5ed10cc42ae78b74ff0ad926"

# Create Users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# Create Movies table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS Movies (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_title TEXT NOT NULL,
    tmdb_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
""")
conn.commit()

# Pydantic models for request/response
class MovieRequest(BaseModel):
    user_id: int
    movies: List[str]

# Create FastAPI app instance
app = FastAPI()

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")


# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
def read_index():
    index_path = FRONTEND_DIR / "index.html"
    with open(index_path, "r") as f:
        html_content = f.read()
    return html_content

#reads login html when user enters page.
@app.get("/login", response_class=HTMLResponse)
def read_login():
    login_path = FRONTEND_DIR / "login.html"
    with open(login_path, "r") as f:
        return f.read()
    
@app.post("/login")
def check_acct(
    email: EmailStr = Form(...),
    password: str = Form(...)):
    cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=400, detail="User does not exist")

    stored_hash = row[3]  # hashed password from DB

    #checks if passwords are correct
    if not bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash.encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    user_id = row[0]  # Get user_id from the first column
    return {"message": "Login successful", "user_id": user_id}
        

#reads register html when user enter page.
@app.get("/register", response_class=HTMLResponse)
def read_register():
    register_path = FRONTEND_DIR / "register.html"
    with open(register_path, "r") as f:
        return f.read()

#adds user info to the DB when user submits form.
@app.post("/register")
#Form is required to convert html data to JSON 
def creat_acct(name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...)):

    #checks if email exists already
    cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    #hashes pass in db to hide user info.
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor.execute(
        "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed_password) 
    )
    conn.commit()
    
    # Get the user_id of the newly created user
    user_id = cursor.lastrowid

    return {"message": f"successfully created User: {name}", "user_id": user_id}

#retrieves dashboard html when user enters page.
@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    dashboard_path = FRONTEND_DIR / "dashboard.html"
    with open(dashboard_path, "r") as f:
        return f.read()

#retrieves recommendations html when user enters page.
@app.get("/recommendations", response_class=HTMLResponse)
def read_recommendations():
    recommendations_path = FRONTEND_DIR / "recommendations.html"
    with open(recommendations_path, "r") as f:
        return f.read()

# Search TMDB for movies
@app.get("/api/search-movies")
def search_movies(query: str):

    #Searches for movies using TMDB API
    
    if not query or len(query) < 2:
        return {"results": []}
    
    try:
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "language": "en-US",
            "page": 1
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Format results to include only what we need
        results = []
        for movie in data.get("results", [])[:10]:  # Limit to 10 results
            results.append({
                "id": movie.get("id"),
                "title": movie.get("title"),
                "release_date": movie.get("release_date", ""),
                "overview": movie.get("overview", ""),
                "poster_path": movie.get("poster_path")
            })
        
        return {"results": results}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error searching TMDB: {str(e)}")

# Save movies to database
@app.post("/api/save-movies")
def save_movies(movie_request: MovieRequest):
    """
    Save user's favorite movies to the database
    """
    user_id = movie_request.user_id
    movies = movie_request.movies
    
    # Verify user exists
    cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
    user_check = cursor.fetchone()
    if not user_check:
        raise HTTPException(status_code=404, detail=f"User not found with user_id: {user_id}")
    
    saved_count = 0
    errors = []
    
    for movie_title in movies:
        if not movie_title or not movie_title.strip():
            continue
        
        movie_title_clean = movie_title.strip()
        
        # Try to get TMDB ID for the movie
        tmdb_id = None
        try:
            url = f"https://api.themoviedb.org/3/search/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "query": movie_title_clean,
                "language": "en-US",
                "page": 1
            }
            response = requests.get(url, params=params, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    tmdb_id = data["results"][0].get("id")
        except Exception as e:
            print(f"TMDB search error for '{movie_title_clean}': {e}")
            # Continue without TMDB ID if search fails
        
        # Insert movie into database
        try:
            cursor.execute(
                "INSERT INTO Movies (user_id, movie_title, tmdb_id) VALUES (?, ?, ?)",
                (user_id, movie_title_clean, tmdb_id)
            )
            saved_count += 1
            print(f"Successfully saved movie: '{movie_title_clean}' for user_id: {user_id}")
        except sqlite3.IntegrityError as e:
            # Movie might already exist for this user, skip it
            error_msg = f"IntegrityError for movie '{movie_title_clean}': {e}"
            print(error_msg)
            errors.append(error_msg)
        except Exception as e:
            # Log any other errors
            error_msg = f"Error saving movie '{movie_title_clean}': {e}"
            print(error_msg)
            errors.append(error_msg)
    
    conn.commit()
    
    if saved_count == 0 and errors:
        raise HTTPException(status_code=400, detail=f"Failed to save any movies. Errors: {'; '.join(errors)}")
    
    return {
        "message": f"Successfully saved {saved_count} movie(s)", 
        "saved_count": saved_count,
        "errors": errors if errors else None
    }


# Run the server with: uvicorn backend.backend:app --reload
# Or from the project root: python -m uvicorn backend.backend:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
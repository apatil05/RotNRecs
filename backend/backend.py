from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pathlib import Path

import sqlite3
import bcrypt
import requests

#connecting to DB
# Use absolute path based on backend directory
DB_PATH = Path(__file__).parent.parent / "RotNRecsDB.db"
conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
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
conn.commit()

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
    
    return {"message": "Login successful"}
        

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

    return {"message": f"successfully created User: {name}"}

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


# Run the server with: uvicorn backend.backend:app --reload
# Or from the project root: python -m uvicorn backend.backend:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
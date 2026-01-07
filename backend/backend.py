from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from pydantic import BaseModel, EmailStr
from pathlib import Path

import sqlite3
import bcrypt

#connecting to DB

conn = sqlite3.connect("RotNRecsDB.db", check_same_thread=False)
cursor = conn.cursor()


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

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")


# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
def read_index():
    index_path = FRONTEND_DIR / "index.html"
    with open(index_path, "r") as f:
        html_content = f.read()
    return html_content


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

    print(name, email, password)  # 👈 DEBUG

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
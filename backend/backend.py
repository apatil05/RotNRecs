from fastapi import FastAPI

# Create FastAPI app instance
app = FastAPI()

# Define a simple GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}


#adds user info to the DB.
@app.post("/register")
def creat_acct():
    #need to add post code here:

    return {"message": "successfully created user!"}
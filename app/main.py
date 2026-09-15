from fastapi import FastAPI

app = FastAPI(title = "AI Knowledge Platform" , version = "1.0.0")

@app.get("/")
def root():
     return {
        "message": "AI Knowledge Platform API is running"
    }
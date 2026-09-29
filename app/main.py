from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# Create all database tables on startup (if they don't exist yet)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple Bank API", version="1.0.0")

# Allow requests from React dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Health check endpoint — confirms the API is running."""
    return {"status": "ok"}

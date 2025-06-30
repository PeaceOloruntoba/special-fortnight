# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth # Your auth router
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables early

app = FastAPI()

# --- CORS CONFIGURATION (MUST BE HERE, BEFORE app.include_router) ---
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    # Ensure this matches your frontend's exact origin, including port
    "http://localhost:5173", # Explicitly add for clarity/redundancy in local dev
    "http://127.0.0.1:5173", # Sometimes frontend runs on 127.0.0.1
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Crucial for OPTIONS preflight
    allow_headers=["*"],
)
# --- END CORS CONFIGURATION ---

# Include your API routers AFTER CORS middleware
app.include_router(auth.router, prefix="/auth")

# Add a root endpoint for easy testing
@app.get("/")
async def read_root():
    return {"message": "Welcome to CampusPay API - Root"}

# Add a dummy OPTIONS endpoint for testing, though CORSMiddleware should handle it
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    # This is a fallback/test. The middleware should handle it first.
    return {"message": "OPTIONS handled (by fallback, if middleware fails)"}
 
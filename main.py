from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.config import settings
from api.resume import router as resume_router
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI Resume Analyzer",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api/resume", tags=["Resume"])

# Static directory path
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

@app.get("/")
def read_root():
    # Return the index.html on root
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Welcome to AI Resume Analyzer API."}

# Mount static files AFTER defining routes to avoid conflicts
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

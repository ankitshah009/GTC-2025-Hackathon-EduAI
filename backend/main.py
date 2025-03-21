from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from app.routers import content, images, deep_research

# Initialize FastAPI app
app = FastAPI(
    title="EduAI API",
    description="Backend API for EduAI: AI-Powered Educational Content Generator",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(deep_research.router, prefix="/api/deep-research", tags=["deep-research"])

# Set up static files directory
static_directory = Path(__file__).parent / "static"
os.makedirs(static_directory / "generated_images", exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "EduAI API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

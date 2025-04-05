from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import projects, topics, master_brain

app = FastAPI(
    title="AI-Facilitated Code & Learning Graph System",
    description="A system that monitors code changes, analyzes them with Google Gemini, and maintains knowledge graphs.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(topics.router)
app.include_router(master_brain.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI-Facilitated Code & Learning Graph System API",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 
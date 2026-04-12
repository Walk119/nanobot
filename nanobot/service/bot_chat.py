"""Bot Chat Service - Entry point for skills API service.

This module provides the main entry point for exposing the skills directory
structure and file contents via RESTful API endpoints.
"""
from typing import Optional
import os
import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .service import SkillsService
from .api import SkillsAPI, ProjectsAPI

# Module-level instances (lazy initialization)
_skills_service: Optional[SkillsService] = None
_skills_api: Optional[SkillsAPI] = None
_projects_api: Optional[ProjectsAPI] = None


def get_skills_service(skills_root: Optional[str] = None) -> SkillsService:
    """Get or create the skills service instance."""
    global _skills_service
    
    if _skills_service is None:
        if skills_root is None:
            # Default to nanobot/skills
            current_dir = os.path.dirname(os.path.abspath(__file__))
            nanobot_dir = os.path.dirname(current_dir)
            skills_root = os.path.join(nanobot_dir, 'skills')
        
        _skills_service = SkillsService(skills_root)
    
    return _skills_service


def get_skills_api(skills_root: Optional[str] = None) -> SkillsAPI:
    """Get or create the skills API router."""
    global _skills_api
    
    if _skills_api is None:
        _skills_api = SkillsAPI(skills_root)
    
    return _skills_api


def get_projects_api() -> ProjectsAPI:
    """Get or create the projects API router."""
    global _projects_api
    
    if _projects_api is None:
        # ProjectsAPI defines routes that use Depends(get_db)
        # So it doesn't need to be initialized with a DB session here.
        _projects_api = ProjectsAPI()
    
    return _projects_api


def create_standalone_app() -> 'FastAPI':
    """Create a standalone FastAPI application with skills and projects endpoints."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="NanoBot Service",
        description="API service for browsing skills and managing projects",
        version="1.1.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include skills router
    skills_api = get_skills_api()
    app.include_router(skills_api.get_router())
    
    # Include projects router
    projects_api = get_projects_api()
    app.include_router(projects_api.get_router())
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "NanoBot Service",
            "version": "1.1.0",
            "endpoints": {
                "skills": "/api/skills",
                "projects": "/api/projects"
            }
        }
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    # Initialize database tables before starting
    # In a real async environment, this should be handled in a lifespan event
    # but for this standalone script, we can run it here.
    import asyncio
    from .databases.session import init_db
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print("Initializing database...")
        loop.run_until_complete(init_db())
    finally:
        loop.close()

    app = create_standalone_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

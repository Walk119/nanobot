"""Bot Chat Service - Entry point for skills API service.

This module provides the main entry point for exposing the skills directory
structure and file contents via RESTful API endpoints.

Usage:
    from nanobot.service import SkillsAPI
    
    # Create FastAPI app
    from fastapi import FastAPI
    app = FastAPI()
    
    # Include skills router
    skills_api = SkillsAPI()
    app.include_router(skills_api.get_router())
    
    # Or use the bot_chat service directly
    from nanobot.service.bot_chat import get_skills_service, get_skills_api
    service = get_skills_service()
    api = get_skills_api()
"""
from typing import Optional
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
print(current_dir, project_root)
sys.path.insert(0, project_root)
from .service import SkillsService
from .api import SkillsAPI

# Module-level instances (lazy initialization)
_skills_service: Optional[SkillsService] = None
_skills_api: Optional[SkillsAPI] = None


def get_skills_service(skills_root: Optional[str] = None) -> SkillsService:
    """Get or create the skills service instance.
    
    Args:
        skills_root: Path to skills directory (defaults to nanobot/skills)
        
    Returns:
        SkillsService instance
    """
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
    """Get or create the skills API router.
    
    Args:
        skills_root: Path to skills directory (defaults to nanobot/skills)
        
    Returns:
        SkillsAPI instance with registered routes
    """
    global _skills_api
    
    if _skills_api is None:
        _skills_api = SkillsAPI(skills_root)
    
    return _skills_api


def create_standalone_app() -> 'FastAPI':
    """Create a standalone FastAPI application with skills endpoints.
    
    This is a convenience function for running the skills service as a
    standalone application.
    
    Returns:
        FastAPI application instance with skills routes
        
    Example:
        from nanobot.service.bot_chat import create_standalone_app
        
        app = create_standalone_app()
        
        # Run with uvicorn
        # uvicorn nanobot.service.bot_chat:create_standalone_app --reload
    """
    from fastapi import FastAPI
    
    app = FastAPI(
        title="NanoBot Skills Service",
        description="API service for browsing and retrieving skills directory structure and content",
        version="1.0.0"
    )
    
    # Include skills router
    api = get_skills_api()
    app.include_router(api.get_router())
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "NanoBot Skills Service",
            "version": "1.0.0",
            "endpoints": {
                "list_skills": "GET /api/skills",
                "get_tree": "GET /api/skills/tree",
                "get_skill": "GET /api/skills/{skill_name}",
                "get_skill_info": "GET /api/skills/{skill_name}/info",
                "get_file": "GET /api/skills/{skill_name}/file/{file_path}",
                "get_raw_file": "GET /api/skills/file/raw?file_path={path}",
                "search": "GET /api/skills/search?q=query"
            }
        }
    
    return app


# Convenience functions for direct usage
def list_skills():
    """List all available skills."""
    service = get_skills_service()
    return service.list_skills()


def get_skill_details(skill_name: str):
    """Get detailed information about a skill."""
    service = get_skills_service()
    return service.get_skill_details(skill_name)


def get_skills_tree(include_content: bool = False, max_depth: int = -1):
    """Get the complete skills directory structure."""
    service = get_skills_service()
    return service.get_skills_tree(include_content, max_depth)


def get_file_content(file_path: str):
    """Get raw file content by path."""
    service = get_skills_service()
    return service.get_file_content(file_path)


if __name__ == "__main__":
    # For testing: run the standalone server
    import uvicorn
    
    app = create_standalone_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
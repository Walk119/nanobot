"""API layer for skills service - provides HTTP endpoints."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from .service import SkillsService
import os


class SkillsAPI:
    """API router for skills endpoints."""
    
    def __init__(self, skills_root: Optional[str] = None):
        """Initialize the API router.
        
        Args:
            skills_root: Path to skills directory (defaults to nanobot/skills)
        """
        if skills_root is None:
            # Default to nanobot/skills relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            nanobot_dir = os.path.dirname(current_dir)
            skills_root = os.path.join(nanobot_dir, 'skills')
        
        self.service = SkillsService(skills_root)
        self.router = APIRouter(prefix='/api/skills', tags=['skills'])
        self._register_routes()
    
    def _register_routes(self):
        """Register all API routes."""
        
        @self.router.get('')
        async def list_skills():
            """List all available skills.
            
            Returns:
                List of skills with basic information
            """
            return {'skills': self.service.list_skills()}
        
        @self.router.get('/tree')
        async def get_skills_tree(
            include_content: bool = Query(False, description="Include file contents"),
            max_depth: int = Query(-1, description="Maximum depth (-1 for unlimited)")
        ):
            """Get the complete skills directory structure.
            
            Args:
                include_content: Whether to include file contents
                max_depth: Maximum depth to traverse
                
            Returns:
                Complete directory tree structure
            """
            try:
                tree = self.service.get_skills_tree(include_content, max_depth)
                return tree
            except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.router.get('/{skill_name}')
        async def get_skill_details(skill_name: str):
            """Get detailed information about a specific skill.
            
            Args:
                skill_name: Name of the skill
                
            Returns:
                Detailed skill information including structure
            """
            details = self.service.get_skill_details(skill_name)
            if details is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Skill '{skill_name}' not found"
                )
            return details
        
        @self.router.get('/{skill_name}/info')
        async def get_skill_info(skill_name: str):
            """Get basic information about a skill.
            
            Args:
                skill_name: Name of the skill
                
            Returns:
                Basic skill information
            """
            info = self.service.get_skill_info(skill_name)
            if info is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Skill '{skill_name}' not found"
                )
            
            return {
                'name': info.name,
                'description': info.description,
                'directory': info.directory,
                'has_scripts': info.has_scripts,
                'script_count': info.script_count,
            }
        
        @self.router.get('/{skill_name}/file/{file_path:path}')
        async def get_skill_file(skill_name: str, file_path: str):
            """Get a specific file from a skill.
            
            Args:
                skill_name: Name of the skill
                file_path: Relative path within the skill directory
                
            Returns:
                File content and metadata
            """
            full_path = f"{skill_name}/{file_path}"
            file_node = self.service.get_file(full_path)
            
            if file_node is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"File '{full_path}' not found"
                )
            
            return {
                'name': file_node.name,
                'path': file_node.path,
                'content': file_node.content,
                'size': file_node.size,
                'extension': file_node.extension,
            }
        
        @self.router.get('/search')
        async def search_skills(q: str = Query(..., description="Search query")):
            """Search skills by name or description.
            
            Args:
                q: Search query string
                
            Returns:
                List of matching skills
            """
            if len(q) < 2:
                raise HTTPException(
                    status_code=400, 
                    detail="Search query must be at least 2 characters"
                )
            
            results = self.service.search_skills(q)
            return {'results': results, 'count': len(results)}
        
        @self.router.get('/file/raw')
        async def get_raw_file(file_path: str = Query(..., description="Relative file path from skills root")):
            """Get raw file content by file path.
            
            Args:
                file_path: Relative path from skills root (e.g., 'github/SKILL.md')
                
            Returns:
                Plain text content of the file
            """
            content = self.service.get_file_content(file_path)
            
            if content is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"File '{file_path}' not found or cannot be read"
                )
            
            # Return as plain text with appropriate content type
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(content, media_type="text/plain")
    
    def get_router(self) -> APIRouter:
        """Get the FastAPI router instance.
        
        Returns:
            FastAPI APIRouter with all skills routes registered
        """
        return self.router

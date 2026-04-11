"""API layer for skills service - provides HTTP endpoints."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query,Path, Depends, Body
from .service import SkillsService
from .chat_service import ChatService
import os
from pathlib import Path
from loguru import logger


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
        
        self.default_skills_root = skills_root
        self.router = APIRouter(prefix='/api/skills', tags=['skills'])
        self._register_routes()

    def get_service(self, skill_root: Optional[str] = Query(None, description="Custom skills root path")):
        """Dependency to get the appropriate SkillsService instance.
        
        Args:
            skill_root: Optional custom root path from query parameter
            
        Returns:
            SkillsService instance initialized with the target root
        """
        if skill_root:
            # Convert relative path to absolute path to ensure consistent resolution
            if not os.path.isabs(skill_root):
                # Handle both with and without ./ prefix
                current_dir = Path(__file__).parent.parent.parent
                target_root = (current_dir/skill_root).resolve()
            else:
                target_root = skill_root
        else:
            target_root = self.default_skills_root
        return SkillsService(target_root)

    def get_chat_service(self, config: Optional[str] = Query(None, description="Path to config file"),
                         workspace: Optional[str] = Query(None, description="Workspace directory")):
        """Dependency to get a ChatService instance.
        
        Args:
            config: Path to config file
            workspace: Path to workspace directory
            
        Returns:
            ChatService instance
        """
        # If config or workspace is None, read from config.json
        logger.info(f"generate chat service. config: {config}, workspace: {workspace}")
        if config is None or workspace is None:
            import json
            import os

            config_file = os.path.join(os.path.dirname(__file__), 'config.json')
            logger.info(f"read config.json from {config_file}")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if config is None and 'config' in config_data:
                        config = config_data['config']
                    if workspace is None and 'workspace' in config_data:
                        workspace = config_data['workspace']
        current_dir = Path(__file__).parent.parent.parent
        if not Path(config).is_absolute():
            config = Path(current_dir / config).resolve()
        if not Path(workspace).is_absolute():
            workspace = Path(current_dir / workspace).resolve()
        logger.info(f"config_path: {config}, workspace: {workspace}")
        return ChatService(config_path=config, workspace=workspace)
    
    def _register_routes(self):
        """Register all API routes."""
        
        @self.router.get('')
        async def list_skills(service: SkillsService = Depends(self.get_service)):
            """List all available skills.
            
            Returns:
                List of skills with basic information
            """
            return {'skills': service.list_skills()}
        
        @self.router.get('/tree')
        async def get_skills_tree(
            include_content: bool = Query(False, description="Include file contents"),
            max_depth: int = Query(-1, description="Maximum depth (-1 for unlimited)"),
            service: SkillsService = Depends(self.get_service)
        ):
            """Get the complete skills directory structure.
            
            Args:
                include_content: Whether to include file contents
                max_depth: Maximum depth to traverse
                
            Returns:
                Complete directory tree structure
            """
            try:
                tree = service.get_skills_tree(include_content, max_depth)
                return tree
            except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.router.get('/search')
        async def search_skills(
            q: str = Query(..., description="Search query"),
            service: SkillsService = Depends(self.get_service)
        ):
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
            
            results = service.search_skills(q)
            return {'results': results, 'count': len(results)}
        
        @self.router.get('/file/raw')
        async def get_raw_file(
            file_path: str = Query(..., description="Relative file path from skills root"),
            service: SkillsService = Depends(self.get_service)
        ):
            """Get raw file content by file path.
            
            Args:
                file_path: Relative path from skills root (e.g., 'github/SKILL.md')
                
            Returns:
                Plain text content of the file
            """
            content = service.get_file_content(file_path)
            
            if content is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"File '{file_path}' not found or cannot be read"
                )
            
            # Return as plain text with appropriate content type
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(content, media_type="text/plain")

        @self.router.get('/{skill_name}')
        async def get_skill_details(
            skill_name: str,
            service: SkillsService = Depends(self.get_service)
        ):
            """Get detailed information about a specific skill.
            
            Args:
                skill_name: Name of the skill
                
            Returns:
                Detailed skill information including structure
            """
            details = service.get_skill_details(skill_name)
            if details is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Skill '{skill_name}' not found"
                )
            return details
        
        @self.router.get('/{skill_name}/info')
        async def get_skill_info(
            skill_name: str,
            service: SkillsService = Depends(self.get_service)
        ):
            """Get basic information about a skill.
            
            Args:
                skill_name: Name of the skill
                
            Returns:
                Basic skill information
            """
            info = service.get_skill_info(skill_name)
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
        async def get_skill_file(
            skill_name: str, 
            file_path: str,
            service: SkillsService = Depends(self.get_service)
        ):
            """Get a specific file from a skill.
            
            Args:
                skill_name: Name of the skill
                file_path: Relative path within the skill directory
                
            Returns:
                File content and metadata
            """
            full_path = f"{skill_name}/{file_path}"
            file_node = service.get_file(full_path)
            
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

        @self.router.post('/agent/chat')
        async def agent_chat(
                message: str = Body(..., description="Message to send to the agent", embed=True),
                session_id: str = Query("api:direct", description="Session ID"),
                chat_service: ChatService = Depends(self.get_chat_service)
        ):
            """Interact with the agent directly via API.

            Args:
                message: Message to send to the agent
                session_id: Session ID
                chat_service: ChatService instance

            Returns:
                Agent response
            """
            try:
                print('message', message)
                # Process message
                response = await chat_service.process_message(message, session_id)

                # Close the chat service
                await chat_service.close()

                return response

            except Exception as e:
                # Ensure we close the service even if there's an error
                try:
                    await chat_service.close()
                except:
                    pass

                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing agent request: {str(e)}"
                )

    def get_router(self) -> APIRouter:
        """Get the FastAPI router instance.
        
        Returns:
            FastAPI APIRouter with all skills routes registered
        """
        return self.router
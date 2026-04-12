"""API layer for skills service - provides HTTP endpoints."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Path, Depends, Body
from .service import SkillsService
from .chat_service import ChatService
from .project.project_base import ProjectService
from .databases.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
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
        self.router = APIRouter(prefix='/api', tags=['skills'])
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
        
        @self.router.get('/skills')
        async def list_skills(service: SkillsService = Depends(self.get_service)):
            """List all available skills."""
            return {'skills': service.list_skills()}
        
        @self.router.get('/skills/tree')
        async def get_skills_tree(
            include_content: bool = Query(False, description="Include file contents"),
            max_depth: int = Query(-1, description="Maximum depth (-1 for unlimited)"),
            service: SkillsService = Depends(self.get_service)
        ):
            """Get the complete skills directory structure."""
            try:
                tree = service.get_skills_tree(include_content, max_depth)
                return tree
            except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.router.get('/skills/search')
        async def search_skills(
            q: str = Query(..., description="Search query"),
            service: SkillsService = Depends(self.get_service)
        ):
            """Search skills by name or description."""
            if len(q) < 2:
                raise HTTPException(
                    status_code=400, 
                    detail="Search query must be at least 2 characters"
                )
            
            results = service.search_skills(q)
            return {'results': results, 'count': len(results)}
        
        @self.router.get('/skills/file/raw')
        async def get_raw_file(
            file_path: str = Query(..., description="Relative file path from skills root"),
            service: SkillsService = Depends(self.get_service)
        ):
            """Get raw file content by file path."""
            content = service.get_file_content(file_path)
            
            if content is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"File '{file_path}' not found or cannot be read"
                )
            
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(content, media_type="text/plain")

        @self.router.put('/skills/file/raw')
        async def update_raw_file(
            file_path: str = Query(..., description="Relative file path from skills root"),
            content: str = Body(..., embed=True, description="The new content for the file"),
            service: SkillsService = Depends(self.get_service)
        ):
            """Update raw file content by file path."""
            try:
                success = service.update_file_content(file_path, content)
                if not success:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to update file '{file_path}'"
                    )
                return {"status": "success", "file_path": file_path}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.get('/skills/{skill_name}')
        async def get_skill_details(
            skill_name: str,
            service: SkillsService = Depends(self.get_service)
        ):
            """Get detailed information about a specific skill."""
            details = service.get_skill_details(skill_name)
            if details is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Skill '{skill_name}' not found"
                )
            return details
        
        @self.router.get('/skills/{skill_name}/info')
        async def get_skill_info(
            skill_name: str,
            service: SkillsService = Depends(self.get_service)
        ):
            """Get basic information about a skill."""
            info = info = service.get_skill_info(skill_name)
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
        
        @self.router.get('/skills/{skill_name}/file/{file_path:path}')
        async def get_skill_file(
            skill_name: str, 
            file_path: str,
            service: SkillsService = Depends(self.get_service)
        ):
            """Get a specific file from a skill."""
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

        @self.router.post('/skills/agent/chat')
        async def agent_chat(
                message: str = Body(..., description="Message to send to the agent", embed=True),
                session_id: str = Query("api:direct", description="Session ID"),
                chat_service: ChatService = Depends(self.get_chat_service)
        ):
            """Interact with the agent directly via API."""
            try:
                print('message', message)
                response = await chat_service.process_message(message, session_id)
                await chat_service.close()
                return response
            except Exception as e:
                try:
                    await chat_service.close()
                except:
                    pass
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing agent request: {str(e)}"
                )

        @self.router.post('/nodes')
        async def create_node(
            name: str = Body(..., embed=True),
            type: str = Body(..., embed=True),
            parentId: Optional[str] = Body(None, embed=True),
            content: Optional[str] = Body(None, embed=True),
            service: SkillsService = Depends(self.get_service)
        ):
            """Create a new file or directory node."""
            try:
                node_type = 'folder' if type == 'folder' else 'file'
                parent_path = parentId if parentId else ""
                
                # 构建相对路径
                if parent_path:
                    rel_path = f"{parent_path}/{name}"
                else:
                    rel_path = name
                
                if node_type == 'file':
                    success = service.repository.create_file(rel_path, content or "")
                else:
                    success = service.repository.create_directory(rel_path)
                
                if not success:
                    raise Exception(f"Failed to create {node_type}")

                return {
                    "path": rel_path,
                    "name": name,
                    "type": type,
                    "content": content if node_type == 'file' else None
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.patch('/nodes/{path:path}')
        async def update_node(
            path: str,
            name: Optional[str] = Body(None, embed=True),
            destination: Optional[str] = Body(None, embed=True),
            service: SkillsService = Depends(self.get_service)
        ):
            """Rename or move a node."""
            try:
                if destination:
                    target_path = destination
                elif name:
                    p = Path(path)
                    # 如果 p.parent 是 "."，说明文件在根目录
                    parent_dir = str(p.parent)
                    if parent_dir == ".":
                        target_path = name
                    else:
                        target_path = f"{parent_dir}/{name}"
                else:
                    raise HTTPException(status_code=400, detail="Either name or destination must be provided")

                new_path = service.repository.move_node(path, target_path)
                return {"path": new_path}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.delete('/nodes/{path:path}')
        async def delete_node(
            path: str,
            service: SkillsService = Depends(self.get_service)
        ):
            """Delete a node."""
            try:
                full_path = service.skills_root / path
                if not full_path.exists():
                     raise HTTPException(status_code=404, detail="Node not found")
                
                if full_path.is_file():
                    full_path.unlink()
                else:
                    import shutil
                    shutil.rmtree(full_path)
                return {"status": "success"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def get_router(self) -> APIRouter:
        """Get the FastAPI router instance."""
        return self.router


class ProjectsAPI:
    """API router for projects endpoints."""
    
    def __init__(self):
        """Initialize the API router."""
        self.router = APIRouter(prefix='/api/projects', tags=['projects'])
        self._register_routes()

    def get_service(self, db: AsyncSession = Depends(get_db)) -> ProjectService:
        """Dependency to get the ProjectService instance."""
        return ProjectService(db)
    
    def _register_routes(self):
        """Register all API routes."""
        
        @self.router.get('')
        async def list_projects(service: ProjectService = Depends(self.get_service)):
            """List all registered projects."""
            projects = await service.list_projects()
            return {'projects': [
                {
                    'name': p.name,
                    'description': p.description,
                    'path': p.path,
                    'created_at': p.created_at
                }
                for p in projects
            ]}
        
        @self.router.get('/detail')
        async def get_project(
            path: str = Query(..., description="Unique project path"),
            service: ProjectService = Depends(self.get_service)
        ):
            """Get a specific project by path."""
            project = await service.get_project(path)
            if project is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Project with path '{path}' not found"
                )
            return {
                'name': project.name,
                'description': project.description,
                'path': project.path,
                'created_at': project.created_at
            }
        
        @self.router.post('')
        async def register_project(
            path: str = Body(..., description="Project unique path"),
            name: Optional[str] = Body(None, description="Project display name"),
            description: Optional[str] = Body(None, description="Project description"),
            service: ProjectService = Depends(self.get_service)
        ):
            """Register a new project or update an existing one by path."""
            try:
                project = await service.register_project(
                    path=path,
                    name=name,
                    description=description
                )
                return {
                    'name': project.name,
                    'description': project.description,
                    'path': project.path,
                    'created_at': project.created_at
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put('')
        async def update_project(
            path: str = Query(..., description="Project path identifier"),
            name: Optional[str] = Body(None, description="New project name"),
            description: Optional[str] = Body(None, description="New project description"),
            service: ProjectService = Depends(self.get_service)
        ):
            """Update an existing project identified by path."""
            update_data = {}
            if name is not None: update_data['name'] = name
            if description is not None: update_data['description'] = description
            
            project = await service.update_project(path, **update_data)
            if project is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Project with path '{path}' not found"
                )
            return {
                'name': project.name,
                'description': project.description,
                'path': project.path,
                'created_at': project.created_at
            }
        
        @self.router.delete('')
        async def unregister_project(
            path: str = Query(..., description="Project path to unregister"),
            service: ProjectService = Depends(self.get_service)
        ):
            """Unregister (delete) a project record by path."""
            deleted = await service.unregister_project(path)
            if not deleted:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Project with path '{path}' not found"
                )
            return {'message': f"Project with path '{path}' unregistered successfully"}

    def get_router(self) -> APIRouter:
        """Get the FastAPI router instance."""
        return self.router

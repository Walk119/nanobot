# nanobot/service/project/project_base.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..databases.repository import ProjectRepository
from ..databases.models import ProjectModel
from pathlib import Path
from loguru import logger

class ProjectService:
    """Business logic for project operations, identifying projects by their path."""

    def __init__(self, db: AsyncSession):
        """Initialize the project service.

        Args:
            db: AsyncSession instance for database operations
        """
        self.repository = ProjectRepository(db)

    async def get_project(self, path: str) -> Optional[ProjectModel]:
        """Get a project by its unique path.

        Args:
            path: Project absolute or relative path

        Returns:
            ProjectModel or None if not found
        """
        return await self.repository.get_project_by_path(path)

    async def list_projects(self) -> List[ProjectModel]:
        """List all registered projects.

        Returns:
            List of ProjectModel objects
        """
        return await self.repository.list_projects()

    async def register_project(self, path: str, name: Optional[str] = None,
                               description: Optional[str] = None) -> ProjectModel:
        """Register a new project or update existing one by path.

        Args:
            path: The unique project path
            name: Display name (defaults to directory name if None)
            description: Optional description

        Returns:
            The created or updated ProjectModel
        """
        existing = await self.get_project(path)
        if existing:
            update_data = {}
            if name: update_data['name'] = name
            if description: update_data['description'] = description
            return await self.repository.update_project_by_path(path, **update_data)

        # 如果没有名字，取路径最后一部分
        if not name:
            import os
            name = os.path.basename(path.rstrip(os.sep))
        if not Path(path).is_dir():
            logger.info(f'insert into db and mkdir {path}')
            Path(path).mkdir(parents=True, exist_ok=True)
        return await self.repository.create_project(
            path=path,
            name=name,
            description=description or ""
        )

    async def update_project(self, path: str, **kwargs) -> Optional[ProjectModel]:
        """Update an existing project identified by path.

        Args:
            path: Project path
            **kwargs: Project attributes to update (name, description)

        Returns:
            Updated ProjectModel or None if not found
        """
        return await self.repository.update_project_by_path(path, **kwargs)

    async def unregister_project(self, path: str) -> bool:
        """Unregister (delete) a project by its path.

        Args:
            path: Project path

        Returns:
            True if project was deleted, False otherwise
        """
        return await self.repository.delete_project_by_path(path)
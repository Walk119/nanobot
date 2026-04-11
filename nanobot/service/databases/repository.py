from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import SkillModel, ProjectModel


class DatabaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_skill_by_id(self, skill_id: int) -> Optional[SkillModel]:
        return await self.db.get(SkillModel, skill_id)

    async def get_skill_by_name(self, name: str) -> Optional[SkillModel]:
        stmt = select(SkillModel).where(SkillModel.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_skills(self) -> List[SkillModel]:
        stmt = select(SkillModel).order_by(SkillModel.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_skill(self, **kwargs) -> SkillModel:
        new_skill = SkillModel(**kwargs)
        self.db.add(new_skill)
        await self.db.commit()
        await self.db.refresh(new_skill)
        return new_skill

    async def update_skill(self, skill_id: int, **kwargs) -> Optional[SkillModel]:
        if not kwargs:
            return await self.get_skill_by_id(skill_id)

        stmt = update(SkillModel).where(SkillModel.id == skill_id).values(**kwargs)
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_skill_by_id(skill_id)

    async def delete_skill(self, skill_id: int) -> bool:
        stmt = delete(SkillModel).where(SkillModel.id == skill_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_project_by_id(self, project_id: int) -> Optional[ProjectModel]:
        return await self.db.get(ProjectModel, project_id)

    async def get_project_by_name(self, name: str) -> Optional[ProjectModel]:
        stmt = select(ProjectModel).where(ProjectModel.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_projects(self) -> List[ProjectModel]:
        stmt = select(ProjectModel).order_by(ProjectModel.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_project(self, **kwargs) -> ProjectModel:
        new_project = ProjectModel(**kwargs)
        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)
        return new_project

    async def update_project(self, project_id: int, **kwargs) -> Optional[ProjectModel]:
        if not kwargs:
            return await self.get_project_by_id(project_id)

        stmt = update(ProjectModel).where(ProjectModel.id == project_id).values(**kwargs)
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_project_by_id(project_id)

    async def delete_project(self, project_id: int) -> bool:
        stmt = delete(ProjectModel).where(ProjectModel.id == project_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import SkillModel, ProjectModel


async def init_default_data(db: AsyncSession):
    """初始化默认数据，确保数据库中有基础配置"""
    # 检查是否已有数据
    result = await db.execute(select(SkillModel).limit(1))
    if not result.scalars().first():
        default_skill = SkillModel(
            name="base_bot",
            description="Default assistant",
            directory="nanobot/skills/base_bot",  # 补全必填字段
            has_scripts=True
        )
        db.add(default_skill)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def init_project(db: AsyncSession):
    """初始化默认项目"""
    result = await db.execute(select(ProjectModel).limit(1))
    if not result.scalars().first():
        default_project = ProjectModel(
            name="nanobot",
            description="nanobot skills",
            path="nanobot/skills",  # 补全必填字段
        )
        db.add(default_project)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

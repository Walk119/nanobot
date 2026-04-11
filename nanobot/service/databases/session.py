from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import json
import os
from pathlib import Path
from loguru import logger
# Read workspace path from config.json
current_dir = Path(__file__).parent.parent.parent
config_path = Path(current_dir / 'service/config.json')
logger.info(config_path)
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

workspace_path = config.get('workspace', 'nanobot/cli/workspace')

# Create database path in workspace directory
if not Path(workspace_path).is_absolute():
    workspace_path = Path(Path(current_dir).parent / workspace_path).resolve()

# Ensure workspace directory exists
os.makedirs(workspace_path, exist_ok=True)

# Create database URL using workspace path
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(workspace_path, 'nanobot.db')}"
logger.info(DATABASE_URL)
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库，创建所有表"""
    from .models import SkillModel, ProjectModel  # 导入所有模型，确保它们被注册

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """删除所有表"""
    from .models import SkillModel  # 导入所有模型，确保它们被注册
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
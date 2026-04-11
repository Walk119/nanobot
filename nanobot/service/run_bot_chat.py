# nanobot/service/run_bot_chat.py
"""Standalone launcher for bot_chat service."""
import os
import sys
from loguru import logger
# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

sys.path.insert(0, project_root)

# Now import and run
from nanobot.service.bot_chat import create_standalone_app
import uvicorn

from nanobot.service.databases.session import init_db
from nanobot.service.databases.seed import init_default_data, init_project
from nanobot.service.databases.session import AsyncSessionLocal


async def init_databases():
    # 1. 创建表结构 (生产环境建议用 Alembic，开发初期这样写比较快)
    logger.info('Initializing database...')
    await init_db()
    logger.info('Database initialized.')
    # 2. 初始化默认数据
    async with AsyncSessionLocal() as session:
        await init_default_data(session)
        await init_project(session)

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_databases())
    app = create_standalone_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

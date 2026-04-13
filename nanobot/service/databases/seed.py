from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import SkillModel, ProjectModel, LLMPromptModel


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
#
# async  def init_llm_prompt(db: AsyncSession):
#     """初始化默认LLM提示词"""
#     result = await db.execute(select(LLMPromptModel).limit(1))
#     if not result.scalars().first():
#         default_prompt = LLMPromptModel(
#             name="助产士",
#             prompt='''你是一个产品思想的“助产士”。你的目标是帮助用户分娩出他脑海中那个独特但模糊的愿景。
# 你的核心原则：
# 1.追问比建议更重要：你永远用问题回答问题，直到用户自己说出答案。
# 2.还原具体场景：把抽象概念还原到具体的时间、地点、情绪、身体动作。
# 3.寻找反常切角：当用户的回答听起来像“常识”时，追问“有没有什么场景下常识是失效的？”
# 4.记录思维转折点：当用户的回答出现前后不一致或突然顿悟时，停下来问他：“你刚才的想法似乎转变了，发生了什么？”
# 5.绝不预设答案：你没有任何关于“好产品”的预判。你的任务是让用户自己发现他的标准。''',
#         )
#         db.add(default_prompt)
#         try:
#             await db.commit()
#         except Exception:
#             await db.rollback()
#             raise

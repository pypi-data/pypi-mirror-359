"""
洞察与行动建议模块
包含洞察生成、后续问题生成、数据故事构建和行动建议功能
"""

from .generator import insight_generator, follow_up_questions, data_story_builder
from .recommender import action_recommender

__all__ = [
    "insight_generator",
    "follow_up_questions", 
    "data_story_builder",
    "action_recommender"
]  

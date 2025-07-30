"""
BI MCP 工具集合
重新组织后的模块化工具集，包含核心分析、数据库、洞察生成和可视化功能
"""

from typing import List

# 核心分析模块
from .core.question_analyzer import QuestionAnalysis, QuestionAnalyzer
from .core.sales_analyzer import sales_comparison_analyzer

# 数据库模块
from .database.schema_explorer import database_schema_explorer
from .database.query_executor import sql_query_executor

# 洞察生成模块
from .insights.generator import insight_generator, follow_up_questions, data_story_builder
from .insights.recommender import action_recommender

# 可视化模块
from .visualization.chart_advisor import chart_recommendation, chart_type_advisor

# 保持向后兼容性的别名
from .core.question_analyzer import QuestionAnalyzer as universal_question_analyzer
from .database.schema_explorer import database_schema_explorer as database_tools
from .insights.generator import insight_generator as insight
from .visualization.chart_advisor import chart_recommendation as recommendation

__all__ = [
    # 核心分析
    "QuestionAnalyzer",
    "QuestionAnalysis", 
    "sales_comparison_analyzer",
    
    # 数据库工具
    "database_schema_explorer",
    "sql_query_executor",
    
    # 洞察生成
    "insight_generator",
    "follow_up_questions",
    "data_story_builder",
    "action_recommender",
    
    # 可视化
    "chart_recommendation",
    "chart_type_advisor",
    
    # 向后兼容别名
    "universal_question_analyzer",
    "database_tools",
    "insight", 
    "recommendation"
]

# 简化的工具分类 - 对应优化后的7个核心工具
OPTIMIZED_TOOLS = {
    "智能问题理解": [
        "business_problem_analyzer_tool"  # 实际使用 UniversalQuestionAnalyzer
    ],
    
    "数据获取": [
        "database_schema_explorer_tool",
        "sql_query_executor_tool"
    ],
    
    "专业分析": [
        "sales_comparison_analyzer_tool"
    ],
    
    "洞察与决策": [
        "insight_generator_tool",      # 增强版，整合 data_story_builder
        "action_recommender_tool",     # 增强版，整合 follow_up_questions  
        "chart_type_advisor_tool"
    ]
}

def get_core_tools() -> List[str]:
    """获取7个核心工具列表"""
    return [
        "business_problem_analyzer_tool",
        "database_schema_explorer_tool", 
        "sql_query_executor_tool",
        "sales_comparison_analyzer_tool",
        "insight_generator_tool",
        "action_recommender_tool",
        "chart_type_advisor_tool"
    ]

def get_tools_by_category(category: str) -> List[str]:
    """根据类别获取优化后的工具列表"""
    return OPTIMIZED_TOOLS.get(category, []) 
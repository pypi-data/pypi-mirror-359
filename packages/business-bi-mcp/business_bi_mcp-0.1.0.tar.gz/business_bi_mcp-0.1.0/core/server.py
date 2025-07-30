"""
MCP服务器配置模块
管理FastMCP服务器的创建、配置和工具注册
"""

import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP

# 导入智能BI工具
from tools import (
    business_problem_analyzer, question_guide, kpi_identifier,
    analysis_method_recommender, chart_type_advisor, simple_analysis_planner,
    data_collection_guide, result_interpreter,
    insight_generator, action_recommender, follow_up_questions, data_story_builder
)

# 降低 MCP 协议日志级别
logging.getLogger("mcp").setLevel(logging.WARNING)


def create_mcp_server(name: str = "business_bi_assistant") -> FastMCP:
    """
    创建并配置MCP服务器
    
    Args:
        name: 服务器名称
        
    Returns:
        配置好的FastMCP服务器实例
    """
    mcp = FastMCP(name)
    
    # 注册智能BI工具
    register_bi_tools(mcp)
    
    # 注册基础工具（保持向后兼容）
    register_basic_tools(mcp)
    
    return mcp


def register_bi_tools(mcp: FastMCP) -> None:
    """
    注册12个核心智能BI工具
    """
    
    # 业务问题分析工具组
    @mcp.tool(
        title="业务问题分析器",
        description="帮助用户理解和定义业务问题，提供结构化的问题分析框架"
    )
    async def business_problem_analyzer_tool(
        problem_description: str,
        business_context: Optional[str] = None,
        time_period: Optional[str] = None,
        current_situation: Optional[str] = None
    ):
        return await business_problem_analyzer(problem_description, business_context, time_period, current_situation)
    
    @mcp.tool(
        title="问题引导器", 
        description="帮助用户明确分析目标和问题，提供结构化的问题引导"
    )
    async def question_guide_tool(
        user_goal: str,
        business_type: Optional[str] = None,
        available_data: Optional[str] = None,
        time_constraint: Optional[str] = None
    ):
        return await question_guide(user_goal, business_type, available_data, time_constraint)
    
    @mcp.tool(
        title="KPI识别器",
        description="帮助用户识别关键绩效指标，建立监控体系"
    )
    async def kpi_identifier_tool(
        business_goal: str,
        problem_area: str,
        business_model: Optional[str] = None,
        industry: Optional[str] = None
    ):
        return await kpi_identifier(business_goal, problem_area, business_model, industry)
    
    # 分析方法推荐工具组
    @mcp.tool(
        title="分析方法推荐器",
        description="根据业务问题推荐合适的分析方法和技术"
    )
    async def analysis_method_recommender_tool(
        problem_type: str,
        data_availability: str,
        business_size: str,
        time_constraint: Optional[str] = None,
        technical_level: Optional[str] = None
    ):
        return await analysis_method_recommender(problem_type, data_availability, business_size, time_constraint, technical_level)
    
    @mcp.tool(
        title="图表类型顾问",
        description="推荐合适的图表类型来展示分析结果"
    )
    async def chart_type_advisor_tool(
        data_type: str,
        analysis_purpose: str,
        audience_level: str,
        data_size: Optional[str] = None
    ):
        return await chart_type_advisor(data_type, analysis_purpose, audience_level, data_size)
    
    @mcp.tool(
        title="简化分析规划器",
        description="为没有技术背景的用户制定简化的分析计划"
    )
    async def simple_analysis_planner_tool(
        business_question: str,
        available_resources: str,
        deadline: str,
        expected_outcome: Optional[str] = None
    ):
        return await simple_analysis_planner(business_question, available_resources, deadline, expected_outcome)
    
    # 数据收集与结果解读工具组
    @mcp.tool(
        title="数据收集指导",
        description="指导用户如何收集和准备分析所需的数据"
    )
    async def data_collection_guide_tool(
        analysis_goal: str,
        data_sources: str,
        user_role: str,
        technical_capability: Optional[str] = None
    ):
        return await data_collection_guide(analysis_goal, data_sources, user_role, technical_capability)
    
    @mcp.tool(
        title="结果解读器",
        description="帮助理解和解释分析结果，提供业务洞察"
    )
    async def result_interpreter_tool(
        analysis_results: str,
        business_context: str,
        target_audience: str,
        action_focus: Optional[str] = None
    ):
        return await result_interpreter(analysis_results, business_context, target_audience, action_focus)
    
    # 洞察生成与行动建议工具组
    @mcp.tool(
        title="洞察生成器",
        description="从分析结果中提取关键业务洞察和发现"
    )
    async def insight_generator_tool(
        analysis_data: str,
        business_goal: str,
        stakeholder_interests: str,
        priority_focus: Optional[str] = None
    ):
        return await insight_generator(analysis_data, business_goal, stakeholder_interests, priority_focus)
    
    @mcp.tool(
        title="行动建议器",
        description="基于分析洞察提供具体的行动建议和实施计划"
    )
    async def action_recommender_tool(
        insights: str,
        business_constraints: str,
        implementation_capacity: str,
        priority_level: Optional[str] = None
    ):
        return await action_recommender(insights, business_constraints, implementation_capacity, priority_level)
    
    @mcp.tool(
        title="后续问题生成器",
        description="基于当前分析生成后续探索的问题和方向"
    )
    async def follow_up_questions_tool(
        current_findings: str,
        analysis_scope: str,
        business_priorities: str,
        stakeholder_needs: Optional[str] = None
    ):
        return await follow_up_questions(current_findings, analysis_scope, business_priorities, stakeholder_needs)
    
    @mcp.tool(
        title="数据故事构建器",
        description="将分析结果构建成清晰易懂的数据故事"
    )
    async def data_story_builder_tool(
        key_findings: str,
        target_audience: str,
        story_purpose: str,
        supporting_data: Optional[str] = None
    ):
        return await data_story_builder(key_findings, target_audience, story_purpose, supporting_data)


def register_basic_tools(mcp: FastMCP) -> None:
    """
    注册基础工具（BMI计算器和天气获取）
    保持与原有代码的兼容性
    """
    
    @mcp.tool(title="BMI Calculator")
    def calculate_bmi(weight_kg: float, height_m: float) -> float:
        """Calculate BMI given weight in kg and height in meters"""
        return weight_kg / (height_m**2)

    @mcp.tool(title="Weather Fetcher")  
    async def fetch_weather(city: str) -> str:
        """Fetch current weather for a city"""
        try:
            # 暂时返回模拟数据
            return f"模拟天气数据：{city} 今天晴朗，温度 25°C"
        except Exception as e:
            return f"获取天气信息失败：{str(e)}"

    # 添加资源示例
    @mcp.resource("health://bmi-categories")
    def get_bmi_categories() -> str:
        """Get BMI categories and ranges"""
        return """
BMI 分类标准：
- 体重过轻: < 18.5
- 正常体重: 18.5 - 24.9  
- 超重: 25.0 - 29.9
- 肥胖: ≥ 30.0
""" 
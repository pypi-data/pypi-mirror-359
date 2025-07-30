"""
业务问题分析工具组
包含业务问题分析器、问题引导器和KPI识别器
"""

from typing import Dict, List, Any, Optional
from core.models import (
    BaseResponse, ProblemType, BusinessSize, 
    DataAvailability, BusinessInsight
)


async def business_problem_analyzer(
    problem_description: str,
    business_context: Optional[str] = None,
    time_period: Optional[str] = None,
    current_situation: Optional[str] = None
) -> Dict[str, Any]:
    """
    业务问题分析器 - 帮助用户理解和定义业务问题
    
    Args:
        problem_description: 用户描述的业务问题
        business_context: 业务背景信息
        time_period: 问题发生的时间段
        current_situation: 当前的具体情况
        
    Returns:
        包含问题分析结果的字典
    """
    
    try:
        # 问题分类逻辑
        problem_type = classify_problem(problem_description)
        
        # 构建分析结果
        analysis_result = {
            "问题理解": {
                "核心问题": extract_core_problem(problem_description),
                "问题表现": analyze_problem_symptoms(problem_description, current_situation),
                "潜在影响": assess_potential_impact(problem_description),
                "问题类型": problem_type
            },
            "分析框架": {
                "时间维度": f"建议分析{time_period or '最近3-6个月'}的数据变化趋势",
                "空间维度": "分析不同地区/门店/渠道的差异表现",
                "产品维度": "对比不同产品/服务的表现差异", 
                "客户维度": "分析不同客户群体的行为变化"
            },
            "数据需求": generate_data_requirements(problem_type, business_context),
            "分析重点": generate_analysis_focus(problem_type),
            "预期发现": generate_expected_findings(problem_type),
            "紧急程度": assess_urgency_level(problem_description, current_situation)
        }
        
        next_steps = [
            "使用 analysis_method_recommender 获取具体分析方法",
            "使用 data_collection_guide 了解如何收集数据",
            "使用 kpi_identifier 确定关键监控指标"
        ]
        
        return BaseResponse(
            success=True,
            message="业务问题分析完成",
            data=analysis_result,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"分析过程中出现错误：{str(e)}",
            suggested_next_steps=["请检查输入信息后重试"]
        ).dict()


async def question_guide(
    user_goal: str,
    business_type: Optional[str] = None,
    available_data: Optional[str] = None,
    time_constraint: Optional[str] = None
) -> Dict[str, Any]:
    """
    问题引导器 - 帮助用户明确分析目标和问题
    
    Args:
        user_goal: 用户想要了解的目标
        business_type: 业务类型
        available_data: 可用的数据
        time_constraint: 时间限制
        
    Returns:
        包含问题引导结果的字典
    """
    
    try:
        guide_result = {
            "目标明确": {
                "核心目标": clarify_user_goal(user_goal),
                "成功标准": define_success_criteria(user_goal),
                "关键问题": generate_key_questions(user_goal, business_type)
            },
            "分析路径": {
                "第一步": "先看什么 - 最重要的指标和数据",
                "第二步": "再分析什么 - 深入分析的维度",
                "第三步": "最后对比什么 - 找出差异和原因",
                "预计时间": estimate_analysis_time(time_constraint, available_data)
            },
            "问题清单": generate_guided_questions(user_goal, business_type),
            "常见陷阱": get_common_pitfalls(business_type),
            "快速开始": generate_quick_start_guide(user_goal, available_data)
        }
        
        next_steps = [
            "根据问题清单收集相关信息",
            "使用 business_problem_analyzer 进行深入分析",
            "使用 data_collection_guide 准备数据"
        ]
        
        return BaseResponse(
            success=True,
            message="问题引导完成",
            data=guide_result,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"引导过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更具体的目标描述"]
        ).dict()


async def kpi_identifier(
    business_goal: str,
    problem_area: str,
    business_model: Optional[str] = None,
    industry: Optional[str] = None
) -> Dict[str, Any]:
    """
    KPI识别器 - 帮助用户识别关键绩效指标
    
    Args:
        business_goal: 业务目标
        problem_area: 问题领域
        business_model: 商业模式
        industry: 所属行业
        
    Returns:
        包含KPI识别结果的字典
    """
    
    try:
        kpi_result = {
            "核心KPI": identify_core_kpis(business_goal, problem_area, industry),
            "辅助指标": identify_supporting_metrics(business_goal, problem_area),
            "监控频率": {
                "日常监控": "需要每天查看的关键指标",
                "周度回顾": "每周分析的重要趋势",
                "月度评估": "每月深度分析的核心指标"
            },
            "计算方法": generate_kpi_calculations(business_goal, problem_area),
            "基准设定": suggest_benchmarks(industry, business_model),
            "预警机制": setup_alert_system(business_goal, problem_area),
            "仪表板建议": design_dashboard_layout(business_goal, problem_area)
        }
        
        next_steps = [
            "开始收集KPI相关数据",
            "使用 data_collection_guide 了解数据获取方法",
            "使用 chart_type_advisor 选择合适的展示图表"
        ]
        
        return BaseResponse(
            success=True,
            message="KPI识别完成",
            data=kpi_result,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"KPI识别过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更详细的业务目标描述"]
        ).dict()


# 辅助函数实现

def classify_problem(problem_description: str) -> str:
    """问题分类逻辑"""
    keywords_map = {
        "sales_decline": ["销售下降", "销量减少", "业绩下滑", "收入减少"],
        "customer_loss": ["客户流失", "用户减少", "客户离开", "留存率"],
        "cost_increase": ["成本上升", "费用增加", "成本控制"],
        "profit_drop": ["利润下降", "盈利减少", "毛利率"],
        "product_performance": ["产品表现", "产品销售", "产品分析"]
    }
    
    for problem_type, keywords in keywords_map.items():
        if any(keyword in problem_description for keyword in keywords):
            return problem_type
    
    return "general_analysis"


def extract_core_problem(problem_description: str) -> str:
    """提取核心问题"""
    if "销售" in problem_description or "业绩" in problem_description:
        return "业务表现未达预期，需要找出具体原因并制定改进措施"
    elif "客户" in problem_description:
        return "客户行为或满意度存在问题，需要分析客户需求和体验"
    elif "成本" in problem_description:
        return "成本控制或效率优化问题，需要分析成本结构和优化空间"
    else:
        return "业务运营中存在需要数据支持的决策问题"


def analyze_problem_symptoms(problem_description: str, current_situation: Optional[str]) -> List[str]:
    """分析问题表现"""
    symptoms = ["根据描述，问题主要表现为具体的数据变化或业务现象"]
    
    if current_situation:
        symptoms.append(f"当前状况：{current_situation}")
    
    symptoms.extend([
        "建议收集具体的数据指标来量化问题",
        "需要了解问题发生的时间、范围和程度"
    ])
    
    return symptoms


def assess_potential_impact(problem_description: str) -> List[str]:
    """评估潜在影响"""
    return [
        "短期影响：可能影响当前业务指标和客户满意度",
        "中期影响：如不解决可能影响市场竞争力",
        "长期影响：可能影响企业可持续发展",
        "建议尽快分析原因并制定应对措施"
    ]


def generate_data_requirements(problem_type: str, business_context: Optional[str]) -> Dict[str, List[str]]:
    """生成数据需求"""
    base_requirements = {
        "必需数据": [
            "核心业务指标的历史数据（至少3个月）",
            "问题发生前后的对比数据",
            "相关的业务背景信息"
        ],
        "有用数据": [
            "行业基准数据",
            "竞争对手信息",
            "客户反馈数据"
        ],
        "数据格式": [
            "Excel表格或CSV文件",
            "按时间序列整理",
            "包含必要的标签和说明"
        ]
    }
    
    return base_requirements


def generate_analysis_focus(problem_type: str) -> Dict[str, str]:
    """生成分析重点"""
    return {
        "关键指标": "最能反映问题本质的核心数据指标",
        "对比维度": "时间对比、竞品对比、细分对比",
        "细分角度": "按产品、地区、客户群体等维度细分分析",
        "关联分析": "寻找可能相关的其他业务因素"
    }


def generate_expected_findings(problem_type: str) -> List[str]:
    """生成预期发现"""
    return [
        "可能发现问题的时间规律性",
        "可能识别出特定的影响因素",
        "可能找到改进的具体方向",
        "可能发现新的业务机会"
    ]


def assess_urgency_level(problem_description: str, current_situation: Optional[str]) -> str:
    """评估紧急程度"""
    urgent_keywords = ["急", "紧急", "严重", "快速", "立即"]
    
    if any(keyword in problem_description for keyword in urgent_keywords):
        return "高 - 建议优先处理"
    elif current_situation and any(keyword in current_situation for keyword in urgent_keywords):
        return "高 - 建议优先处理"
    else:
        return "中 - 建议及时关注"


def clarify_user_goal(user_goal: str) -> str:
    """明确用户目标"""
    return f"根据您的描述，您的核心目标是：{user_goal}。建议将目标进一步细化为可衡量的具体指标。"


def define_success_criteria(user_goal: str) -> List[str]:
    """定义成功标准"""
    return [
        "能够用数据清晰描述当前状况",
        "找出问题的主要原因",
        "制定出可执行的改进方案",
        "建立持续监控机制"
    ]


def generate_key_questions(user_goal: str, business_type: Optional[str]) -> List[str]:
    """生成关键问题"""
    return [
        "具体想要改善哪个指标？",
        "目前的表现和期望的差距是多少？",
        "问题是从什么时候开始的？",
        "已经尝试过什么解决方法？",
        "有什么外部因素可能影响结果？"
    ]


def estimate_analysis_time(time_constraint: Optional[str], available_data: Optional[str]) -> str:
    """估算分析时间"""
    if time_constraint and "急" in time_constraint:
        return "快速分析：1-2天，重点关注核心指标"
    elif available_data and "充足" in available_data:
        return "深度分析：1-2周，全面系统的分析"
    else:
        return "标准分析：3-5天，平衡深度和效率"


def generate_guided_questions(user_goal: str, business_type: Optional[str]) -> List[str]:
    """生成引导性问题"""
    return [
        "为了实现目标，最重要的是了解什么？",
        "什么数据能最直接反映目标的达成情况？",
        "有哪些因素可能影响目标的实现？",
        "如何衡量改进的效果？"
    ]


def get_common_pitfalls(business_type: Optional[str]) -> List[str]:
    """获取常见陷阱"""
    return [
        "只看表面数据，不分析深层原因",
        "忽略时间因素和季节性影响",
        "没有对比基准，无法判断好坏",
        "数据不够细分，无法找到具体问题",
        "只关注问题，忽略机会"
    ]


def generate_quick_start_guide(user_goal: str, available_data: Optional[str]) -> List[str]:
    """生成快速开始指南"""
    return [
        "第一步：明确最重要的1-2个指标",
        "第二步：收集最近3个月的相关数据",
        "第三步：制作简单的趋势图查看变化",
        "第四步：按不同维度分解数据找差异",
        "第五步：结合业务背景分析可能原因"
    ]


def identify_core_kpis(business_goal: str, problem_area: str, industry: Optional[str]) -> List[Dict[str, str]]:
    """识别核心KPI"""
    kpis = []
    
    if "销售" in business_goal or "revenue" in business_goal.lower():
        kpis.extend([
            {"指标名称": "销售收入", "重要性": "极高", "计算方法": "总销售额 = 销量 × 单价"},
            {"指标名称": "销售增长率", "重要性": "高", "计算方法": "(本期销售额 - 上期销售额) / 上期销售额 × 100%"}
        ])
    
    if "客户" in business_goal:
        kpis.extend([
            {"指标名称": "客户获取成本", "重要性": "高", "计算方法": "营销费用 / 新客户数量"},
            {"指标名称": "客户留存率", "重要性": "高", "计算方法": "留存客户数 / 总客户数 × 100%"}
        ])
    
    if not kpis:  # 默认KPI
        kpis = [
            {"指标名称": "核心业务指标", "重要性": "高", "计算方法": "根据具体业务定义"},
            {"指标名称": "效率指标", "重要性": "中", "计算方法": "产出/投入"}
        ]
    
    return kpis


def identify_supporting_metrics(business_goal: str, problem_area: str) -> List[str]:
    """识别辅助指标"""
    return [
        "流量指标：网站访问量、转化率等",
        "运营指标：成本率、效率指标等", 
        "质量指标：客户满意度、产品质量等",
        "市场指标：市场份额、竞争位置等"
    ]


def generate_kpi_calculations(business_goal: str, problem_area: str) -> Dict[str, str]:
    """生成KPI计算方法"""
    return {
        "基础计算": "确保数据来源准确，计算逻辑清晰",
        "时间窗口": "选择合适的统计周期（日/周/月）",
        "对比基准": "设定行业基准或历史基准",
        "异常处理": "识别和处理异常值的方法"
    }


def suggest_benchmarks(industry: Optional[str], business_model: Optional[str]) -> List[str]:
    """建议基准设定"""
    return [
        "内部基准：与自己的历史表现对比",
        "行业基准：与同行业平均水平对比",
        "竞品基准：与主要竞争对手对比",
        "目标基准：基于业务目标设定的理想水平"
    ]


def setup_alert_system(business_goal: str, problem_area: str) -> Dict[str, str]:
    """设置预警机制"""
    return {
        "绿色预警": "指标正常，继续保持",
        "黄色预警": "指标轻微异常，需要关注",
        "红色预警": "指标严重异常，需要立即行动",
        "触发条件": "基于历史数据设定合理的预警阈值"
    }


def design_dashboard_layout(business_goal: str, problem_area: str) -> List[str]:
    """设计仪表板布局"""
    return [
        "顶部：最重要的核心KPI，用大数字显示",
        "中部：关键趋势图表，显示变化趋势",
        "底部：详细分解数据，支持钻取分析",
        "右侧：预警信息和关键提醒"
    ] 
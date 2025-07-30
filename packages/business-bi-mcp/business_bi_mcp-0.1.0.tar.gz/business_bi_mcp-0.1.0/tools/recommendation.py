"""
分析方法推荐工具组
包含分析方法推荐器、图表类型顾问和简化分析规划师
"""

from typing import Dict, List, Any, Optional
from core.models import (
    BaseResponse, AnalysisMethod, ChartRecommendation,
    AnalysisPurpose, Audience, DataAvailability, BusinessSize
)


async def analysis_method_recommender(
    problem_type: str,
    analysis_goal: str,
    data_availability: Optional[str] = "moderate",
    business_size: Optional[str] = "medium"
) -> Dict[str, Any]:
    """
    分析方法推荐器 - 根据业务问题推荐具体的分析方法和步骤
    
    Args:
        problem_type: 问题类型分类
        analysis_goal: 分析的主要目标
        data_availability: 可用数据的丰富程度
        business_size: 业务规模
        
    Returns:
        包含推荐分析方法的字典
    """
    
    try:
        # 获取分析方法库
        methods_db = get_analysis_methods_database()
        
        # 根据问题类型获取推荐方法
        problem_methods = methods_db.get(problem_type, methods_db["general_analysis"])
        
        # 根据数据可用性筛选方法
        filtered_methods = filter_methods_by_data_availability(
            problem_methods["methods"], 
            data_availability
        )
        
        # 构建推荐结果
        recommendation_result = {
            "问题分析": {
                "问题类型": problem_methods["name"],
                "问题描述": problem_methods["description"],
                "分析目标": analysis_goal
            },
            "推荐方法": generate_method_recommendations(filtered_methods, business_size),
            "实施步骤": generate_detailed_steps(filtered_methods[0] if filtered_methods else None),
            "数据清单": generate_data_checklist(problem_type, analysis_goal),
            "时间投入": estimate_time_investment(filtered_methods, data_availability),
            "难度评估": assess_difficulty_level(filtered_methods, business_size),
            "成功要素": get_success_factors(problem_type)
        }
        
        next_steps = [
            "使用 chart_type_advisor 选择合适的图表",
            "使用 data_collection_guide 准备数据",
            "使用 simple_analysis_planner 制定详细计划"
        ]
        
        return BaseResponse(
            success=True,
            message="分析方法推荐完成",
            data=recommendation_result,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"推荐过程中出现错误：{str(e)}",
            suggested_next_steps=["请检查问题类型是否正确"]
        ).dict()


async def chart_type_advisor(
    analysis_purpose: str,
    message_focus: str,
    data_characteristics: Optional[str] = None,
    audience: Optional[str] = "colleagues"
) -> Dict[str, Any]:
    """
    图表类型顾问 - 根据分析目标推荐最合适的图表类型
    
    Args:
        analysis_purpose: 分析目的
        message_focus: 希望图表重点传达的信息
        data_characteristics: 数据的特点
        audience: 图表的观看对象
        
    Returns:
        包含图表推荐结果的字典
    """
    
    try:
        # 获取图表推荐库
        chart_db = get_chart_recommendations_database()
        
        # 根据分析目的获取推荐图表
        purpose_charts = chart_db.get(analysis_purpose, chart_db["comparison"])
        
        # 构建图表建议结果
        chart_advice = {
            "分析需求": {
                "分析目的": analysis_purpose,
                "重点信息": message_focus,
                "数据特点": data_characteristics or "待详细了解",
                "目标受众": audience
            },
            "推荐图表": generate_chart_recommendations(purpose_charts, audience),
            "选择指南": generate_chart_selection_guide(analysis_purpose, message_focus),
            "制作要点": generate_chart_creation_tips(purpose_charts),
            "解读指导": generate_chart_interpretation_guide(analysis_purpose),
            "工具建议": get_chart_tools_recommendations(audience),
            "常见错误": get_chart_common_mistakes(analysis_purpose)
        }
        
        next_steps = [
            "使用 data_collection_guide 准备图表数据",
            "使用 result_interpreter 学习如何解读图表",
            "使用 insight_generator 从图表中提取洞察"
        ]
        
        return BaseResponse(
            success=True,
            message="图表类型推荐完成",
            data=chart_advice,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"图表推荐过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更具体的分析需求"]
        ).dict()


async def simple_analysis_planner(
    analysis_objective: str,
    available_time: str,
    team_size: Optional[str] = "1人",
    experience_level: Optional[str] = "初级"
) -> Dict[str, Any]:
    """
    简化分析规划师 - 为业务小白制定简单易执行的分析计划
    
    Args:
        analysis_objective: 分析目标
        available_time: 可用时间
        team_size: 团队规模
        experience_level: 经验水平
        
    Returns:
        包含分析计划的字典
    """
    
    try:
        # 根据经验水平和时间制定计划
        plan_template = get_analysis_plan_template(experience_level, available_time)
        
        # 构建分析计划
        analysis_plan = {
            "项目概览": {
                "分析目标": analysis_objective,
                "团队配置": team_size,
                "时间安排": available_time,
                "经验水平": experience_level
            },
            "阶段计划": generate_phase_plan(analysis_objective, available_time, experience_level),
            "每日任务": generate_daily_tasks(available_time, experience_level),
            "关键里程碑": define_key_milestones(analysis_objective),
            "资源需求": identify_resource_requirements(team_size, experience_level),
            "风险预案": create_risk_mitigation_plan(experience_level),
            "质量检查": setup_quality_checkpoints(analysis_objective),
            "成果交付": define_deliverables(analysis_objective, available_time)
        }
        
        next_steps = [
            "开始执行第一阶段任务",
            "使用相关工具收集和分析数据",
            "定期检查进度和质量"
        ]
        
        return BaseResponse(
            success=True,
            message="分析计划制定完成",
            data=analysis_plan,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"计划制定过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更具体的时间和目标要求"]
        ).dict()


# 辅助函数实现

def get_analysis_methods_database() -> Dict[str, Any]:
    """获取分析方法数据库"""
    return {
        "sales_decline": {
            "name": "销售下降分析",
            "description": "系统性分析销售下降的原因",
            "methods": [
                {
                    "method": "趋势对比分析",
                    "description": "对比不同时间段的销售表现",
                    "steps": ["收集历史销售数据", "按月/季度制作趋势图", "识别下降起始点", "分析下降模式"],
                    "charts": ["折线图", "柱状图"],
                    "difficulty": "简单",
                    "data_requirement": "limited"
                },
                {
                    "method": "多维度拆解分析",
                    "description": "从产品、地区、客户等维度拆解分析",
                    "steps": ["按产品分类统计", "按销售区域统计", "按客户群体统计", "识别问题集中点"],
                    "charts": ["饼图", "堆积柱状图", "热力图"],
                    "difficulty": "中等",
                    "data_requirement": "moderate"
                },
                {
                    "method": "漏斗分析",
                    "description": "分析销售流程各环节的转化率",
                    "steps": ["梳理销售流程", "统计各环节数据", "计算转化率", "找出瓶颈环节"],
                    "charts": ["漏斗图", "转化率图"],
                    "difficulty": "中等",
                    "data_requirement": "comprehensive"
                }
            ]
        },
        "customer_loss": {
            "name": "客户流失分析",
            "description": "分析客户流失的原因和模式",
            "methods": [
                {
                    "method": "客户生命周期分析",
                    "description": "分析客户从获取到流失的完整过程",
                    "steps": ["定义客户流失标准", "统计客户留存率", "分析流失时间点", "识别流失原因"],
                    "charts": ["留存率曲线", "生命周期图"],
                    "difficulty": "中等",
                    "data_requirement": "moderate"
                },
                {
                    "method": "客户分群分析",
                    "description": "将客户按特征分组，分析不同群体的流失情况",
                    "steps": ["客户特征收集", "客户分群", "各群体流失率统计", "原因对比分析"],
                    "charts": ["分组对比图", "散点图"],
                    "difficulty": "复杂",
                    "data_requirement": "comprehensive"
                }
            ]
        },
        "general_analysis": {
            "name": "通用业务分析",
            "description": "适用于各种业务问题的基础分析方法",
            "methods": [
                {
                    "method": "对比分析",
                    "description": "通过对比找出差异和问题",
                    "steps": ["确定对比维度", "收集对比数据", "制作对比图表", "分析差异原因"],
                    "charts": ["柱状图", "折线图"],
                    "difficulty": "简单",
                    "data_requirement": "limited"
                }
            ]
        }
    }


def get_chart_recommendations_database() -> Dict[str, Any]:
    """获取图表推荐数据库"""
    return {
        "trend_analysis": {
            "primary_charts": [
                {
                    "type": "折线图",
                    "when": "显示数据随时间的变化趋势",
                    "pros": ["清晰显示趋势", "容易理解", "适合时间序列"],
                    "example": "月度销售额变化、客户增长趋势",
                    "difficulty": "简单"
                },
                {
                    "type": "面积图",
                    "when": "强调数量的累积或对比",
                    "pros": ["视觉冲击力强", "显示总量变化"],
                    "example": "累计销售额、市场份额变化",
                    "difficulty": "简单"
                }
            ]
        },
        "comparison": {
            "primary_charts": [
                {
                    "type": "柱状图",
                    "when": "比较不同类别的数值大小",
                    "pros": ["对比清晰", "精确显示数值", "容易制作"],
                    "example": "各产品销量对比、各地区业绩对比",
                    "difficulty": "简单"
                },
                {
                    "type": "雷达图",
                    "when": "多维度综合对比",
                    "pros": ["多维展示", "整体评价"],
                    "example": "产品多属性对比、员工绩效评估",
                    "difficulty": "中等"
                }
            ]
        },
        "composition": {
            "primary_charts": [
                {
                    "type": "饼图",
                    "when": "显示部分与整体的关系",
                    "pros": ["直观显示占比", "简单易懂"],
                    "example": "销售额构成、成本结构分析",
                    "difficulty": "简单"
                },
                {
                    "type": "堆积柱状图",
                    "when": "展示分类数据的构成和对比",
                    "pros": ["同时显示总量和构成", "支持多维对比"],
                    "example": "各月销售额及产品构成",
                    "difficulty": "中等"
                }
            ]
        }
    }


def filter_methods_by_data_availability(methods: List[Dict], data_availability: str) -> List[Dict]:
    """根据数据可用性筛选方法"""
    if data_availability == "limited":
        return [m for m in methods if m.get("data_requirement", "moderate") in ["limited", "moderate"]]
    elif data_availability == "comprehensive":
        return methods
    else:  # moderate
        return [m for m in methods if m.get("data_requirement", "moderate") != "comprehensive"]


def generate_method_recommendations(methods: List[Dict], business_size: str) -> List[Dict[str, Any]]:
    """生成方法推荐"""
    recommendations = []
    
    for i, method in enumerate(methods[:3]):  # 最多推荐3个方法
        priority = "首选" if i == 0 else "备选"
        recommendations.append({
            "优先级": priority,
            "方法名称": method["method"],
            "适用场景": method["description"],
            "推荐理由": f"适合{business_size}规模企业，{method['difficulty']}操作",
            "实施难度": method["difficulty"],
            "推荐图表": method["charts"]
        })
    
    return recommendations


def generate_detailed_steps(method: Optional[Dict]) -> List[Dict[str, str]]:
    """生成详细步骤"""
    if not method:
        return [{"步骤": "请先选择分析方法", "说明": "根据推荐选择合适的分析方法"}]
    
    detailed_steps = []
    for i, step in enumerate(method.get("steps", []), 1):
        detailed_steps.append({
            "步骤": f"第{i}步：{step}",
            "说明": f"具体操作：{step}的详细执行方法",
            "预期时间": "半天到1天",
            "注意事项": "确保数据质量和分析准确性"
        })
    
    return detailed_steps


def generate_data_checklist(problem_type: str, analysis_goal: str) -> Dict[str, List[str]]:
    """生成数据清单"""
    return {
        "必需数据": [
            "核心业务指标数据（最近3-6个月）",
            "问题相关的直接数据",
            "时间序列数据用于趋势分析"
        ],
        "有用数据": [
            "行业基准数据",
            "竞争对手信息",
            "客户反馈和行为数据",
            "外部环境因素数据"
        ],
        "数据格式": [
            "Excel或CSV格式",
            "统一的时间格式",
            "清晰的列标题",
            "完整性检查"
        ]
    }


def estimate_time_investment(methods: List[Dict], data_availability: str) -> Dict[str, str]:
    """估算时间投入"""
    base_time = {
        "limited": {"prep": "1-2天", "analysis": "2-3天", "total": "1周"},
        "moderate": {"prep": "2-3天", "analysis": "3-5天", "total": "1-2周"},
        "comprehensive": {"prep": "3-5天", "analysis": "5-7天", "total": "2-3周"}
    }
    
    time_estimate = base_time.get(data_availability, base_time["moderate"])
    
    return {
        "数据准备": time_estimate["prep"],
        "分析执行": time_estimate["analysis"],
        "总体时间": time_estimate["total"],
        "并行建议": "数据准备和分析工具学习可以并行进行"
    }


def assess_difficulty_level(methods: List[Dict], business_size: str) -> Dict[str, str]:
    """评估难度水平"""
    difficulties = [m.get("difficulty", "中等") for m in methods]
    main_difficulty = difficulties[0] if difficulties else "中等"
    
    return {
        "操作难度": main_difficulty,
        "技能要求": "基础的Excel操作和逻辑思维能力",
        "学习成本": "新手需要1-2天熟悉分析方法",
        "常见陷阱": "数据质量问题、结果过度解读、忽略业务背景"
    }


def get_success_factors(problem_type: str) -> List[str]:
    """获取成功要素"""
    return [
        "数据质量：确保数据准确、完整、及时",
        "业务理解：结合实际业务背景分析",
        "系统思维：从多个角度全面分析问题",
        "持续跟踪：建立长期监控机制",
        "行动导向：分析结果要能指导实际行动"
    ]


def generate_chart_recommendations(charts_data: Dict, audience: str) -> List[Dict[str, Any]]:
    """生成图表推荐"""
    recommendations = []
    
    for chart in charts_data.get("primary_charts", []):
        suitability = "高" if chart["difficulty"] == "简单" or audience == "management" else "中"
        recommendations.append({
            "图表类型": chart["type"],
            "适用场景": chart["when"],
            "主要优点": chart["pros"],
            "使用示例": chart["example"],
            "制作难度": chart["difficulty"],
            "适合程度": suitability
        })
    
    return recommendations


def generate_chart_selection_guide(analysis_purpose: str, message_focus: str) -> Dict[str, str]:
    """生成图表选择指南"""
    return {
        "首要原则": "选择最能突出重点信息的图表类型",
        "受众考虑": "根据观看者的专业程度选择复杂度",
        "数据特点": "根据数据的类型和规模选择合适的展示方式",
        "美观实用": "在美观和实用性之间找到平衡",
        "一致性": "同一报告中保持图表风格一致"
    }


def generate_chart_creation_tips(charts_data: Dict) -> List[str]:
    """生成图表制作要点"""
    return [
        "数据准备：确保数据格式规整，无缺失值",
        "标题设置：使用清晰明确的图表标题",
        "轴标签：为坐标轴添加适当的标签和单位",
        "颜色选择：使用对比明显但不刺眼的颜色",
        "图例说明：添加必要的图例和数据标签",
        "简洁原则：避免过多装饰，突出数据本身"
    ]


def generate_chart_interpretation_guide(analysis_purpose: str) -> List[str]:
    """生成图表解读指导"""
    return [
        "整体趋势：先看整体变化趋势和模式",
        "关键数值：识别最高、最低、异常值",
        "对比分析：不同类别或时间点的对比",
        "变化原因：结合业务背景分析变化原因",
        "行动建议：从图表洞察中提取可行建议"
    ]


def get_chart_tools_recommendations(audience: str) -> Dict[str, List[str]]:
    """获取图表工具推荐"""
    return {
        "入门工具": ["Excel/WPS表格", "腾讯文档", "Google Sheets"],
        "专业工具": ["Tableau", "Power BI", "帆软FineBI"],
        "在线工具": ["百度图说", "镝数聚", "Flourish"],
        "编程工具": ["Python matplotlib", "R ggplot2", "Echarts"]
    }


def get_chart_common_mistakes(analysis_purpose: str) -> List[str]:
    """获取常见图表错误"""
    return [
        "误用图表类型：用饼图显示趋势，用折线图显示占比",
        "轴线误导：不从0开始，夸大变化幅度",
        "信息过载：在一个图表中显示过多信息",
        "颜色滥用：使用过多颜色造成视觉混乱",
        "缺乏背景：没有提供足够的背景信息帮助理解"
    ]


def get_analysis_plan_template(experience_level: str, available_time: str) -> Dict[str, Any]:
    """获取分析计划模板"""
    templates = {
        "初级": {
            "focus": "基础分析，重点关注核心指标",
            "complexity": "简单直接的方法",
            "support": "需要更多指导和模板"
        },
        "中级": {
            "focus": "深入分析，多维度对比",
            "complexity": "中等复杂度的方法",
            "support": "可以相对独立完成"
        },
        "高级": {
            "focus": "全面分析，复杂建模",
            "complexity": "高级分析方法",
            "support": "自主性强，可指导他人"
        }
    }
    
    return templates.get(experience_level, templates["初级"])


def generate_phase_plan(objective: str, available_time: str, experience_level: str) -> List[Dict[str, Any]]:
    """生成阶段计划"""
    if "1周" in available_time or "急" in available_time:
        return [
            {"阶段": "第1-2天", "任务": "问题定义和数据收集", "产出": "数据清单和初始数据"},
            {"阶段": "第3-4天", "任务": "基础分析和图表制作", "产出": "核心图表和初步发现"},
            {"阶段": "第5-7天", "任务": "结果解读和报告撰写", "产出": "分析报告和建议"}
        ]
    else:
        return [
            {"阶段": "第1周", "任务": "需求分析和计划制定", "产出": "分析计划和数据需求"},
            {"阶段": "第2周", "任务": "数据收集和清理", "产出": "清洁的分析数据"},
            {"阶段": "第3周", "任务": "深度分析和建模", "产出": "分析模型和洞察"},
            {"阶段": "第4周", "任务": "报告撰写和汇报", "产出": "最终报告和行动计划"}
        ]


def generate_daily_tasks(available_time: str, experience_level: str) -> List[str]:
    """生成每日任务"""
    if experience_level == "初级":
        return [
            "明确今日的具体分析目标",
            "收集和整理相关数据",
            "制作1-2个核心图表",
            "记录分析过程和发现",
            "准备明日的工作计划"
        ]
    else:
        return [
            "回顾分析进度和质量",
            "深入分析特定维度",
            "验证分析结果的合理性",
            "文档化分析过程",
            "与相关人员沟通确认"
        ]


def define_key_milestones(objective: str) -> List[Dict[str, str]]:
    """定义关键里程碑"""
    return [
        {"里程碑": "需求确认", "标准": "分析目标和范围明确定义"},
        {"里程碑": "数据就绪", "标准": "所需数据收集完整且质量达标"},
        {"里程碑": "初步分析", "标准": "核心发现和趋势已经识别"},
        {"里程碑": "深度洞察", "标准": "原因分析完成，建议方案形成"},
        {"里程碑": "成果交付", "标准": "分析报告完成并获得认可"}
    ]


def identify_resource_requirements(team_size: str, experience_level: str) -> Dict[str, List[str]]:
    """识别资源需求"""
    return {
        "人力资源": [f"分析师 {team_size}", "业务专家支持", "数据提供方配合"],
        "技术资源": ["分析软件（Excel/BI工具）", "数据访问权限", "计算设备"],
        "知识资源": ["分析方法培训", "业务背景资料", "行业基准数据"],
        "时间资源": ["专门的分析时间", "沟通协调时间", "汇报展示时间"]
    }


def create_risk_mitigation_plan(experience_level: str) -> List[Dict[str, str]]:
    """创建风险预案"""
    return [
        {"风险": "数据质量问题", "预案": "建立数据验证机制，准备备用数据源"},
        {"风险": "分析方向偏离", "预案": "定期与业务方确认，设置检查点"},
        {"风险": "时间不足", "预案": "优先核心分析，简化非关键环节"},
        {"风险": "技能不够", "预案": "寻求专家支持，使用简化工具"},
        {"风险": "结果不可信", "预案": "交叉验证，请第三方审核"}
    ]


def setup_quality_checkpoints(objective: str) -> List[Dict[str, str]]:
    """设置质量检查点"""
    return [
        {"检查点": "数据质量", "标准": "数据完整性、准确性、一致性检查"},
        {"检查点": "分析逻辑", "标准": "分析方法正确，逻辑链条清晰"},
        {"检查点": "结果合理性", "标准": "结果符合业务常识，经得起推敲"},
        {"检查点": "可行性", "标准": "建议具有可操作性和实用价值"},
        {"检查点": "沟通效果", "标准": "结果能够清晰传达给目标受众"}
    ]


def define_deliverables(objective: str, available_time: str) -> List[Dict[str, str]]:
    """定义交付成果"""
    return [
        {"成果": "分析报告", "内容": "完整的问题分析和解决方案"},
        {"成果": "关键图表", "内容": "核心发现的可视化展示"},
        {"成果": "行动建议", "内容": "具体可执行的改进措施"},
        {"成果": "监控仪表板", "内容": "持续跟踪的关键指标"},
        {"成果": "知识总结", "内容": "分析过程和方法的文档化"}
    ] 
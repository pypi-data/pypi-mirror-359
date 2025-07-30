"""
洞察生成与行动建议工具组
包含洞察生成器、行动建议器、后续问题生成器和数据故事构建器
"""

from typing import Dict, List, Any, Optional
from core.models import BaseResponse, BusinessInsight


async def insight_generator(
    analysis_results: str,
    business_context: str,
    key_findings: Optional[str] = None,
    original_question: Optional[str] = None
) -> Dict[str, Any]:
    """
    洞察生成器 - 帮助从数据分析结果中提取有价值的业务洞察
    
    Args:
        analysis_results: 分析得到的结果或观察到的现象
        business_context: 业务背景信息
        key_findings: 主要发现或数据表现
        original_question: 最初想要解决的业务问题
        
    Returns:
        包含业务洞察的字典
    """
    
    try:
        # 解析分析结果并提取洞察
        raw_insights = extract_raw_insights(analysis_results, key_findings)
        
        # 结合业务背景深化洞察
        business_insights = contextualize_insights(raw_insights, business_context)
        
        # 评估洞察的重要性和可信度
        insight_assessment = assess_insight_quality(business_insights, analysis_results)
        
        # 构建洞察报告
        insight_report = {
            "分析概要": {
                "原始问题": original_question or "业务问题分析",
                "分析结果": analysis_results[:200] + "..." if len(analysis_results) > 200 else analysis_results,
                "业务背景": business_context,
                "关键发现": key_findings or "基于分析结果自动提取"
            },
            "核心洞察": generate_core_insights(business_insights, business_context),
            "深层分析": generate_deep_analysis(business_insights, business_context),
            "趋势判断": analyze_trends_and_patterns(analysis_results, business_context),
            "风险识别": identify_business_risks(business_insights, business_context),
            "机会发现": discover_business_opportunities(business_insights, business_context),
            "洞察评估": insight_assessment,
            "应用指导": generate_insight_application_guide(business_insights)
        }
        
        next_steps = [
            "使用 action_recommender 制定具体行动计划",
            "使用 follow_up_questions 探索更深层问题",
            "使用 data_story_builder 构建数据故事"
        ]
        
        return BaseResponse(
            success=True,
            message="业务洞察生成完成",
            data=insight_report,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"洞察生成过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更详细的分析结果和业务背景"]
        ).dict()


async def action_recommender(
    business_insights: str,
    business_priority: str,
    available_resources: Optional[str] = None,
    time_frame: Optional[str] = "3个月"
) -> Dict[str, Any]:
    """
    行动建议器 - 基于业务洞察提供具体的行动建议
    
    Args:
        business_insights: 业务洞察内容
        business_priority: 业务优先级或目标
        available_resources: 可用资源情况
        time_frame: 实施时间框架
        
    Returns:
        包含行动建议的字典
    """
    
    try:
        # 分析洞察并识别行动机会
        action_opportunities = identify_action_opportunities(business_insights, business_priority)
        
        # 制定分阶段行动计划
        phased_action_plan = create_phased_action_plan(action_opportunities, time_frame, available_resources)
        
        # 评估行动的可行性和影响
        action_evaluation = evaluate_action_feasibility(phased_action_plan, available_resources)
        
        # 构建行动建议报告
        action_report = {
            "洞察分析": {
                "核心洞察": business_insights[:200] + "..." if len(business_insights) > 200 else business_insights,
                "业务优先级": business_priority,
                "资源状况": available_resources or "标准配置",
                "时间框架": time_frame
            },
            "行动机会": action_opportunities,
            "推荐行动": generate_prioritized_actions(phased_action_plan, business_priority),
            "实施计划": create_implementation_plan(phased_action_plan, time_frame),
            "资源配置": plan_resource_allocation(phased_action_plan, available_resources),
            "风险管控": identify_implementation_risks(phased_action_plan),
            "效果预期": estimate_action_outcomes(phased_action_plan, business_insights),
            "监控机制": design_monitoring_system(phased_action_plan)
        }
        
        next_steps = [
            "开始执行高优先级行动",
            "建立实施监控机制",
            "定期评估执行效果并调整计划"
        ]
        
        return BaseResponse(
            success=True,
            message="行动建议制定完成",
            data=action_report,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"行动建议生成过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更具体的业务洞察和优先级"]
        ).dict()


async def follow_up_questions(
    current_analysis: str,
    findings_summary: str,
    business_objective: Optional[str] = None,
    analysis_depth: Optional[str] = "standard"
) -> Dict[str, Any]:
    """
    后续问题生成器 - 基于当前分析结果生成值得进一步探索的问题
    
    Args:
        current_analysis: 当前分析的内容和结果
        findings_summary: 主要发现的摘要
        business_objective: 业务目标
        analysis_depth: 分析深度需求
        
    Returns:
        包含后续问题的字典
    """
    
    try:
        # 分析当前结果并识别知识空白
        knowledge_gaps = identify_knowledge_gaps(current_analysis, findings_summary)
        
        # 生成不同层次的后续问题
        strategic_questions = generate_strategic_questions(findings_summary, business_objective)
        tactical_questions = generate_tactical_questions(current_analysis, findings_summary)
        operational_questions = generate_operational_questions(current_analysis)
        
        # 根据分析深度筛选问题
        filtered_questions = filter_questions_by_depth(
            strategic_questions + tactical_questions + operational_questions,
            analysis_depth
        )
        
        # 构建问题报告
        questions_report = {
            "当前状况": {
                "已完成分析": current_analysis[:150] + "..." if len(current_analysis) > 150 else current_analysis,
                "主要发现": findings_summary,
                "业务目标": business_objective or "通用业务分析",
                "分析深度": analysis_depth
            },
            "知识空白": knowledge_gaps,
            "战略层问题": strategic_questions,
            "战术层问题": tactical_questions,
            "操作层问题": operational_questions,
            "优先级排序": prioritize_questions(filtered_questions, business_objective),
            "探索建议": generate_exploration_suggestions(filtered_questions),
            "分析方法": suggest_analysis_methods_for_questions(filtered_questions)
        }
        
        next_steps = [
            "选择最重要的2-3个问题进行深入分析",
            "收集回答这些问题所需的额外数据",
            "使用适当的分析工具探索选定问题"
        ]
        
        return BaseResponse(
            success=True,
            message="后续问题生成完成",
            data=questions_report,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"问题生成过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更详细的分析结果和发现摘要"]
        ).dict()


async def data_story_builder(
    key_insights: str,
    target_audience: str,
    business_impact: Optional[str] = None,
    story_style: Optional[str] = "business"
) -> Dict[str, Any]:
    """
    数据故事构建器 - 将分析洞察转化为引人入胜的数据故事
    
    Args:
        key_insights: 关键洞察内容
        target_audience: 目标受众
        business_impact: 业务影响描述
        story_style: 故事风格
        
    Returns:
        包含数据故事的字典
    """
    
    try:
        # 分析洞察并提取故事元素
        story_elements = extract_story_elements(key_insights, business_impact)
        
        # 根据受众调整故事结构和语言
        audience_adaptation = adapt_story_for_audience(story_elements, target_audience)
        
        # 构建完整的数据故事
        data_story = build_complete_story(audience_adaptation, story_style)
        
        # 构建故事报告
        story_report = {
            "故事概要": {
                "核心洞察": key_insights[:200] + "..." if len(key_insights) > 200 else key_insights,
                "目标受众": target_audience,
                "业务影响": business_impact or "待评估",
                "故事风格": story_style
            },
            "故事结构": design_story_structure(story_elements, target_audience),
            "完整故事": data_story,
            "关键信息": extract_key_messages(data_story),
            "可视化建议": suggest_visualizations_for_story(story_elements),
            "演示指导": create_presentation_guide(data_story, target_audience),
            "互动元素": design_interactive_elements(story_elements, target_audience),
            "效果预期": estimate_story_impact(data_story, target_audience)
        }
        
        next_steps = [
            "根据建议制作可视化图表",
            "准备故事演示材料",
            "向目标受众展示数据故事"
        ]
        
        return BaseResponse(
            success=True,
            message="数据故事构建完成",
            data=story_report,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"故事构建过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更清晰的关键洞察和受众信息"]
        ).dict()


# 辅助函数实现

def extract_raw_insights(analysis_results: str, key_findings: Optional[str]) -> List[str]:
    """提取原始洞察"""
    insights = []
    
    # 基于关键词识别洞察
    if "增长" in analysis_results or "上升" in analysis_results:
        insights.append("检测到正向增长趋势")
    
    if "下降" in analysis_results or "减少" in analysis_results:
        insights.append("发现下降趋势，需要关注")
    
    if "差异" in analysis_results or "对比" in analysis_results:
        insights.append("不同维度间存在显著差异")
    
    if "季节" in analysis_results or "周期" in analysis_results:
        insights.append("数据表现出周期性规律")
    
    # 结合关键发现
    if key_findings:
        insights.append(f"关键发现表明：{key_findings}")
    
    return insights if insights else ["数据显示出值得关注的业务模式"]


def contextualize_insights(raw_insights: List[str], business_context: str) -> List[Dict[str, str]]:
    """结合业务背景深化洞察"""
    contextualized = []
    
    for insight in raw_insights:
        context_insight = {
            "洞察内容": insight,
            "业务含义": f"在{business_context}背景下，{insight.lower()}",
            "影响程度": evaluate_insight_impact(insight, business_context),
            "可信度": "中等 - 需要进一步验证"
        }
        contextualized.append(context_insight)
    
    return contextualized


def assess_insight_quality(insights: List[Dict], analysis_results: str) -> Dict[str, str]:
    """评估洞察质量"""
    return {
        "数据支撑": "中等 - 基于当前分析结果",
        "业务相关性": "高 - 直接关联业务问题",
        "可操作性": "中等 - 需要进一步分析确定具体行动",
        "创新程度": "标准 - 基于常规分析方法",
        "风险水平": "低 - 洞察相对保守可靠"
    }


def generate_core_insights(insights: List[Dict], business_context: str) -> List[Dict[str, str]]:
    """生成核心洞察"""
    core_insights = []
    
    for i, insight in enumerate(insights[:3], 1):  # 取前3个最重要的洞察
        core_insight = {
            "洞察编号": f"核心洞察 {i}",
            "洞察描述": insight["洞察内容"],
            "业务价值": f"对{business_context}具有重要指导意义",
            "行动指向": "建议制定相应的业务策略",
            "验证建议": "通过额外数据或实验验证"
        }
        core_insights.append(core_insight)
    
    return core_insights


def generate_deep_analysis(insights: List[Dict], business_context: str) -> Dict[str, List[str]]:
    """生成深层分析"""
    return {
        "根本原因分析": [
            "从数据层面看，可能的驱动因素包括...",
            "从业务层面看，影响因素可能是...",
            "从外部环境看，相关因素包括..."
        ],
        "关联性分析": [
            "当前发现与历史趋势的关联",
            "不同业务指标间的相互影响",
            "内外部因素的综合作用"
        ],
        "影响范围评估": [
            "对核心业务指标的影响程度",
            "对不同客户群体的影响差异",
            "对未来发展的潜在影响"
        ]
    }


def analyze_trends_and_patterns(analysis_results: str, business_context: str) -> Dict[str, str]:
    """分析趋势和模式"""
    return {
        "短期趋势": "基于近期数据的趋势判断",
        "中期展望": "结合业务周期的中期预测",
        "长期影响": "对长期业务发展的影响评估",
        "关键拐点": "需要重点关注的变化节点",
        "稳定因素": "相对稳定不变的业务要素"
    }


def identify_business_risks(insights: List[Dict], business_context: str) -> List[Dict[str, str]]:
    """识别业务风险"""
    return [
        {
            "风险类型": "趋势风险",
            "风险描述": "当前趋势可能带来的负面影响",
            "风险等级": "中等",
            "应对建议": "密切监控关键指标变化"
        },
        {
            "风险类型": "决策风险",
            "风险描述": "基于当前洞察做决策的不确定性",
            "风险等级": "低",
            "应对建议": "通过更多数据验证决策依据"
        }
    ]


def discover_business_opportunities(insights: List[Dict], business_context: str) -> List[Dict[str, str]]:
    """发现业务机会"""
    return [
        {
            "机会类型": "优化机会",
            "机会描述": "基于数据洞察的业务优化空间",
            "价值评估": "中等 - 具有一定改进潜力",
            "实施难度": "中等",
            "建议行动": "制定具体的优化计划"
        },
        {
            "机会类型": "创新机会",
            "机会描述": "数据揭示的新的业务可能性",
            "价值评估": "高 - 可能带来突破性改进",
            "实施难度": "高",
            "建议行动": "进行小规模试点验证"
        }
    ]


def generate_insight_application_guide(insights: List[Dict]) -> List[str]:
    """生成洞察应用指导"""
    return [
        "将洞察转化为具体的业务策略",
        "建立基于洞察的决策框架",
        "设计实验验证洞察的准确性",
        "建立持续监控洞察变化的机制",
        "与团队分享洞察并达成共识"
    ]


def identify_action_opportunities(insights: str, priority: str) -> List[Dict[str, str]]:
    """识别行动机会"""
    opportunities = []
    
    # 基于洞察内容识别机会
    if "增长" in insights:
        opportunities.append({
            "机会": "增长加速",
            "描述": "基于增长趋势，进一步扩大优势",
            "类型": "扩张型"
        })
    
    if "问题" in insights or "下降" in insights:
        opportunities.append({
            "机会": "问题解决",
            "描述": "针对发现的问题制定解决方案",
            "类型": "修复型"
        })
    
    if "差异" in insights:
        opportunities.append({
            "机会": "差异利用",
            "描述": "利用不同维度的差异优化配置",
            "类型": "优化型"
        })
    
    # 根据优先级调整机会
    if "收入" in priority or "销售" in priority:
        opportunities.append({
            "机会": "收入提升",
            "描述": "重点关注收入相关的改进机会",
            "类型": "收入型"
        })
    
    return opportunities if opportunities else [{
        "机会": "常规优化",
        "描述": "基于分析结果的常规业务优化",
        "类型": "通用型"
    }]


def create_phased_action_plan(opportunities: List[Dict], time_frame: str, resources: Optional[str]) -> Dict[str, List[Dict]]:
    """制定分阶段行动计划"""
    if "1个月" in time_frame or "急" in time_frame:
        phases = ["第1周", "第2-4周"]
    elif "3个月" in time_frame:
        phases = ["第1个月", "第2个月", "第3个月"]
    else:
        phases = ["短期（1-2个月）", "中期（3-6个月）", "长期（6个月以上）"]
    
    plan = {}
    for i, phase in enumerate(phases):
        phase_actions = []
        for j, opp in enumerate(opportunities):
            if j % len(phases) == i:  # 简单分配逻辑
                action = {
                    "行动": f"实施{opp['机会']}计划",
                    "目标": opp['描述'],
                    "优先级": "高" if i == 0 else "中",
                    "预期成果": f"在{opp['类型']}方面取得改进"
                }
                phase_actions.append(action)
        plan[phase] = phase_actions
    
    return plan


def evaluate_action_feasibility(plan: Dict, resources: Optional[str]) -> Dict[str, str]:
    """评估行动可行性"""
    return {
        "资源充足度": "中等 - 需要合理配置现有资源",
        "技术可行性": "高 - 基于现有能力可以实施",
        "时间合理性": "中等 - 时间安排相对紧凑",
        "风险可控性": "高 - 风险在可控范围内",
        "预期成功率": "70-80% - 具有较高成功可能性"
    }


def generate_prioritized_actions(plan: Dict, priority: str) -> List[Dict[str, str]]:
    """生成优先级行动"""
    all_actions = []
    for phase, actions in plan.items():
        for action in actions:
            action_item = {
                "行动名称": action["行动"],
                "实施阶段": phase,
                "优先级": action["优先级"],
                "预期收益": evaluate_action_benefit(action, priority),
                "实施难度": "中等"
            }
            all_actions.append(action_item)
    
    # 按优先级排序
    return sorted(all_actions, key=lambda x: x["优先级"], reverse=True)


def create_implementation_plan(plan: Dict, time_frame: str) -> List[Dict[str, str]]:
    """创建实施计划"""
    implementation = []
    
    for phase, actions in plan.items():
        for action in actions:
            impl_item = {
                "时间节点": phase,
                "具体行动": action["行动"],
                "责任分工": "指定负责人和协作团队",
                "关键里程碑": "设定可衡量的阶段目标",
                "成功标准": action.get("预期成果", "达到预期目标")
            }
            implementation.append(impl_item)
    
    return implementation


def plan_resource_allocation(plan: Dict, resources: Optional[str]) -> Dict[str, List[str]]:
    """规划资源配置"""
    return {
        "人力资源": [
            "指定项目负责人和核心团队",
            "明确各阶段的人员投入",
            "安排必要的培训和支持"
        ],
        "技术资源": [
            "确保必要的工具和系统支持",
            "准备数据分析和监控工具",
            "建立实施效果追踪机制"
        ],
        "财务资源": [
            "预算各阶段的资金需求",
            "设定投资回报预期",
            "建立成本控制机制"
        ],
        "时间资源": [
            "合理安排项目时间表",
            "预留缓冲时间应对意外",
            "设定关键节点检查机制"
        ]
    }


def identify_implementation_risks(plan: Dict) -> List[Dict[str, str]]:
    """识别实施风险"""
    return [
        {
            "风险": "执行偏差",
            "描述": "实际执行与计划存在偏差",
            "概率": "中等",
            "影响": "中等",
            "应对": "建立定期检查和调整机制"
        },
        {
            "风险": "资源不足",
            "描述": "实施过程中资源配置不够",
            "概率": "低",
            "影响": "中等",
            "应对": "提前识别和预留备用资源"
        },
        {
            "风险": "外部变化",
            "描述": "外部环境变化影响实施效果",
            "概率": "中等",
            "影响": "高",
            "应对": "保持灵活性，及时调整策略"
        }
    ]


def estimate_action_outcomes(plan: Dict, insights: str) -> Dict[str, str]:
    """估算行动结果"""
    return {
        "短期效果": "1-2个月内可见初步改进",
        "中期收益": "3-6个月内达到预期目标",
        "长期价值": "6个月以上形成可持续改进",
        "量化指标": "关键指标改进10-30%",
        "定性收益": "提升团队能力和决策质量"
    }


def design_monitoring_system(plan: Dict) -> Dict[str, List[str]]:
    """设计监控机制"""
    return {
        "关键指标": [
            "定义核心成功指标",
            "设定预警阈值",
            "建立指标收集机制"
        ],
        "监控频率": [
            "每周检查执行进度",
            "每月评估阶段成果",
            "每季度全面回顾调整"
        ],
        "反馈机制": [
            "建立团队反馈渠道",
            "收集利益相关者意见",
            "定期举行回顾会议"
        ],
        "调整机制": [
            "设定调整触发条件",
            "明确调整决策流程",
            "保持计划灵活性"
        ]
    }


def identify_knowledge_gaps(analysis: str, findings: str) -> List[Dict[str, str]]:
    """识别知识空白"""
    gaps = []
    
    # 基于常见分析维度识别空白
    analysis_dimensions = ["时间", "地区", "产品", "客户", "渠道"]
    
    for dimension in analysis_dimensions:
        if dimension not in analysis.lower():
            gaps.append({
                "空白领域": f"{dimension}维度分析",
                "具体描述": f"缺少从{dimension}角度的深入分析",
                "重要程度": "中等",
                "建议补充": f"收集{dimension}相关数据进行补充分析"
            })
    
    # 基于发现识别需要深入的领域
    if "原因" not in findings.lower():
        gaps.append({
            "空白领域": "根本原因分析",
            "具体描述": "未深入分析现象背后的根本原因",
            "重要程度": "高",
            "建议补充": "进行因果关系分析"
        })
    
    return gaps[:3]  # 返回前3个最重要的空白


def generate_strategic_questions(findings: str, objective: Optional[str]) -> List[str]:
    """生成战略层问题"""
    questions = [
        "这些发现对我们的长期战略目标有什么影响？",
        "我们应该如何调整业务策略来应对这些趋势？",
        "这些洞察揭示了哪些新的市场机会？",
        "我们的核心竞争优势在这些发现中如何体现？"
    ]
    
    if objective:
        questions.append(f"基于这些发现，我们如何更好地实现{objective}？")
    
    return questions


def generate_tactical_questions(analysis: str, findings: str) -> List[str]:
    """生成战术层问题"""
    return [
        "哪些具体的业务环节需要立即优化？",
        "我们应该优先关注哪些客户群体或产品线？",
        "资源应该如何重新配置以支持这些发现？",
        "我们需要建立哪些新的业务流程或机制？",
        "如何衡量和监控改进措施的效果？"
    ]


def generate_operational_questions(analysis: str) -> List[str]:
    """生成操作层问题"""
    return [
        "具体的执行步骤应该是什么？",
        "需要哪些工具和资源来支持实施？",
        "谁应该负责各项改进措施的执行？",
        "如何确保团队理解并遵循新的操作方式？",
        "实施过程中可能遇到哪些障碍，如何克服？"
    ]


def filter_questions_by_depth(questions: List[str], depth: str) -> List[str]:
    """根据深度筛选问题"""
    if depth == "shallow":
        return questions[:3]
    elif depth == "deep":
        return questions
    else:  # standard
        return questions[:5]


def prioritize_questions(questions: List[str], objective: Optional[str]) -> List[Dict[str, str]]:
    """问题优先级排序"""
    prioritized = []
    
    for i, question in enumerate(questions[:5]):
        priority = "高" if i < 2 else "中" if i < 4 else "低"
        urgency = "紧急" if "立即" in question or "优先" in question else "一般"
        
        prioritized.append({
            "问题": question,
            "优先级": priority,
            "紧急程度": urgency,
            "建议时间": "1-2周" if priority == "高" else "2-4周"
        })
    
    return prioritized


def generate_exploration_suggestions(questions: List[str]) -> List[str]:
    """生成探索建议"""
    return [
        "从最重要的问题开始，逐步深入分析",
        "结合定量和定性方法探索问题",
        "寻找外部基准和最佳实践参考",
        "与相关利益相关者讨论和验证",
        "设计小规模实验验证假设"
    ]


def suggest_analysis_methods_for_questions(questions: List[str]) -> Dict[str, str]:
    """为问题建议分析方法"""
    return {
        "趋势分析": "使用时间序列分析探索变化趋势",
        "对比分析": "通过基准对比找出差异和机会",
        "相关性分析": "探索不同因素间的关联关系",
        "细分分析": "深入分析不同细分维度的表现",
        "实验设计": "通过A/B测试验证假设"
    }


def extract_story_elements(insights: str, impact: Optional[str]) -> Dict[str, str]:
    """提取故事元素"""
    return {
        "背景": "业务面临的挑战和机遇",
        "问题": "需要解决的核心问题",
        "发现": insights[:100] + "..." if len(insights) > 100 else insights,
        "转折": "数据揭示的关键洞察",
        "解决方案": "基于洞察的行动建议",
        "结果": impact or "预期的业务改进"
    }


def adapt_story_for_audience(elements: Dict, audience: str) -> Dict[str, str]:
    """根据受众调整故事"""
    if audience == "management":
        return {
            "重点": "业务影响和投资回报",
            "语言": "简洁直接，重点突出",
            "结构": "结论先行，数据支撑",
            "时长": "5-10分钟精简版"
        }
    elif audience == "technical":
        return {
            "重点": "分析方法和数据细节",
            "语言": "专业术语，逻辑严密",
            "结构": "问题-方法-结果-结论",
            "时长": "15-20分钟详细版"
        }
    else:  # general
        return {
            "重点": "易懂的发现和实用建议",
            "语言": "通俗易懂，避免专业术语",
            "结构": "故事化叙述，循序渐进",
            "时长": "10-15分钟标准版"
        }


def build_complete_story(adaptation: Dict, style: str) -> Dict[str, str]:
    """构建完整故事"""
    return {
        "开场": "用引人入胜的方式介绍背景和问题",
        "发展": "逐步展示数据发现和分析过程",
        "高潮": "揭示最重要的洞察和转折点",
        "结局": "提出解决方案和预期结果",
        "总结": "重申关键信息和行动号召"
    }


def design_story_structure(elements: Dict, audience: str) -> List[Dict[str, str]]:
    """设计故事结构"""
    return [
        {"环节": "引入", "内容": "设定背景，引出问题", "时间": "1-2分钟"},
        {"环节": "探索", "内容": "展示分析过程和发现", "时间": "3-5分钟"},
        {"环节": "洞察", "内容": "揭示关键洞察", "时间": "2-3分钟"},
        {"环节": "行动", "内容": "提出解决方案", "时间": "2-3分钟"},
        {"环节": "展望", "内容": "描绘未来愿景", "时间": "1-2分钟"}
    ]


def extract_key_messages(story: Dict) -> List[str]:
    """提取关键信息"""
    return [
        "数据揭示了重要的业务洞察",
        "这些发现对业务决策具有指导意义",
        "建议采取具体的改进行动",
        "预期能够带来可衡量的业务价值"
    ]


def suggest_visualizations_for_story(elements: Dict) -> List[Dict[str, str]]:
    """为故事建议可视化"""
    return [
        {"类型": "趋势图", "用途": "展示关键指标变化", "位置": "发展阶段"},
        {"类型": "对比图", "用途": "突出重要差异", "位置": "洞察阶段"},
        {"类型": "流程图", "用途": "说明解决方案", "位置": "行动阶段"},
        {"类型": "预测图", "用途": "展示未来预期", "位置": "展望阶段"}
    ]


def create_presentation_guide(story: Dict, audience: str) -> List[str]:
    """创建演示指导"""
    return [
        "开始时建立与听众的连接",
        "使用具体的数字和案例支持观点",
        "在关键节点暂停，让听众消化信息",
        "用提问的方式引导听众思考",
        "结束时明确下一步行动",
        "准备回答可能的问题和质疑"
    ]


def design_interactive_elements(elements: Dict, audience: str) -> List[str]:
    """设计互动元素"""
    return [
        "在开场提出引发思考的问题",
        "在关键发现处征求听众的看法",
        "邀请听众分享类似的经验",
        "在解决方案阶段讨论可行性",
        "结束时收集反馈和建议"
    ]


def estimate_story_impact(story: Dict, audience: str) -> Dict[str, str]:
    """估算故事影响"""
    return {
        "理解程度": "高 - 故事结构清晰易懂",
        "记忆程度": "中等 - 关键信息容易记住",
        "说服力": "中等 - 数据支撑的论证有说服力",
        "行动激发": "中等 - 能够激发听众采取行动",
        "传播价值": "高 - 容易向他人分享和传播"
    }


# 辅助函数

def evaluate_insight_impact(insight: str, context: str) -> str:
    """评估洞察影响程度"""
    if "增长" in insight or "机会" in insight:
        return "积极 - 有利于业务发展"
    elif "下降" in insight or "问题" in insight:
        return "警示 - 需要重点关注"
    else:
        return "中性 - 需要进一步分析"


def evaluate_action_benefit(action: Dict, priority: str) -> str:
    """评估行动收益"""
    if priority in action.get("目标", ""):
        return "高 - 直接支持核心目标"
    else:
        return "中等 - 有助于整体改进" 
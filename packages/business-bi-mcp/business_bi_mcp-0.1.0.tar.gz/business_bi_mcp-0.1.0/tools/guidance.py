"""
数据收集与结果解读工具组
包含数据收集指导和结果解读器
"""

from typing import Dict, List, Any, Optional
from core.models import BaseResponse, DataAccessLevel, DataAvailability


async def data_collection_guide(
    analysis_type: str,
    business_system: Optional[str] = None,
    data_access_level: Optional[str] = "employee",
    time_constraint: Optional[str] = None
) -> Dict[str, Any]:
    """
    数据收集指导 - 指导用户如何收集和准备分析所需的数据
    
    Args:
        analysis_type: 要进行的分析类型
        business_system: 现有的业务系统
        data_access_level: 数据获取权限级别
        time_constraint: 时间要求
        
    Returns:
        包含数据收集指导的字典
    """
    
    try:
        # 根据分析类型确定数据需求
        data_requirements = get_data_requirements_by_analysis_type(analysis_type)
        
        # 根据权限级别制定收集策略
        collection_strategy = get_collection_strategy_by_access_level(data_access_level)
        
        # 构建数据收集指导
        collection_guide = {
            "分析需求": {
                "分析类型": analysis_type,
                "业务系统": business_system or "待确认",
                "权限级别": data_access_level,
                "时间要求": time_constraint or "正常进度"
            },
            "数据清单": data_requirements,
            "获取方法": generate_data_acquisition_methods(business_system, data_access_level),
            "整理步骤": generate_data_processing_steps(analysis_type),
            "质量检查": generate_data_quality_checklist(),
            "常见问题": get_common_data_issues_and_solutions(),
            "模板工具": provide_data_templates(analysis_type),
            "时间规划": estimate_data_collection_time(time_constraint, data_access_level)
        }
        
        next_steps = [
            "开始按清单收集数据",
            "使用模板整理数据格式",
            "完成后使用 result_interpreter 解读结果"
        ]
        
        return BaseResponse(
            success=True,
            message="数据收集指导生成完成",
            data=collection_guide,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"生成指导过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更具体的分析需求"]
        ).dict()


async def result_interpreter(
    analysis_results: str,
    analysis_method: str,
    business_context: Optional[str] = None,
    target_audience: Optional[str] = "management"
) -> Dict[str, Any]:
    """
    结果解读器 - 帮助用户理解和解释分析结果
    
    Args:
        analysis_results: 分析得到的结果数据或图表
        analysis_method: 使用的分析方法
        business_context: 业务背景信息
        target_audience: 目标受众
        
    Returns:
        包含结果解读的字典
    """
    
    try:
        # 解析分析结果
        result_analysis = parse_analysis_results(analysis_results, analysis_method)
        
        # 生成业务解读
        business_interpretation = generate_business_interpretation(
            result_analysis, business_context, target_audience
        )
        
        # 构建解读结果
        interpretation_guide = {
            "结果概览": {
                "分析方法": analysis_method,
                "主要发现": extract_key_findings(analysis_results),
                "数据质量": assess_result_reliability(analysis_results),
                "置信程度": evaluate_confidence_level(analysis_results, analysis_method)
            },
            "深度解读": business_interpretation,
            "关键洞察": generate_key_insights(result_analysis, business_context),
            "对比分析": generate_comparative_analysis(result_analysis),
            "风险提示": identify_interpretation_risks(analysis_method, business_context),
            "沟通建议": generate_communication_recommendations(target_audience),
            "后续行动": suggest_follow_up_actions(result_analysis, business_context)
        }
        
        next_steps = [
            "使用 insight_generator 提取更深层洞察",
            "使用 action_recommender 制定行动计划",
            "准备向相关人员汇报结果"
        ]
        
        return BaseResponse(
            success=True,
            message="结果解读完成",
            data=interpretation_guide,
            suggested_next_steps=next_steps
        ).dict()
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"结果解读过程中出现错误：{str(e)}",
            suggested_next_steps=["请提供更完整的分析结果信息"]
        ).dict()


# 辅助函数实现

def get_data_requirements_by_analysis_type(analysis_type: str) -> Dict[str, List[str]]:
    """根据分析类型获取数据需求"""
    
    analysis_data_map = {
        "销售分析": {
            "核心数据": [
                "销售交易记录（时间、金额、产品、客户）",
                "产品信息（类别、价格、成本）",
                "客户信息（地区、类型、购买历史）",
                "销售人员信息（团队、区域分工）"
            ],
            "补充数据": [
                "市场活动记录（促销、广告投入）",
                "竞争对手价格信息",
                "季节性因素数据",
                "宏观经济指标"
            ],
            "时间范围": "建议收集至少12个月的历史数据"
        },
        "客户分析": {
            "核心数据": [
                "客户基本信息（注册时间、地区、类型）",
                "购买行为数据（频次、金额、产品偏好）",
                "客户生命周期数据（获取、活跃、流失状态）",
                "客户服务记录（投诉、满意度、问题类型）"
            ],
            "补充数据": [
                "客户反馈和评价",
                "市场研究和调研数据",
                "竞争对手客户策略",
                "行业客户行为基准"
            ],
            "时间范围": "建议收集至少6个月的客户行为数据"
        },
        "运营分析": {
            "核心数据": [
                "运营流程数据（效率、质量、成本）",
                "人员配置数据（工作量、绩效、成本）",
                "设备使用数据（利用率、故障率、维护成本）",
                "库存管理数据（周转率、缺货率、持有成本）"
            ],
            "补充数据": [
                "行业基准数据",
                "最佳实践案例",
                "外部服务商数据",
                "政策法规变化"
            ],
            "时间范围": "建议收集至少3个月的运营数据"
        }
    }
    
    # 默认通用数据需求
    default_requirements = {
        "核心数据": [
            "与分析目标直接相关的关键指标数据",
            "时间序列数据用于趋势分析",
            "分类维度数据用于对比分析"
        ],
        "补充数据": [
            "行业基准或竞争对手数据",
            "外部环境因素数据",
            "历史背景和事件数据"
        ],
        "时间范围": "建议收集3-6个月的相关数据"
    }
    
    return analysis_data_map.get(analysis_type, default_requirements)


def get_collection_strategy_by_access_level(access_level: str) -> Dict[str, List[str]]:
    """根据权限级别制定收集策略"""
    
    strategies = {
        "owner": {
            "直接获取": [
                "从业务系统直接导出完整数据",
                "访问所有历史记录和详细信息",
                "获取敏感数据和财务信息",
                "调取系统日志和操作记录"
            ],
            "协调资源": [
                "安排技术人员协助数据提取",
                "协调各部门提供专业数据",
                "外部供应商和合作伙伴数据",
                "购买第三方数据和报告"
            ]
        },
        "manager": {
            "直接获取": [
                "获取部门内相关业务数据",
                "查看管理报表和汇总数据",
                "访问团队绩效和操作数据",
                "获取客户反馈和投诉信息"
            ],
            "申请协助": [
                "向IT部门申请数据导出",
                "请其他部门提供协作数据",
                "申请查看更高级别的数据",
                "寻求外部数据支持"
            ]
        },
        "employee": {
            "可获取数据": [
                "个人工作范围内的数据",
                "公开的业务报表和统计",
                "客户交互和服务记录",
                "自己负责的项目数据"
            ],
            "需要协助": [
                "向直接主管申请更多数据权限",
                "请同事协助提供相关数据",
                "通过正式流程申请敏感数据",
                "利用公开渠道获取行业数据"
            ]
        },
        "limited": {
            "基础数据": [
                "公开的业务概况和统计",
                "行业公开报告和数据",
                "网络公开信息和资料",
                "用户调研和问卷数据"
            ],
            "替代方案": [
                "使用抽样数据进行分析",
                "通过问卷收集一手数据",
                "利用公开数据推断趋势",
                "寻找代理指标进行分析"
            ]
        }
    }
    
    return strategies.get(access_level, strategies["employee"])


def generate_data_acquisition_methods(business_system: Optional[str], access_level: str) -> Dict[str, List[str]]:
    """生成数据获取方法"""
    
    methods = {
        "系统导出": [
            "ERP系统：财务、库存、销售数据",
            "CRM系统：客户信息、销售线索、服务记录",
            "POS系统：交易明细、商品信息、支付数据",
            "OA系统：人员信息、流程数据、审批记录"
        ],
        "手工收集": [
            "Excel表格整理现有数据",
            "问卷调研收集客户反馈",
            "实地观察记录运营数据",
            "访谈收集定性信息"
        ],
        "第三方获取": [
            "购买行业研究报告",
            "获取政府公开统计数据",
            "收集竞争对手公开信息",
            "利用网络爬虫获取数据"
        ],
        "合作获取": [
            "与供应商交换数据",
            "与客户合作收集使用数据",
            "行业协会共享基准数据",
            "咨询公司提供专业数据"
        ]
    }
    
    return methods


def generate_data_processing_steps(analysis_type: str) -> List[Dict[str, str]]:
    """生成数据处理步骤"""
    
    return [
        {
            "步骤": "数据收集",
            "说明": "按照清单收集所需的各类数据",
            "要点": "确保数据完整性和时效性",
            "工具": "Excel、数据库导出工具"
        },
        {
            "步骤": "数据清理",
            "说明": "检查和处理数据质量问题",
            "要点": "处理缺失值、异常值、重复值",
            "工具": "Excel数据验证、Python pandas"
        },
        {
            "步骤": "数据标准化",
            "说明": "统一数据格式和标准",
            "要点": "统一时间格式、单位、编码方式",
            "工具": "Excel格式化、数据转换脚本"
        },
        {
            "步骤": "数据整合",
            "说明": "将不同来源的数据合并",
            "要点": "建立统一的主键和关联关系",
            "工具": "Excel VLOOKUP、数据库JOIN"
        },
        {
            "步骤": "数据验证",
            "说明": "验证整理后数据的准确性",
            "要点": "逻辑检查、汇总核对、抽样验证",
            "工具": "Excel透视表、统计汇总"
        }
    ]


def generate_data_quality_checklist() -> Dict[str, List[str]]:
    """生成数据质量检查清单"""
    
    return {
        "完整性检查": [
            "检查是否有缺失的时间段",
            "确认所有必需字段都有数据",
            "验证数据覆盖范围是否充分",
            "检查关键维度是否完整"
        ],
        "准确性检查": [
            "核对关键数值的正确性",
            "验证计算公式和逻辑",
            "与原始单据进行抽样对比",
            "检查数据录入错误"
        ],
        "一致性检查": [
            "统一时间格式和时区",
            "标准化产品名称和编码",
            "统一金额单位和币种",
            "保持分类标准的一致性"
        ],
        "合理性检查": [
            "识别明显的异常值",
            "检查数据变化的合理性",
            "验证业务逻辑的正确性",
            "确认数据符合业务规则"
        ]
    }


def get_common_data_issues_and_solutions() -> List[Dict[str, str]]:
    """获取常见数据问题及解决方案"""
    
    return [
        {
            "问题": "数据缺失",
            "表现": "某些时间段或维度的数据为空",
            "解决": "寻找替代数据源、使用插值方法、或调整分析范围",
            "预防": "建立数据收集的标准流程和检查机制"
        },
        {
            "问题": "格式不统一",
            "表现": "相同数据在不同系统中格式不同",
            "解决": "制定统一的数据标准、使用转换工具",
            "预防": "建立企业级数据标准和规范"
        },
        {
            "问题": "数据重复",
            "表现": "同一记录在多个地方出现",
            "解决": "使用去重工具、建立唯一标识符",
            "预防": "设计合理的数据录入流程"
        },
        {
            "问题": "时效性差",
            "表现": "数据更新不及时，存在滞后",
            "解决": "建立实时或定期更新机制",
            "预防": "设计自动化的数据收集系统"
        },
        {
            "问题": "权限限制",
            "表现": "无法获取所需的敏感或高级数据",
            "解决": "申请临时权限、使用脱敏数据、寻找代理指标",
            "预防": "提前规划数据需求和权限申请"
        }
    ]


def provide_data_templates(analysis_type: str) -> Dict[str, str]:
    """提供数据模板"""
    
    templates = {
        "销售数据模板": "包含日期、产品、客户、金额、数量等标准字段的Excel模板",
        "客户数据模板": "包含客户ID、注册时间、属性、行为数据的标准格式",
        "运营数据模板": "包含时间、流程、效率、成本等运营指标的记录格式",
        "财务数据模板": "包含会计期间、科目、金额、部门等财务数据格式",
        "通用分析模板": "适用于各类业务分析的基础数据整理模板"
    }
    
    return {
        "推荐模板": templates.get(f"{analysis_type}模板", templates["通用分析模板"]),
        "获取方式": "可以从企业内部系统导出，或使用标准的Excel模板",
        "自定义指导": "根据具体业务需求，在标准模板基础上增加必要字段",
        "质量要求": "确保数据格式统一、字段完整、逻辑正确"
    }


def estimate_data_collection_time(time_constraint: Optional[str], access_level: str) -> Dict[str, str]:
    """估算数据收集时间"""
    
    base_time = {
        "owner": {"collection": "1-2天", "processing": "1-2天", "total": "3-4天"},
        "manager": {"collection": "2-3天", "processing": "2-3天", "total": "5-6天"}, 
        "employee": {"collection": "3-5天", "processing": "2-3天", "total": "1周"},
        "limited": {"collection": "5-7天", "processing": "3-4天", "total": "1.5-2周"}
    }
    
    time_estimate = base_time.get(access_level, base_time["employee"])
    
    if time_constraint and ("急" in time_constraint or "快" in time_constraint):
        return {
            "数据收集": f"{time_estimate['collection']}（加急）",
            "数据处理": f"{time_estimate['processing']}（简化流程）",
            "总计时间": f"{time_estimate['total']}（优先处理）",
            "加急建议": "重点收集核心数据，简化非关键环节"
        }
    
    return {
        "数据收集": time_estimate["collection"],
        "数据处理": time_estimate["processing"],
        "总计时间": time_estimate["total"],
        "并行建议": "数据收集和处理可以部分并行进行"
    }


def parse_analysis_results(results: str, method: str) -> Dict[str, Any]:
    """解析分析结果"""
    
    # 简化的结果解析逻辑
    parsed_results = {
        "数据类型": "定量分析" if any(char.isdigit() for char in results) else "定性分析",
        "结果规模": "大量数据" if len(results) > 500 else "中等数据" if len(results) > 100 else "简单数据",
        "包含图表": "是" if any(word in results for word in ["图", "表", "chart"]) else "否",
        "关键数值": extract_numbers_from_text(results),
        "趋势描述": extract_trends_from_text(results),
        "对比信息": extract_comparisons_from_text(results)
    }
    
    return parsed_results


def generate_business_interpretation(result_analysis: Dict, business_context: Optional[str], audience: str) -> Dict[str, Any]:
    """生成业务解读"""
    
    interpretation = {
        "管理层视角": {
            "核心结论": "基于分析结果的主要业务结论",
            "影响评估": "对业务目标和KPI的影响程度",
            "决策建议": "需要做出的关键决策和选择",
            "资源需求": "实施改进所需的资源投入"
        },
        "操作层视角": {
            "具体发现": "详细的数据发现和现象描述",
            "原因分析": "导致当前结果的可能原因",
            "改进机会": "可以优化的具体环节和方法",
            "实施步骤": "具体的执行步骤和时间安排"
        },
        "技术层视角": {
            "数据质量": "分析数据的可靠性和局限性",
            "方法说明": "使用的分析方法和适用条件",
            "置信水平": "结果的可信程度和不确定性",
            "进一步分析": "需要补充的分析和验证"
        }
    }
    
    # 根据受众调整重点
    if audience == "management":
        return {key: interpretation[key] for key in ["管理层视角", "操作层视角"]}
    elif audience == "colleagues":
        return {key: interpretation[key] for key in ["操作层视角", "技术层视角"]}
    else:
        return interpretation


def extract_key_findings(results: str) -> List[str]:
    """提取关键发现"""
    
    # 简化的关键发现提取
    findings = []
    
    if "上升" in results or "增长" in results or "提高" in results:
        findings.append("检测到正向趋势变化")
    
    if "下降" in results or "减少" in results or "降低" in results:
        findings.append("检测到负向趋势变化")
    
    if "%" in results:
        findings.append("包含百分比数据，适合对比分析")
    
    if not findings:
        findings = ["结果包含重要的业务信息，需要进一步解读"]
    
    return findings


def assess_result_reliability(results: str) -> str:
    """评估结果可靠性"""
    
    if len(results) > 1000:
        return "高 - 数据样本充足，结果相对可靠"
    elif len(results) > 200:
        return "中 - 数据适中，结果基本可靠"
    else:
        return "低 - 数据较少，建议增加样本"


def evaluate_confidence_level(results: str, method: str) -> str:
    """评估置信水平"""
    
    confidence_factors = {
        "趋势分析": "高 - 时间序列分析结果较为稳定",
        "对比分析": "中 - 依赖于对比基准的合理性",
        "相关性分析": "中 - 需要注意相关性不等于因果性",
        "回归分析": "高 - 统计模型结果相对可信"
    }
    
    return confidence_factors.get(method, "中 - 结果需要结合业务经验判断")


def generate_key_insights(result_analysis: Dict, business_context: Optional[str]) -> List[str]:
    """生成关键洞察"""
    
    insights = [
        "数据反映了当前业务的真实状况",
        "结果与预期的差异值得深入分析",
        "发现的趋势具有重要的指导意义",
        "建议结合外部环境因素进行综合判断"
    ]
    
    # 根据业务背景调整洞察
    if business_context:
        if "竞争" in business_context:
            insights.append("需要考虑竞争环境对结果的影响")
        if "季节" in business_context:
            insights.append("注意季节性因素对数据的影响")
    
    return insights


def generate_comparative_analysis(result_analysis: Dict) -> Dict[str, str]:
    """生成对比分析"""
    
    return {
        "历史对比": "与历史同期数据的对比情况",
        "行业对比": "与行业平均水平的对比位置",
        "竞品对比": "与主要竞争对手的对比优势",
        "目标对比": "与预设目标的完成情况对比"
    }


def identify_interpretation_risks(method: str, business_context: Optional[str]) -> List[str]:
    """识别解读风险"""
    
    return [
        "避免过度解读：不要从有限数据得出过于绝对的结论",
        "考虑偶然性：单次数据可能存在偶然因素影响",
        "注意因果关系：相关性不等于因果关系",
        "结合定性分析：数据分析需要结合业务经验和直觉",
        "持续验证：重要结论需要通过后续数据验证"
    ]


def generate_communication_recommendations(audience: str) -> Dict[str, List[str]]:
    """生成沟通建议"""
    
    recommendations = {
        "management": [
            "重点突出业务影响和决策建议",
            "使用简洁的图表和关键数字",
            "提供明确的行动方案和时间表",
            "准备回答投资回报和风险问题"
        ],
        "colleagues": [
            "详细说明分析过程和方法",
            "分享具体的操作建议和改进点",
            "讨论实施中可能遇到的问题",
            "建立后续协作和跟进机制"
        ],
        "clients": [
            "重点展示对客户的价值和收益",
            "使用通俗易懂的语言和案例",
            "提供具体的服务改进措施",
            "建立反馈和持续优化机制"
        ]
    }
    
    return {
        "沟通要点": recommendations.get(audience, recommendations["colleagues"]),
        "表达技巧": [
            "用故事化的方式描述数据发现",
            "结合具体案例说明抽象概念",
            "使用对比和类比帮助理解",
            "留出充分时间回答问题和讨论"
        ]
    }


def suggest_follow_up_actions(result_analysis: Dict, business_context: Optional[str]) -> List[Dict[str, str]]:
    """建议后续行动"""
    
    return [
        {
            "行动": "深化分析",
            "描述": "针对关键发现进行更深入的原因分析",
            "优先级": "高",
            "时间": "1-2周"
        },
        {
            "行动": "验证结果",
            "描述": "通过其他数据源或方法验证分析结论",
            "优先级": "中",
            "时间": "1周"
        },
        {
            "行动": "制定计划",
            "描述": "基于分析结果制定具体的改进计划",
            "优先级": "高",
            "时间": "2-3天"
        },
        {
            "行动": "监控跟踪",
            "描述": "建立关键指标的持续监控机制",
            "优先级": "中",
            "时间": "1周"
        }
    ]


# 辅助工具函数

def extract_numbers_from_text(text: str) -> List[str]:
    """从文本中提取数字"""
    import re
    numbers = re.findall(r'\d+\.?\d*', text)
    return numbers[:5]  # 返回前5个数字


def extract_trends_from_text(text: str) -> List[str]:
    """从文本中提取趋势描述"""
    trend_keywords = ["上升", "下降", "增长", "减少", "稳定", "波动"]
    trends = [keyword for keyword in trend_keywords if keyword in text]
    return trends


def extract_comparisons_from_text(text: str) -> List[str]:
    """从文本中提取对比信息"""
    comparison_keywords = ["高于", "低于", "相比", "对比", "超过", "不及"]
    comparisons = [keyword for keyword in comparison_keywords if keyword in text]
    return comparisons 
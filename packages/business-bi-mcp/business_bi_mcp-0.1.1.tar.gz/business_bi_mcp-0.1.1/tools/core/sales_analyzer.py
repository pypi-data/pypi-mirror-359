"""
销售额对比分析工具
专门处理销售额对比分析的完整流程，集成数据查询、分析、洞察生成和行动建议
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

# 导入需要的工具 - 使用新的模块化路径
from tools.database import database_schema_explorer, sql_query_executor
from tools.insights import insight_generator, action_recommender


async def sales_comparison_analyzer(
    question: str,
    time_period_1: Optional[str] = None,
    time_period_2: Optional[str] = None,
    comparison_type: str = "week_over_week",
    business_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    销售额对比分析器 - 完整的销售对比分析流程
    
    Args:
        question: 用户提出的问题，如"最近一周的销售额比上周怎么样"
        time_period_1: 对比时间段1（如"最近一周"）
        time_period_2: 对比时间段2（如"上周"）
        comparison_type: 对比类型（week_over_week, month_over_month, year_over_year）
        business_context: 业务背景信息
        
    Returns:
        包含完整分析结果的字典
    """
    
    try:
        analysis_id = f"sales_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 第一步：探索数据库结构
        print("🗃️ 第一步：探索数据库表结构...")
        schema_result = await database_schema_explorer(
            database_type="postgresql",
            table_pattern="orders%",
            include_columns=True
        )
        
        # 第二步：生成并执行SQL查询
        print("💾 第二步：执行销售数据查询...")
        
        # 生成时间范围SQL
        time_sql_conditions = _generate_time_conditions(comparison_type, time_period_1, time_period_2)
        
        # 构建销售对比SQL查询
        sales_comparison_sql = _build_sales_comparison_sql(time_sql_conditions, schema_result)
        
        # 执行查询
        query_result = await sql_query_executor(
            query=sales_comparison_sql,
            query_purpose=f"销售额对比分析: {question}",
            database_type="postgresql",
            limit_rows=1000
        )
        
        # 第三步：生成业务洞察
        print("💡 第三步：生成业务洞察...")
        insights_result = await insight_generator(
            analysis_data=json.dumps(query_result.get("data", {}), ensure_ascii=False),
            business_goal=business_context or "销售对比分析",
            stakeholder_interests="销售团队",
            priority_focus="销售表现对比"
        )
        
        # 第四步：生成行动建议
        print("🎯 第四步：制定行动建议...")
        action_result = await action_recommender(
            insights=_extract_performance_metrics(query_result),
            business_constraints=business_context or "跨境电商",
            implementation_capacity="中等团队",
            priority_level="高优先级"
        )
        
        # 整合分析结果
        comprehensive_analysis = {
            "分析元信息": {
                "分析ID": analysis_id,
                "分析时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "对比类型": comparison_type,
                "时间范围": f"{time_period_1 or '最近一周'} vs {time_period_2 or '上周'}",
                "分析状态": "已完成",
                "问题描述": question
            },
            
            "数据探索": {
                "数据库信息": schema_result.get("data", {}).get("数据库信息", {}),
                "可用表结构": schema_result.get("data", {}).get("表结构信息", {}),
                "SQL查询": sales_comparison_sql
            },
            
            "销售数据": query_result.get("data", {}),
            
            "深度洞察": insights_result.get("data", {}),
            
            "行动方案": action_result.get("data", {}),
            
            "分析总结": _generate_analysis_summary(
                query_result, insights_result, action_result, comparison_type
            )
        }
        
        return {
            "success": True,
            "message": "销售额对比分析完成",
            "data": comprehensive_analysis,
            "suggested_next_steps": [
                "📈 查看详细的销售数据对比结果",
                "💡 重点关注生成的业务洞察",
                "🎯 实施推荐的行动方案",
                "📊 使用 chart_type_advisor 选择合适的可视化图表",
                "🔄 定期监控关键指标变化"
            ]
        }
        
    except Exception as e:
        logging.error(f"销售额对比分析失败: {str(e)}")
        return {
            "success": False,
            "error": f"分析过程中出现错误: {str(e)}",
            "fallback_suggestions": [
                "🔍 检查数据库连接状态",
                "📊 使用 database_schema_explorer 重新探索数据结构",
                "💬 提供更详细的问题描述"
            ]
        }


def _generate_time_conditions(comparison_type: str, period_1: Optional[str], period_2: Optional[str]) -> Dict[str, str]:
    """生成时间条件SQL"""
    
    current_date = datetime.now()
    
    if comparison_type == "week_over_week":
        # 最近一周 vs 上周
        period_1_start = current_date - timedelta(days=7)
        period_1_end = current_date
        period_2_start = current_date - timedelta(days=14)
        period_2_end = current_date - timedelta(days=7)
        
        return {
            "period_1_condition": f"order_date >= '{period_1_start.strftime('%Y-%m-%d')}' AND order_date < '{period_1_end.strftime('%Y-%m-%d')}'",
            "period_2_condition": f"order_date >= '{period_2_start.strftime('%Y-%m-%d')}' AND order_date < '{period_2_end.strftime('%Y-%m-%d')}'",
            "period_1_label": "最近一周",
            "period_2_label": "上周"
        }
    
    elif comparison_type == "month_over_month":
        # 本月 vs 上月
        period_1_start = current_date.replace(day=1)
        period_2_end = period_1_start
        period_2_start = (period_1_start - timedelta(days=1)).replace(day=1)
        
        return {
            "period_1_condition": f"order_date >= '{period_1_start.strftime('%Y-%m-%d')}' AND order_date < '{current_date.strftime('%Y-%m-%d')}'",
            "period_2_condition": f"order_date >= '{period_2_start.strftime('%Y-%m-%d')}' AND order_date < '{period_2_end.strftime('%Y-%m-%d')}'",
            "period_1_label": "本月",
            "period_2_label": "上月"
        }
    
    else:  # year_over_year
        # 今年 vs 去年同期
        period_1_start = current_date.replace(month=1, day=1)
        period_2_start = period_1_start.replace(year=current_date.year - 1)
        period_2_end = current_date.replace(year=current_date.year - 1)
        
        return {
            "period_1_condition": f"order_date >= '{period_1_start.strftime('%Y-%m-%d')}' AND order_date < '{current_date.strftime('%Y-%m-%d')}'",
            "period_2_condition": f"order_date >= '{period_2_start.strftime('%Y-%m-%d')}' AND order_date < '{period_2_end.strftime('%Y-%m-%d')}'",
            "period_1_label": "今年至今",
            "period_2_label": "去年同期"
        }


def _build_sales_comparison_sql(time_conditions: Dict[str, str], schema_info: Dict[str, Any]) -> str:
    """构建销售对比SQL查询"""
    
    # 基础的销售对比查询
    base_sql = f"""
    -- 销售额对比分析查询
    WITH period_1_sales AS (
        SELECT 
            'period_1' as period_name,
            '{time_conditions["period_1_label"]}' as period_label,
            COUNT(*) as order_count,
            SUM(total_amount) as total_sales,
            AVG(total_amount) as avg_order_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM orders 
        WHERE {time_conditions["period_1_condition"]}
        AND order_status != 'cancelled'
    ),
    period_2_sales AS (
        SELECT 
            'period_2' as period_name,
            '{time_conditions["period_2_label"]}' as period_label,
            COUNT(*) as order_count,
            SUM(total_amount) as total_sales,
            AVG(total_amount) as avg_order_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM orders 
        WHERE {time_conditions["period_2_condition"]}
        AND order_status != 'cancelled'
    ),
    comparison_summary AS (
        SELECT 
            p1.period_label as current_period,
            p1.total_sales as current_sales,
            p1.order_count as current_orders,
            p1.avg_order_value as current_aov,
            p1.unique_customers as current_customers,
            
            p2.period_label as previous_period,
            p2.total_sales as previous_sales,
            p2.order_count as previous_orders,
            p2.avg_order_value as previous_aov,
            p2.unique_customers as previous_customers,
            
            -- 计算变化率
            CASE 
                WHEN p2.total_sales > 0 THEN 
                    ROUND(((p1.total_sales - p2.total_sales) / p2.total_sales * 100), 2)
                ELSE NULL 
            END as sales_change_percent,
            
            CASE 
                WHEN p2.order_count > 0 THEN 
                    ROUND(((p1.order_count - p2.order_count) / p2.order_count * 100), 2)
                ELSE NULL 
            END as order_change_percent,
            
            CASE 
                WHEN p2.avg_order_value > 0 THEN 
                    ROUND(((p1.avg_order_value - p2.avg_order_value) / p2.avg_order_value * 100), 2)
                ELSE NULL 
            END as aov_change_percent
            
        FROM period_1_sales p1
        CROSS JOIN period_2_sales p2
    )
    SELECT * FROM comparison_summary
    
    UNION ALL
    
    -- 按平台分组的对比
    SELECT 
        CONCAT('平台对比: ', COALESCE(platform, '未知平台')) as current_period,
        SUM(CASE WHEN {time_conditions["period_1_condition"]} THEN total_amount ELSE 0 END) as current_sales,
        COUNT(CASE WHEN {time_conditions["period_1_condition"]} THEN 1 END) as current_orders,
        AVG(CASE WHEN {time_conditions["period_1_condition"]} THEN total_amount END) as current_aov,
        COUNT(DISTINCT CASE WHEN {time_conditions["period_1_condition"]} THEN customer_id END) as current_customers,
        
        '' as previous_period,
        SUM(CASE WHEN {time_conditions["period_2_condition"]} THEN total_amount ELSE 0 END) as previous_sales,
        COUNT(CASE WHEN {time_conditions["period_2_condition"]} THEN 1 END) as previous_orders,
        AVG(CASE WHEN {time_conditions["period_2_condition"]} THEN total_amount END) as previous_aov,
        COUNT(DISTINCT CASE WHEN {time_conditions["period_2_condition"]} THEN customer_id END) as previous_customers,
        
        -- 平台销售额变化率
        CASE 
            WHEN SUM(CASE WHEN {time_conditions["period_2_condition"]} THEN total_amount ELSE 0 END) > 0 THEN 
                ROUND((
                    (SUM(CASE WHEN {time_conditions["period_1_condition"]} THEN total_amount ELSE 0 END) - 
                     SUM(CASE WHEN {time_conditions["period_2_condition"]} THEN total_amount ELSE 0 END)) / 
                    SUM(CASE WHEN {time_conditions["period_2_condition"]} THEN total_amount ELSE 0 END) * 100
                ), 2)
            ELSE NULL 
        END as sales_change_percent,
        NULL as order_change_percent,
        NULL as aov_change_percent
        
    FROM orders 
    WHERE ({time_conditions["period_1_condition"]} OR {time_conditions["period_2_condition"]})
    AND order_status != 'cancelled'
    GROUP BY platform
    HAVING SUM(total_amount) > 0
    ORDER BY current_sales DESC;
    """
    
    return base_sql


def _extract_performance_metrics(query_result: Dict[str, Any]) -> str:
    """从查询结果中提取性能指标"""
    
    try:
        query_data = query_result.get("data", {}).get("查询结果", [])
        
        if not query_data:
            return "无法获取性能数据"
        
        # 提取主要对比数据（第一行通常是总体对比）
        main_comparison = query_data[0] if query_data else {}
        
        current_sales = main_comparison.get("current_sales", 0)
        previous_sales = main_comparison.get("previous_sales", 0)
        sales_change = main_comparison.get("sales_change_percent", 0)
        
        performance_summary = f"""
        当前期间销售额: {current_sales:,.2f}
        上期销售额: {previous_sales:,.2f}
        销售额变化: {sales_change:+.2f}%
        订单量变化: {main_comparison.get("order_change_percent", 0):+.2f}%
        客单价变化: {main_comparison.get("aov_change_percent", 0):+.2f}%
        """
        
        return performance_summary
        
    except Exception:
        return "性能指标提取失败"


def _generate_analysis_summary(
    query_result: Dict[str, Any],
    insights_result: Dict[str, Any], 
    action_result: Dict[str, Any],
    comparison_type: str
) -> Dict[str, Any]:
    """生成分析总结"""
    
    try:
        # 提取关键数据
        query_data = query_result.get("data", {}).get("查询结果", [])
        main_data = query_data[0] if query_data else {}
        
        sales_change = main_data.get("sales_change_percent", 0)
        current_sales = main_data.get("current_sales", 0)
        previous_sales = main_data.get("previous_sales", 0)
        
        # 判断表现
        if sales_change > 5:
            performance_status = "表现优秀"
            trend_icon = "📈"
        elif sales_change > 0:
            performance_status = "稳定增长" 
            trend_icon = "📊"
        elif sales_change > -5:
            performance_status = "基本持平"
            trend_icon = "📊"
        elif sales_change > -15:
            performance_status = "需要关注"
            trend_icon = "📉"
        else:
            performance_status = "需要紧急行动"
            trend_icon = "🚨"
        
        return {
            "核心结论": {
                "整体表现": f"{trend_icon} {performance_status}",
                "销售额变化": f"{sales_change:+.2f}%",
                "当前销售额": f"{current_sales:,.2f}",
                "上期销售额": f"{previous_sales:,.2f}",
                "对比类型": comparison_type
            },
            
            "关键发现": [
                f"销售额{('增长' if sales_change > 0 else '下降')}了{abs(sales_change):.1f}%",
                f"订单量变化{main_data.get('order_change_percent', 0):+.1f}%",
                f"客单价变化{main_data.get('aov_change_percent', 0):+.1f}%"
            ],
            
            "重要洞察": insights_result.get("data", {}).get("关键洞察", [])[:3],
            
            "优先行动": action_result.get("data", {}).get("immediate_actions", [])[:3] if action_result.get("data") else [],
            
            "风险提示": [
                "数据基于当前可用信息，请结合业务实际情况判断",
                "建议结合外部因素（如促销活动、市场变化）综合分析",
                "定期监控趋势变化，及时调整策略"
            ]
        }
        
    except Exception as e:
        return {
            "总结状态": "生成失败",
            "错误信息": str(e),
            "建议": "请检查数据完整性后重新分析"
        }


# 快速分析接口
async def quick_sales_comparison(question: str) -> Dict[str, Any]:
    """快速销售额对比分析接口"""
    
    # 自动识别对比类型
    if "周" in question:
        comparison_type = "week_over_week"
    elif "月" in question:
        comparison_type = "month_over_month"
    elif "年" in question:
        comparison_type = "year_over_year"
    else:
        comparison_type = "week_over_week"  # 默认周对比
    
    return await sales_comparison_analyzer(
        question=question,
        comparison_type=comparison_type,
        business_context="跨境电商销售分析"
    ) 
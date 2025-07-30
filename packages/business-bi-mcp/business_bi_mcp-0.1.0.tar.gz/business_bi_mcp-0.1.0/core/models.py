"""
通用数据模型模块
定义智能BI助手中使用的Pydantic数据模型
"""

from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProblemType(str, Enum):
    """业务问题类型枚举"""
    SALES_DECLINE = "sales_decline"
    CUSTOMER_LOSS = "customer_loss"
    COST_INCREASE = "cost_increase"
    PROFIT_DROP = "profit_drop"
    MARKET_SHARE_LOSS = "market_share_loss"
    PRODUCT_PERFORMANCE = "product_performance"
    SEASONAL_PATTERN = "seasonal_pattern"
    COMPETITOR_IMPACT = "competitor_impact"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    CUSTOMER_SATISFACTION = "customer_satisfaction"


class DataAvailability(str, Enum):
    """数据可用性级别"""
    LIMITED = "limited"
    MODERATE = "moderate"
    COMPREHENSIVE = "comprehensive"


class BusinessSize(str, Enum):
    """业务规模"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class AnalysisPurpose(str, Enum):
    """分析目的"""
    TREND_ANALYSIS = "trend_analysis"
    COMPARISON = "comparison"
    COMPOSITION = "composition"
    DISTRIBUTION = "distribution"
    CORRELATION = "correlation"
    PERFORMANCE_TRACKING = "performance_tracking"
    REGIONAL_ANALYSIS = "regional_analysis"


class Audience(str, Enum):
    """受众类型"""
    MANAGEMENT = "management"
    COLLEAGUES = "colleagues"
    CLIENTS = "clients"
    GENERAL = "general"


class DataAccessLevel(str, Enum):
    """数据访问权限级别"""
    OWNER = "owner"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    LIMITED = "limited"


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    suggested_next_steps: List[str] = Field(default_factory=list)


class AnalysisMethod(BaseModel):
    """分析方法模型"""
    method: str = Field(description="分析方法名称")
    description: str = Field(description="方法描述")
    steps: List[str] = Field(description="实施步骤")
    charts: List[str] = Field(description="推荐图表类型")
    difficulty: Literal["简单", "中等", "复杂"] = Field(description="难度级别")


class ChartRecommendation(BaseModel):
    """图表推荐模型"""
    type: str = Field(description="图表类型")
    when: str = Field(description="使用场景")
    pros: List[str] = Field(description="优点")
    example: str = Field(description="使用示例")


class BusinessInsight(BaseModel):
    """业务洞察模型"""
    key_findings: List[str] = Field(description="关键发现")
    root_causes: List[str] = Field(description="根本原因")
    opportunities: List[str] = Field(description="机会识别")
    risks: List[str] = Field(description="风险提示")
    urgency_level: Literal["低", "中", "高"] = Field(description="紧急程度") 
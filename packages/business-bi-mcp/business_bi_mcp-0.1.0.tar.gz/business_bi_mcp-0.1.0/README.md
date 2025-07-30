# 智能BI助手 MCP - 业务小白专版

[![PyPI version](https://badge.fury.io/py/business-bi-mcp.svg)](https://badge.fury.io/py/business-bi-mcp)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/business-bi-mcp)](https://pepy.tech/project/business-bi-mcp)

> 🚀 专为业务小白设计的智能数据分析助手，提供12个核心BI分析工具，让数据分析变得简单易懂！

## 🎯 快速开始

### 安装

```bash
# 从PyPI安装
pip install business-bi-mcp

# 使用uv安装（推荐）
uv add business-bi-mcp
```

### 立即使用

```bash
# 启动BI助手（命令行方式）
business-bi-mcp

# 或者
bi-mcp

# 作为MCP服务器运行
python -m business_bi_mcp
```

### MCP客户端配置

在Claude Desktop等MCP客户端中添加配置：

```json
{
  "mcpServers": {
    "business_bi_assistant": {
      "command": "business-bi-mcp",
      "args": []
    }
  }
}
```

## 🏆 核心特色

✅ **零技术门槛** - 用业务语言，不讲技术概念  
✅ **智能引导** - 将困惑转化为清晰的分析方案  
✅ **自动推荐** - 智能推荐数据、图表和分析方法  
✅ **完整工具链** - 12个核心工具覆盖完整BI流程  
✅ **中文优化** - 专为中文用户场景优化  
✅ **即插即用** - 与Claude等AI助手无缝集成  

## 项目概述

**智能BI助手 MCP** 是专门为**没有技术背景的业务人员**设计的数据分析助手。当你遇到业务问题时，比如"销售额下降了"、"客户流失严重"、"不知道哪个产品卖得好"，这个助手会帮你一步步分析原因，找到解决方案。

### 设计理念

- **业务语言**：用你熟悉的业务术语，不讲技术概念
- **问题引导**：帮你把模糊的困惑转化为清晰的分析方案
- **自动推荐**：告诉你需要看什么数据、用什么图表
- **简单易懂**：提供具体的操作步骤，一看就会

## MCP 工具设计

### 1. 核心工具清单

```typescript
export const BUSINESS_BI_TOOLS = [
  // === 业务问题分析 ===
  'business_problem_analyzer',     // 业务问题深度分析
  'data_story_builder',           // 数据分析故事构建
  'question_guide',               // 问题引导助手
  
  // === 分析方法推荐 ===
  'analysis_method_recommender',   // 分析方法推荐
  'chart_type_advisor',           // 图表类型建议
  'kpi_identifier',               // 关键指标识别
  
  // === 实施指导 ===
  'simple_analysis_planner',      // 简化分析计划
  'data_collection_guide',        // 数据收集指导
  'result_interpreter',           // 结果解读助手
  
  // === 业务洞察 ===
  'insight_generator',            // 洞察生成器
  'action_recommender',           // 行动建议
  'follow_up_questions'           // 后续问题建议
] as const;
```

### 2. 核心工具详细设计

#### 2.1 业务问题分析器 `business_problem_analyzer`

```typescript
interface BusinessProblemAnalyzerSchema {
  name: "business_problem_analyzer";
  description: "帮助分析和理解业务问题，将模糊的困惑转化为清晰的分析方向";
  inputSchema: {
    type: "object";
    properties: {
      problem_description: {
        type: "string";
        description: "用自己的话描述遇到的业务问题或困惑";
        minLength: 5;
      };
      business_context: {
        type: "string";
        description: "简单描述你的业务类型（如电商、餐饮、制造等）";
      };
      time_period: {
        type: "string";
        description: "问题发生的时间段（如最近一个月、今年vs去年等）";
      };
      current_situation: {
        type: "string";
        description: "目前的具体情况或数据表现";
      };
    };
    required: ["problem_description"];
  };
}

async function businessProblemAnalyzer(args: BusinessProblemAnalyzerInput) {
  const analysisPrompt = `
你是一位资深的业务分析师，专门帮助没有数据分析经验的业务人员解决问题。

【用户的困惑】
${args.problem_description}

【业务背景】
${args.business_context || '待了解'}

【时间范围】
${args.time_period || '未明确'}

【当前情况】
${args.current_situation || '待详细了解'}

请用通俗易懂的语言帮助用户：

## 1. 问题理解
- **核心问题是什么**：用一句话总结用户真正想解决的问题
- **问题的具体表现**：这个问题是如何体现出来的
- **可能的影响**：如果不解决会有什么后果

## 2. 原因分析框架
为了找到原因，我们需要从这几个角度来看：
- **时间维度**：是什么时候开始出现这个问题的？
- **空间维度**：是所有地区/门店都有这个问题吗？
- **产品维度**：是所有产品都有问题还是特定产品？
- **客户维度**：是所有客户群体都有这个现象吗？

## 3. 需要收集的数据
要分析这个问题，你需要准备这些数据：
- **必需数据**：最基本必须要有的数据
- **有用数据**：如果有的话会很有帮助的数据
- **数据时间范围**：建议收集多长时间的数据

## 4. 分析重点
根据你的问题，建议重点关注：
- **关键指标**：最重要的几个数字指标
- **对比维度**：需要对比什么（时间、地区、产品等）
- **细分角度**：从哪些角度来细分数据

## 5. 预期发现
通过分析，你可能会发现：
- **潜在原因**：可能导致问题的几种原因
- **改进方向**：可以改善的几个方面
- **行动建议**：具体可以采取的措施
`;

  return {
    analysis: await callAI(analysisPrompt),
    suggestedNextSteps: [
      "使用 analysis_method_recommender 获取具体分析方法",
      "使用 data_collection_guide 了解如何收集数据", 
      "使用 kpi_identifier 确定关键指标"
    ],
    businessImpact: assessBusinessImpact(args),
    urgencyLevel: assessUrgency(args)
  };
}
```

#### 2.2 分析方法推荐器 `analysis_method_recommender`

```typescript
interface AnalysisMethodRecommenderSchema {
  name: "analysis_method_recommender";
  description: "根据业务问题推荐具体的分析方法和步骤";
  inputSchema: {
    type: "object";
    properties: {
      problem_type: {
        type: "string";
        enum: [
          "sales_decline", "customer_loss", "cost_increase", "profit_drop",
          "market_share_loss", "product_performance", "seasonal_pattern",
          "competitor_impact", "operational_efficiency", "customer_satisfaction"
        ];
        description: "问题类型分类";
      };
      data_availability: {
        type: "string";
        enum: ["limited", "moderate", "comprehensive"];
        description: "可用数据的丰富程度";
      };
      analysis_goal: {
        type: "string";
        description: "分析的主要目标";
      };
      business_size: {
        type: "string";
        enum: ["small", "medium", "large"];
        description: "业务规模";
      };
    };
    required: ["problem_type", "analysis_goal"];
  };
}

async function analysisMethodRecommender(args: AnalysisMethodRecommenderInput) {
  // 预定义分析方法库
  const analysisMethodsDB = {
    sales_decline: {
      name: "销售下降分析",
      description: "系统性分析销售下降的原因",
      methods: [
        {
          method: "趋势对比分析",
          description: "对比不同时间段的销售表现",
          steps: ["收集历史销售数据", "按月/季度制作趋势图", "识别下降起始点", "分析下降模式"],
          charts: ["折线图", "柱状图"],
          difficulty: "简单"
        },
        {
          method: "多维度拆解分析", 
          description: "从产品、地区、客户等维度拆解分析",
          steps: ["按产品分类统计", "按销售区域统计", "按客户群体统计", "识别问题集中点"],
          charts: ["饼图", "堆积柱状图", "热力图"],
          difficulty: "中等"
        },
        {
          method: "漏斗分析",
          description: "分析销售流程各环节的转化率",
          steps: ["梳理销售流程", "统计各环节数据", "计算转化率", "找出瓶颈环节"],
          charts: ["漏斗图", "转化率图"],
          difficulty: "中等"
        }
      ]
    },
    customer_loss: {
      name: "客户流失分析",
      description: "分析客户流失的原因和模式",
      methods: [
        {
          method: "客户生命周期分析",
          description: "分析客户从获取到流失的完整过程",
          steps: ["定义客户流失标准", "统计客户留存率", "分析流失时间点", "识别流失原因"],
          charts: ["留存率曲线", "生命周期图"],
          difficulty: "中等"
        },
        {
          method: "客户分群分析",
          description: "将客户按特征分组，分析不同群体的流失情况",
          steps: ["客户特征收集", "客户分群", "各群体流失率统计", "原因对比分析"],
          charts: ["分组对比图", "散点图"],
          difficulty: "复杂"
        }
      ]
    }
    // ... 其他问题类型的分析方法
  };

  const recommendationPrompt = `
根据业务问题推荐最适合的分析方法：

【问题类型】${args.problem_type}
【分析目标】${args.analysis_goal}
【数据情况】${args.data_availability || '中等'}
【业务规模】${args.business_size || '中等'}

请提供：

## 推荐的分析方法
根据问题特点，推荐2-3种最合适的分析方法

## 详细分析步骤
为每种方法提供具体的实施步骤：
1. **第一步**：具体做什么
2. **第二步**：如何操作
3. **第三步**：注意要点
4. **第四步**：结果判断

## 所需数据清单
- **必须的数据**：没有这些数据无法分析
- **有用的数据**：有了会让分析更准确
- **数据格式要求**：数据应该是什么样的

## 预期时间投入
- **数据准备时间**：收集和整理数据需要多久
- **分析时间**：进行分析大概需要多久
- **总体时间**：从开始到得出结论的时间

## 难度评估
- **操作难度**：操作的复杂程度（简单/中等/复杂）
- **技能要求**：需要什么基础技能
- **常见陷阱**：新手容易犯的错误
`;

  const problemMethods = analysisMethodsDB[args.problem_type as keyof typeof analysisMethodsDB];
  
  return {
    recommendedMethods: await callAI(recommendationPrompt),
    methodLibrary: problemMethods,
    quickStartGuide: generateQuickStartGuide(args),
    nextSteps: [
      "使用 chart_type_advisor 选择合适的图表",
      "使用 data_collection_guide 准备数据",
      "使用 simple_analysis_planner 制定分析计划"
    ]
  };
}
```

#### 2.3 图表类型顾问 `chart_type_advisor`

```typescript
interface ChartTypeAdvisorSchema {
  name: "chart_type_advisor";
  description: "根据分析目标推荐最合适的图表类型";
  inputSchema: {
    type: "object";
    properties: {
      analysis_purpose: {
        type: "string";
        enum: [
          "trend_analysis", "comparison", "composition", "distribution",
          "correlation", "performance_tracking", "regional_analysis"
        ];
        description: "分析目的";
      };
      data_characteristics: {
        type: "string";
        description: "数据的特点（如时间序列、分类数据、数值范围等）";
      };
      audience: {
        type: "string";
        enum: ["management", "colleagues", "clients", "general"];
        description: "图表的观看对象";
      };
      message_focus: {
        type: "string";
        description: "希望图表重点传达什么信息";
      };
    };
    required: ["analysis_purpose", "message_focus"];
  };
}

async function chartTypeAdvisor(args: ChartTypeAdvisorInput) {
  const chartRecommendations = {
    trend_analysis: {
      primaryCharts: [
        {
          type: "折线图",
          when: "显示数据随时间的变化趋势",
          pros: ["清晰显示趋势", "容易理解", "适合时间序列"],
          example: "月度销售额变化、客户增长趋势"
        },
        {
          type: "面积图", 
          when: "强调数量的累积或对比",
          pros: ["视觉冲击力强", "显示总量变化"],
          example: "累计销售额、市场份额变化"
        }
      ]
    },
    comparison: {
      primaryCharts: [
        {
          type: "柱状图",
          when: "比较不同类别的数值大小",
          pros: ["对比清晰", "精确显示数值", "容易制作"],
          example: "各产品销量对比、各地区业绩对比"
        },
        {
          type: "雷达图",
          when: "多维度综合对比",
          pros: ["多维展示", "整体评价"],
          example: "产品多属性对比、员工绩效评估"
        }
      ]
    },
    composition: {
      primaryCharts: [
        {
          type: "饼图",
          when: "显示部分与整体的关系",
          pros: ["直观显示占比", "简单易懂"],
          example: "销售额构成、成本结构分析"
        },
        {
          type: "堆积柱状图",
          when: "展示分类数据的构成和对比",
          pros: ["同时显示总量和构成", "支持多维对比"],
          example: "各月销售额及产品构成"
        }
      ]
    }
    // ... 其他分析目的的图表推荐
  };

  const advisorPrompt = `
为你的分析目标推荐最合适的图表：

【分析目的】${args.analysis_purpose}
【数据特点】${args.data_characteristics || '待了解'}
【观看对象】${args.audience || '同事'}
【重点信息】${args.message_focus}

请提供：

## 推荐的图表类型
根据你的需求，推荐2-3种最合适的图表类型

## 图表选择说明
为什么推荐这些图表：
- **最适合的图表**：最推荐使用的图表和原因
- **备选方案**：其他可以考虑的图表类型
- **不建议的图表**：不适合你的分析目的的图表

## 制作要点
- **数据准备**：数据需要如何整理
- **图表设置**：重要的图表参数设置
- **美化建议**：如何让图表更美观易读
- **常见错误**：制作时容易犯的错误

## 解读指导
- **关键看点**：图表中最重要的信息在哪里
- **对比技巧**：如何有效对比和分析
- **结论提取**：如何从图表得出业务结论

## 工具建议
- **简单工具**：Excel/WPS等常用工具的制作方法
- **专业工具**：如果需要更专业的图表，推荐什么工具
- **在线工具**：免费好用的在线制图工具
`;

  return {
    chartRecommendations: await callAI(advisorPrompt),
    chartLibrary: chartRecommendations[args.analysis_purpose as keyof typeof chartRecommendations],
    tutorialLinks: getChartTutorials(args.analysis_purpose),
    nextSteps: [
      "使用 data_collection_guide 准备图表数据",
      "使用 result_interpreter 学习如何解读图表",
      "使用 insight_generator 从图表中提取洞察"
    ]
  };
}
```

#### 2.4 数据收集指导 `data_collection_guide`

```typescript
interface DataCollectionGuideSchema {
  name: "data_collection_guide";
  description: "指导用户如何收集和准备分析所需的数据";
  inputSchema: {
    type: "object";
    properties: {
      analysis_type: {
        type: "string";
        description: "要进行的分析类型";
      };
      business_system: {
        type: "string";
        description: "现有的业务系统（如收银系统、ERP、电商平台等）";
      };
      data_access_level: {
        type: "string";
        enum: ["owner", "manager", "employee", "limited"];
        description: "数据获取权限级别";
      };
      time_constraint: {
        type: "string";
        description: "时间要求（如急需、一周内、充足时间等）";
      };
    };
    required: ["analysis_type"];
  };
}

async function dataCollectionGuide(args: DataCollectionGuideInput) {
  const dataGuidePrompt = `
帮你准备分析所需的数据：

【分析类型】${args.analysis_type}
【业务系统】${args.business_system || '待了解'}
【数据权限】${args.data_access_level || '一般员工'}
【时间要求】${args.time_constraint || '正常'}

请提供：

## 数据清单
根据你的分析需求，需要收集这些数据：

### 核心数据（必须有）
- **数据1**：具体是什么数据，从哪里获取
- **数据2**：为什么需要这个数据，如何使用
- **数据3**：数据的时间范围要求

### 补充数据（有更好）
- **辅助数据**：能让分析更准确的额外数据
- **背景数据**：帮助理解业务背景的数据

## 数据获取方法
### 如果你有系统管理权限
- **直接导出**：从哪个系统的哪个模块导出
- **报表生成**：如何生成需要的报表
- **数据格式**：导出什么格式最好用

### 如果你权限有限
- **找谁帮忙**：应该联系哪个部门或同事
- **申请理由**：如何说明数据用途获得支持  
- **替代方案**：如果拿不到原始数据的其他办法

## 数据整理步骤
1. **数据检查**：拿到数据后先检查什么
2. **数据清理**：如何处理缺失值、异常值
3. **数据格式化**：如何统一数据格式
4. **数据验证**：如何确认数据准确性

## 常见问题解决
- **数据不全**：如果某些数据缺失怎么办
- **数据质量差**：如果数据有错误如何处理
- **格式混乱**：如何统一不同来源的数据格式
- **权限限制**：如何在有限权限下获取足够信息

## 数据保护
- **敏感信息**：哪些数据需要特别保护
- **使用规范**：数据使用的注意事项
- **保存建议**：如何安全保存和备份数据
`;

  return {
    dataGuide: await callAI(dataGuidePrompt),
    dataTemplates: generateDataTemplates(args.analysis_type),
    quickChecklist: getDataCollectionChecklist(),
    nextSteps: [
      "使用 simple_analysis_planner 制定分析计划",
      "使用 chart_type_advisor 选择合适的图表",
      "开始数据收集，有问题可随时咨询"
    ]
  };
}
```

#### 2.5 洞察生成器 `insight_generator`

```typescript
interface InsightGeneratorSchema {
  name: "insight_generator";
  description: "帮助从数据分析结果中提取有价值的业务洞察";
  inputSchema: {
    type: "object";
    properties: {
      analysis_results: {
        type: "string";
        description: "分析得到的结果或观察到的现象";
      };
      business_context: {
        type: "string";
        description: "业务背景信息";
      };
      key_findings: {
        type: "string";
        description: "主要发现或数据表现";
      };
      original_question: {
        type: "string";
        description: "最初想要解决的业务问题";
      };
    };
    required: ["analysis_results", "original_question"];
  };
}

async function insightGenerator(args: InsightGeneratorInput) {
  const insightPrompt = `
帮你从分析结果中提取有价值的业务洞察：

【分析结果】
${args.analysis_results}

【业务背景】
${args.business_context || '待补充'}

【主要发现】
${args.key_findings || '基于分析结果'}

【原始问题】
${args.original_question}

请帮我提取洞察：

## 关键发现
从你的分析中，我们发现了这些重要信息：
- **核心发现1**：最重要的发现是什么
- **核心发现2**：第二重要的发现
- **意外发现**：有什么预料之外的发现吗

## 业务洞察
这些发现对你的业务意味着什么：
- **根本原因**：问题的根本原因可能是什么
- **影响分析**：这个问题会带来什么影响
- **机会识别**：是否发现了新的机会

## 深度解读
- **趋势判断**：这个情况是临时的还是长期趋势
- **程度评估**：问题的严重程度如何
- **范围分析**：影响范围有多大

## 对标分析
- **行业对比**：与行业平均水平相比如何
- **历史对比**：与自己的历史表现相比如何
- **竞争对比**：可能的竞争因素分析

## 风险提示
- **潜在风险**：需要警惕什么风险
- **关键指标**：需要持续监控什么指标
- **预警信号**：什么情况下需要立即行动
`;

  return {
    businessInsights: await callAI(insightPrompt),
    actionableFacts: extractActionableFacts(args),
    riskAssessment: assessBusinessRisks(args),
    nextSteps: [
      "使用 action_recommender 获取具体行动建议",
      "使用 follow_up_questions 了解需要进一步分析的问题",
      "制定基于洞察的改进计划"
    ]
  };
}
```

### 3. 业务问题模板库

```typescript
export const BUSINESS_PROBLEM_TEMPLATES = {
  // 销售问题模板
  sales_issues: {
    templates: [
      {
        problem: "销售额下降",
        commonQuestions: [
          "为什么这个月销售额比上个月少了？",
          "今年的销售不如去年，怎么回事？",
          "最近生意不好，不知道哪里出了问题"
        ],
        analysisApproach: "趋势分析 + 多维度拆解",
        keyMetrics: ["销售额", "订单量", "客单价", "转化率"],
        typicalCauses: ["市场环境", "竞争加剧", "产品问题", "销售策略"]
      },
      {
        problem: "产品卖不动",
        commonQuestions: [
          "某个产品突然卖不动了",
          "新产品推出后反响不好",
          "库存积压严重"
        ],
        analysisApproach: "产品表现分析 + 客户反馈分析",
        keyMetrics: ["销量", "库存周转", "客户评价", "退货率"],
        typicalCauses: ["定价问题", "质量问题", "需求变化", "推广不足"]
      }
    ]
  },
  
  // 客户问题模板
  customer_issues: {
    templates: [
      {
        problem: "客户流失",
        commonQuestions: [
          "老客户不来了",
          "客户复购率下降",
          "流失的客户越来越多"
        ],
        analysisApproach: "客户生命周期分析 + 流失原因分析",
        keyMetrics: ["流失率", "复购率", "客户满意度", "服务质量"],
        typicalCauses: ["服务问题", "价格竞争", "需求变化", "体验不佳"]
      }
    ]
  },
  
  // 运营问题模板
  operational_issues: {
    templates: [
      {
        problem: "成本上升",
        commonQuestions: [
          "成本越来越高，利润越来越少",
          "不知道钱都花到哪里去了",
          "运营效率感觉不高"
        ],
        analysisApproach: "成本结构分析 + 效率分析",
        keyMetrics: ["各项成本占比", "人效", "坪效", "周转率"],
        typicalCauses: ["原材料涨价", "人力成本", "管理效率", "浪费问题"]
      }
    ]
  }
};
```

### 4. 简化的分析流程

```typescript
export const SIMPLIFIED_ANALYSIS_WORKFLOW = {
  // 三步分析法
  step1: {
    name: "看现象",
    description: "先看数据表现，发现问题",
    actions: [
      "收集基础数据",
      "制作简单图表",
      "识别异常表现"
    ],
    tools: ["data_collection_guide", "chart_type_advisor"]
  },
  
  step2: {
    name: "找原因", 
    description: "深入分析，找到原因",
    actions: [
      "多角度拆解分析",
      "对比历史数据",
      "识别影响因素"
    ],
    tools: ["analysis_method_recommender", "insight_generator"]
  },
  
  step3: {
    name: "定方案",
    description: "基于分析结果，制定改进方案",
    actions: [
      "总结关键洞察",
      "制定行动计划",
      "设定监控指标"
    ],
    tools: ["action_recommender", "follow_up_questions"]
  }
};
```

### 5. 使用示例

```typescript
// 典型的业务小白使用流程

// 用户问题："最近销售额下降了，不知道为什么"
const userProblem = "最近一个月销售额比上个月下降了20%，不知道是什么原因";

// 1. 分析业务问题
const problemAnalysis = await mcp.callTool('business_problem_analyzer', {
  problem_description: userProblem,
  business_context: "小型服装店，主营女装",
  time_period: "最近一个月 vs 上个月",
  current_situation: "销售额从10万降到8万"
});

// 2. 获取分析方法建议
const analysisMethod = await mcp.callTool('analysis_method_recommender', {
  problem_type: "sales_decline",
  analysis_goal: "找出销售下降的具体原因",
  data_availability: "moderate",
  business_size: "small"
});

// 3. 获取图表建议
const chartAdvice = await mcp.callTool('chart_type_advisor', {
  analysis_purpose: "trend_analysis",
  data_characteristics: "月度销售数据，按产品分类",
  audience: "management",
  message_focus: "识别销售下降的时间点和产品"
});

// 4. 数据收集指导
const dataGuide = await mcp.callTool('data_collection_guide', {
  analysis_type: "销售下降分析",
  business_system: "收银系统 + 手工记录",
  data_access_level: "owner",
  time_constraint: "一周内"
});

// 5. 生成洞察（在分析完成后）
const insights = await mcp.callTool('insight_generator', {
  analysis_results: "通过数据分析发现主要是连衣裙销量下降70%",
  business_context: "小型服装店，季节性业务",
  key_findings: "连衣裙销量大幅下降，其他品类基本稳定",
  original_question: userProblem
});
```

### 6. MCP配置

```json
{
  "name": "business-bi-assistant",
  "version": "1.0.0", 
  "description": "专为业务小白设计的智能BI分析助手",
  "main": "dist/index.js",
  "keywords": ["business-analysis", "bi", "non-technical", "simple"],
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.6.0",
    "zod": "^3.22.0"
  }
}
```

## 总结

这个优化后的智能BI MCP专门针对**业务小白**设计：

### 🎯 **核心特色**
- **业务语言**：避免技术术语，用业务人员熟悉的语言
- **问题引导**：帮助用户将模糊困惑转化为清晰分析方向
- **方法推荐**：自动推荐适合的分析方法和图表类型
- **步骤简化**：提供简单易懂的三步分析流程

### 🛠️ **主要工具**
- `business_problem_analyzer` - 理解和分析业务问题
- `analysis_method_recommender` - 推荐分析方法
- `chart_type_advisor` - 图表类型建议
- `data_collection_guide` - 数据收集指导
- `insight_generator` - 洞察提取

### 💡 **适用场景**
- "销售额下降了，不知道为什么"
- "客户流失严重，怎么办"
- "这个月利润很低，哪里出问题了"
- "新产品卖得不好，要不要继续"

这样的设计能够真正帮助没有技术背景的业务人员进行数据分析，解决实际的业务问题。 
"""
MCP服务器配置模块
管理FastMCP服务器的创建、配置和工具注册
"""

import logging
from typing import Optional
from fastmcp import FastMCP

# 导入优化后的核心BI工具 - 使用新的模块化结构
from tools.core import QuestionAnalyzer, sales_comparison_analyzer
from tools.database import database_schema_explorer, sql_query_executor
from tools.insights import insight_generator, action_recommender, follow_up_questions, data_story_builder
from tools.visualization.chart_advisor import chart_type_advisor

# 降低 MCP 协议日志级别
logging.getLogger("fastmcp").setLevel(logging.WARNING)


def create_mcp_server(name: str = "business_bi_assistant") -> FastMCP:
    """
    创建并配置MCP服务器
    
    Args:
        name: 服务器名称
        
    Returns:
        配置好的FastMCP服务器实例
    """
    mcp = FastMCP(
        name=name,
        instructions="""
        智能BI助手 - 专为单一数据源（查库）设计的高效数据分析助手
        
        优化后的7个核心工具，消除功能重叠，简化使用流程：
        
        🔍 智能问题理解：
        - business_problem_analyzer: 智能分析业务问题，自动识别问题类型、拆解复杂问题、规划分析路径
        
        📊 数据获取工具：
        - database_schema_explorer: 探索数据库结构和字段信息
        - sql_query_executor: 安全执行SQL查询获取数据
        
        📈 专业分析工具：
        - sales_comparison_analyzer: 完整的销售对比分析流程，集成多维度销售分析
        
        💡 洞察与决策工具：
        - insight_generator: 生成业务洞察，整合结果解读和数据故事功能  
        - action_recommender: 提供行动建议和实施计划，包含后续问题建议
        - chart_type_advisor: 推荐最适合的图表类型进行可视化
        
        简化后的使用流程：
        1. 使用 business_problem_analyzer 智能理解问题需求
        2. 使用 database_schema_explorer 探索可用数据结构
        3. 使用 sql_query_executor 或 sales_comparison_analyzer 获取分析数据
        4. 使用 insight_generator 生成深度洞察
        5. 使用 action_recommender 制定行动方案
        6. 使用 chart_type_advisor 选择合适的可视化方式
        """
    )
    
    # 注册优化后的BI工具
    register_optimized_bi_tools(mcp)
    
    return mcp


def register_optimized_bi_tools(mcp: FastMCP) -> None:
    """
    注册优化后的7个核心智能BI工具
    """
    
    # 初始化智能问题分析器 - 使用新的类名
    question_analyzer = QuestionAnalyzer()
    
    # === 智能问题理解工具 ===
    @mcp.tool(
        description="智能业务问题分析器 - 自动识别问题类型（排名、对比、趋势等），智能拆解复杂问题，自动规划分析路径，为单一数据源场景优化"
    )
    async def business_problem_analyzer_tool(
        question: str,
        business_context: Optional[str] = None,
        analysis_depth: Optional[str] = "standard",
        include_detailed_breakdown: bool = True
    ):
        """智能业务问题分析器"""
        try:
            # 使用通用问题分析器进行智能分析
            analysis_result = await question_analyzer.analyze_question(question, business_context)
            
            # 获取分析摘要
            summary = question_analyzer.get_analysis_summary(analysis_result)
            
            # 构建基础返回数据
            response_data = {
                "问题分析": {
                    "原始问题": question,
                    "问题类型": analysis_result.question_type,
                    "复杂度": analysis_result.complexity_level,
                    "是否需要数据": analysis_result.data_required,
                    "预估步骤": analysis_result.estimated_steps
                },
                "分析路径": analysis_result.analysis_path,
                "查询要素": analysis_result.query_components
            }
            
            # 根据参数决定是否包含详细分解
            if include_detailed_breakdown:
                response_data.update({
                    "子问题分解": analysis_result.sub_questions,
                    "分析摘要": summary
                })
            
            # 生成建议的后续步骤
            suggested_steps = []
            if analysis_result.data_required:
                suggested_steps.append("📊 使用 database_schema_explorer 探索数据结构")
                suggested_steps.append("🔍 根据分析路径执行后续步骤")
                if "销售" in question or "revenue" in question.lower():
                    suggested_steps.append("📈 使用 sales_comparison_analyzer 进行销售分析")
                else:
                    suggested_steps.append("🗄️ 使用 sql_query_executor 执行数据查询")
            else:
                suggested_steps.append("💡 直接进行业务分析和逻辑推理")
                
            suggested_steps.extend([
                "💡 使用 insight_generator 生成业务洞察",
                "🎯 使用 action_recommender 制定行动计划"
            ])

            return {
                "success": True,
                "message": "问题分析完成",
                "data": response_data,
                "suggested_next_steps": suggested_steps
            }
            
        except Exception as e:
            logging.error(f"问题分析失败: {str(e)}")
            return {
                "success": False,
                "error": f"问题分析失败: {str(e)}",
                "suggested_next_steps": [
                    "💬 尝试重新描述问题",
                    "📋 提供更多业务背景信息",
                    "🔄 检查网络连接并重试"
                ]
            }
    
    # === 数据库工具 ===
    @mcp.tool(
        description="探索数据库中的表结构和字段信息，为SQL查询提供基础"
    )
    async def database_schema_explorer_tool(
        database_type: str = "postgresql",
        connection_string: Optional[str] = None,
        table_pattern: Optional[str] = None,
        include_columns: bool = True
    ):
        """数据库表结构探索器"""
        return await database_schema_explorer(database_type, connection_string, table_pattern, include_columns)
    
    @mcp.tool(
        description="安全执行SQL查询并返回分析结果，支持各种业务分析场景"
    )
    async def sql_query_executor_tool(
        query: str,
        query_purpose: str,
        database_type: str = "postgresql",
        connection_string: Optional[str] = None,
        limit_rows: int = 1000,
        explain_plan: bool = False
    ):
        """SQL查询执行器"""
        return await sql_query_executor(query, query_purpose, database_type, connection_string, limit_rows, explain_plan)
    
    # === 专业分析工具 ===
    @mcp.tool(
        description="销售对比分析器 - 提供完整的销售对比分析流程，自动生成SQL查询、执行分析、生成洞察和建议，专门针对销售相关问题优化"
    )
    async def sales_comparison_analyzer_tool(
        question: str,
        time_period_1: Optional[str] = None,
        time_period_2: Optional[str] = None,
        comparison_type: str = "week_over_week",
        business_context: Optional[str] = None
    ):
        """销售对比分析器"""
        return await sales_comparison_analyzer(question, time_period_1, time_period_2, comparison_type, business_context)
    
    # === 洞察与决策工具 ===
    @mcp.tool(
        description="增强版洞察生成器 - 从分析结果中提取关键业务洞察，整合结果解读和数据故事构建功能，提供多层次的业务价值分析"
    )
    async def insight_generator_tool(
        analysis_results: str,
        business_context: str,
        key_findings: Optional[str] = None,
        original_question: Optional[str] = None,
        include_story: bool = True
    ):
        """增强版洞察生成器"""
        # 调用原有的洞察生成功能 - 使用正确的参数名
        insights_result = await insight_generator(
            analysis_results=analysis_results,
            business_context=business_context,
            key_findings=key_findings,
            original_question=original_question
        )
        
        if include_story and insights_result.get("success"):
            # 整合数据故事功能 - 使用已导入的函数
            try:
                story_result = await data_story_builder(
                    key_insights=str(insights_result.get("data", {})),
                    target_audience=business_context,
                    business_impact=original_question or "业务目标"
                )
                
                # 合并洞察和故事
                if story_result.get("success"):
                    insights_result["data"]["数据故事"] = story_result.get("data", {})
                    
            except Exception as e:
                # 如果数据故事生成失败，继续返回基础洞察
                insights_result["data"]["数据故事生成错误"] = str(e)
        
        return insights_result
    
    @mcp.tool(
        description="增强版行动建议器 - 基于分析洞察提供具体的行动建议和实施计划，整合后续问题生成功能，提供完整的决策支持"
    )
    async def action_recommender_tool(
        business_insights: str,
        business_priority: str,
        available_resources: Optional[str] = None,
        time_frame: Optional[str] = "3个月",
        include_follow_up: bool = True
    ):
        """增强版行动建议器"""
        # 调用原有的行动建议功能 - 使用正确的参数名
        action_result = await action_recommender(
            business_insights=business_insights,
            business_priority=business_priority,
            available_resources=available_resources,
            time_frame=time_frame
        )
        
        if include_follow_up and action_result.get("success"):
            # 整合后续问题功能 - 使用已导入的函数
            try:
                follow_up_result = await follow_up_questions(
                    current_analysis=business_insights,
                    findings_summary=business_priority,
                    business_objective=available_resources or "通用业务目标"
                )
                
                # 合并行动建议和后续问题
                if follow_up_result.get("success"):
                    action_result["data"]["后续探索问题"] = follow_up_result.get("data", {})
                    
            except Exception as e:
                # 如果后续问题生成失败，继续返回基础建议
                action_result["data"]["后续问题生成错误"] = str(e)
        
        return action_result
    
    @mcp.tool(
        description="图表类型顾问 - 根据数据类型和分析目的推荐最适合的图表类型，帮助选择最佳的数据可视化方案"
    )
    async def chart_type_advisor_tool(
        analysis_purpose: str,
        message_focus: str,
        data_characteristics: Optional[str] = None,
        audience: Optional[str] = "colleagues"
    ):
        """图表类型顾问"""
        return await chart_type_advisor(
            analysis_purpose=analysis_purpose,
            message_focus=message_focus,
            data_characteristics=data_characteristics,
            audience=audience
        )

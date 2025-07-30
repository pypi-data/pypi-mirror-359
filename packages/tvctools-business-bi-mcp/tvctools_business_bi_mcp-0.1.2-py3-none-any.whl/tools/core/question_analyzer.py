"""
通用问题分析器
自动识别问题类型、判断数据需求、拆解复杂问题并规划分析路径
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class QuestionAnalysis:
    """问题分析结果"""
    question_type: str
    data_required: bool
    complexity_level: str  # simple, medium, complex
    sub_questions: List[str]
    query_components: Dict[str, Any]
    analysis_path: List[str]
    estimated_steps: int


class _QuestionAnalyzer:
    """通用问题分析器的基础实现"""
    
    def __init__(self):
        self.question_patterns = self._initialize_patterns()
        self.data_indicators = self._initialize_data_indicators()
        
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """初始化问题模式识别"""
        return {
            "simple_query": {
                "keywords": ["多少", "什么", "哪个", "几个", "总计", "合计"],
                "patterns": [
                    r"(.+)是多少",
                    r"什么是(.+)",
                    r"哪个(.+)",
                    r"(.+)的总(.+)"
                ],
                "examples": ["上周的销售额是多少", "什么是最好的产品"]
            },
            
            "ranking_analysis": {
                "keywords": ["前", "后", "最", "排名", "排行", "TOP", "前10", "最高", "最低"],
                "patterns": [
                    r"(.+)最(.+)的前(\d+)",
                    r"前(\d+)(.+)",
                    r"TOP\s*(\d+)",
                    r"排名前(\d+)"
                ],
                "examples": ["毛利率最高的前10个产品", "销售最多的前5名"]
            },
            
            "comparison_analysis": {
                "keywords": ["对比", "比较", "相比", "vs", "和", "与", "上周", "上月", "同期"],
                "patterns": [
                    r"(.+)对比(.+)",
                    r"(.+)和(.+)比较",
                    r"(.+)相比(.+)",
                    r"(.+)vs(.+)"
                ],
                "examples": ["最近一周vs上周", "今年和去年对比"]
            },
            
            "trend_analysis": {
                "keywords": ["趋势", "变化", "发展", "走势", "增长", "下降", "波动"],
                "patterns": [
                    r"(.+)趋势",
                    r"(.+)的变化",
                    r"(.+)走势分析"
                ],
                "examples": ["最近3个月的销售趋势", "客户增长变化"]
            },
            
            "correlation_analysis": {
                "keywords": ["关系", "影响", "相关", "因素", "原因", "导致"],
                "patterns": [
                    r"(.+)和(.+)的关系",
                    r"(.+)对(.+)的影响",
                    r"分析(.+)的原因"
                ],
                "examples": ["分析销售下降的原因", "产品价格对销量的影响"]
            },
            
            "comprehensive_analysis": {
                "keywords": ["分析", "评估", "研究", "报告", "总结", "建议"],
                "patterns": [
                    r"分析(.+)",
                    r"评估(.+)",
                    r"(.+)分析报告"
                ],
                "examples": ["分析Q4业绩表现", "评估市场表现"]
            }
        }
    
    def _initialize_data_indicators(self) -> Dict[str, List[str]]:
        """初始化数据需求指示词"""
        return {
            "sales_data": ["销售", "销量", "营收", "收入", "业绩", "GMV"],
            "product_data": ["产品", "商品", "SKU", "品类", "毛利", "利润"],
            "customer_data": ["客户", "用户", "买家", "消费者", "会员"],
            "order_data": ["订单", "交易", "成交", "下单", "购买"],
            "financial_data": ["成本", "费用", "利润", "盈利", "亏损"],
            "operational_data": ["库存", "物流", "配送", "退货", "售后"],
            "time_data": ["昨天", "今天", "上周", "本周", "上月", "本月", "去年", "今年"]
        }
    
    async def analyze_question(self, question: str, context: Optional[str] = None) -> QuestionAnalysis:
        """分析问题并返回分析结果"""
        try:
            # 1. 识别问题类型
            question_type = self._identify_question_type(question)
            
            # 2. 判断数据需求
            data_required = self._check_data_requirement(question)
            
            # 3. 评估复杂度
            complexity_level = self._assess_complexity(question, question_type)
            
            # 4. 拆解子问题
            sub_questions = self._decompose_question(question, question_type)
            
            # 5. 提取查询要素
            query_components = self._extract_query_components(question, question_type)
            
            # 6. 规划分析路径
            analysis_path = self._plan_analysis_path(question_type, data_required, complexity_level)
            
            # 7. 估算步骤数
            estimated_steps = len(analysis_path)
            
            # 8. 构建并返回分析结果
            return QuestionAnalysis(
                question_type=question_type,
                data_required=data_required,
                complexity_level=complexity_level,
                sub_questions=sub_questions,
                query_components=query_components,
                analysis_path=analysis_path,
                estimated_steps=estimated_steps
            )
            
        except Exception as e:
            logging.error(f"问题分析失败: {str(e)}")
            # 返回一个基础分析结果
            return QuestionAnalysis(
                question_type="unknown",
                data_required=True,
                complexity_level="medium",
                sub_questions=[question],
                query_components={},
                analysis_path=["理解问题需求", "获取数据", "分析数据"],
                estimated_steps=3
            )
    
    def _identify_question_type(self, question: str) -> str:
        """识别问题类型"""
        
        # 计算每种类型的匹配分数
        type_scores = {}
        
        for q_type, pattern_info in self.question_patterns.items():
            score = 0
            
            # 关键词匹配
            for keyword in pattern_info["keywords"]:
                if keyword in question:
                    score += 1
            
            # 正则模式匹配
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, question):
                    score += 2
            
            type_scores[q_type] = score
        
        # 返回得分最高的类型
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return "comprehensive_analysis"  # 默认类型
    
    def _check_data_requirement(self, question: str) -> bool:
        """判断是否需要查询数据"""
        
        # 检查是否包含数据相关关键词
        for category, keywords in self.data_indicators.items():
            for keyword in keywords:
                if keyword in question:
                    return True
        
        # 检查是否包含数量、统计相关词汇
        quantity_indicators = ["多少", "几个", "数量", "统计", "计算", "总计", "平均", "最大", "最小"]
        for indicator in quantity_indicators:
            if indicator in question:
                return True
        
        return False
    
    def _assess_complexity(self, question: str, question_type: str) -> str:
        """评估问题复杂度"""
        
        complexity_factors = 0
        
        # 基于问题类型的基础复杂度
        base_complexity = {
            "simple_query": 1,
            "ranking_analysis": 2,
            "comparison_analysis": 3,
            "trend_analysis": 3,
            "correlation_analysis": 4,
            "comprehensive_analysis": 5
        }
        
        complexity_factors += base_complexity.get(question_type, 3)
        
        # 检查复杂度指示因子
        if "分析" in question and "原因" in question:
            complexity_factors += 2
        
        if "建议" in question or "方案" in question:
            complexity_factors += 1
            
        if "前" in question and any(char.isdigit() for char in question):
            complexity_factors += 1
        
        if any(word in question for word in ["综合", "全面", "深入", "详细"]):
            complexity_factors += 2
        
        # 判断复杂度级别
        if complexity_factors <= 2:
            return "simple"
        elif complexity_factors <= 4:
            return "medium"
        else:
            return "complex"
    
    def _decompose_question(self, question: str, question_type: str) -> List[str]:
        """拆解复杂问题为子问题"""
        
        sub_questions = []
        
        if question_type == "comprehensive_analysis":
            # 综合分析需要拆解
            if "分析" in question and "原因" in question:
                sub_questions.extend([
                    "获取相关数据指标",
                    "计算关键指标值",
                    "识别异常和趋势",
                    "分析影响因素",
                    "总结根本原因"
                ])
            elif "建议" in question:
                sub_questions.extend([
                    "分析当前状况",
                    "识别问题和机会",
                    "制定改进方案",
                    "评估方案可行性"
                ])
            else:
                sub_questions.append("分析关键业务指标")
        
        elif question_type == "ranking_analysis":
            # 排名分析的子问题
            sub_questions.extend([
                "获取相关产品/项目数据",
                "计算排名指标",
                "生成排名列表",
                "分析排名原因"
            ])
        
        elif question_type == "comparison_analysis":
            # 对比分析的子问题
            sub_questions.extend([
                "获取对比期间数据",
                "计算对比指标",
                "分析变化原因",
                "评估影响因素"
            ])
        
        return sub_questions if sub_questions else [question]
    
    def _extract_query_components(self, question: str, question_type: str) -> Dict[str, Any]:
        """提取查询要素"""
        
        components = {
            "metrics": [],
            "filters": [],
            "time_range": None,
            "grouping": [],
            "sorting": None,
            "limit": None
        }
        
        # 提取指标
        for category, keywords in self.data_indicators.items():
            for keyword in keywords:
                if keyword in question:
                    components["metrics"].append(keyword)
        
        # 提取时间范围
        time_patterns = [
            r"上周", r"本周", r"上月", r"本月", r"去年", r"今年",
            r"最近(\d+)(天|周|月)", r"过去(\d+)(天|周|月)"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, question)
            if match:
                components["time_range"] = match.group(0)
                break
        
        # 提取数量限制
        limit_match = re.search(r"前(\d+)|TOP\s*(\d+)", question)
        if limit_match:
            components["limit"] = int(limit_match.group(1) or limit_match.group(2))
        
        # 提取排序要求
        if "最高" in question:
            components["sorting"] = "DESC"
        elif "最低" in question:
            components["sorting"] = "ASC"
        
        return components
    
    def _plan_analysis_path(self, question_type: str, data_required: bool, complexity_level: str) -> List[str]:
        """规划分析路径"""
        
        if not data_required:
            # 不需要数据的分析路径
            return [
                "理解问题需求",
                "制定分析框架", 
                "逐步分析推理",
                "生成结论和建议"
            ]
        
        # 需要数据的标准化流程
        standard_path = [
            "理解问题需求",
            "获取数据库表结构",
            "分析数据关系与问题",
            "生成查询SQL",
            "执行SQL获取数据",
            "分析数据结果",
            "生成业务洞察",
            "制定行动建议"
        ]
        
        # 根据复杂度调整路径
        if complexity_level == "complex":
            # 复杂问题需要额外步骤
            enhanced_path = standard_path.copy()
            enhanced_path.insert(1, "拆解为子问题")
            enhanced_path.insert(-1, "综合多维分析")
            return enhanced_path
        
        elif complexity_level == "simple":
            # 简单问题可以简化流程
            return [
                "理解问题需求",
                "获取表结构",
                "生成查询SQL", 
                "执行查询获取数据",
                "返回分析结果"
            ]
        
        return standard_path
    
    def get_analysis_summary(self, analysis: QuestionAnalysis) -> Dict[str, Any]:
        """获取分析摘要"""
        
        return {
            "问题分析摘要": {
                "问题类型": analysis.question_type,
                "是否需要数据": "是" if analysis.data_required else "否",
                "复杂度级别": analysis.complexity_level,
                "预估步骤数": analysis.estimated_steps,
                "分析路径": analysis.analysis_path
            },
            "查询要素": analysis.query_components,
            "子问题列表": analysis.sub_questions
        }

class QuestionAnalyzer:
    """异步通用问题分析器"""
    
    def __init__(self):
        self._analyzer = _QuestionAnalyzer()
    
    async def analyze_question(self, question: str, context: Optional[str] = None) -> QuestionAnalysis:
        """异步分析问题并返回分析结果"""
        try:
            # 调用内部分析器的异步方法
            analysis = await self._analyzer.analyze_question(question, context)
            return analysis
        except Exception as e:
            logging.error(f"问题分析失败: {str(e)}")
            # 返回一个基础分析结果
            return QuestionAnalysis(
                question_type="unknown",
                data_required=True,
                complexity_level="medium",
                sub_questions=[question],
                query_components={},
                analysis_path=["理解问题需求", "获取数据", "分析数据"],
                estimated_steps=3
            )
    
    def get_analysis_summary(self, analysis: QuestionAnalysis) -> Dict[str, Any]:
        """获取分析摘要"""
        try:
            return self._analyzer.get_analysis_summary(analysis)
        except Exception as e:
            logging.error(f"获取分析摘要失败: {str(e)}")
            return {
                "问题分析摘要": {
                    "问题类型": "unknown",
                    "是否需要数据": "是",
                    "复杂度级别": "medium",
                    "预估步骤数": 3,
                    "分析路径": ["理解问题需求", "获取数据", "分析数据"]
                },
                "查询要素": {},
                "子问题列表": []
            } 
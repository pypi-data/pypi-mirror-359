"""
数据库表结构探索模块
提供数据库表结构探索和schema信息获取功能
"""

import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional, Union
import sys
import os
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入公共数据库配置
try:
    from common.db_config import (
        POSTGRES_CONFIG, ECOMMERCE_TABLES,
        get_db_connection, execute_query, get_table_schema,
        get_database_summary
    )
    USE_COMMON_CONFIG = True
except ImportError:
    USE_COMMON_CONFIG = False
    # 备用配置
    POSTGRES_CONFIG = {
        "host": "aws-0-us-east-2.pooler.supabase.com",
        "database": "postgres",
        "user": "postgres.lskfuytknzwktrrbkhsk",
        "password": "f$wFANpa+D.a3f_",
        "port": 6543
    }

def _get_default_connection_string() -> str:
    """获取默认连接字符串"""
    return f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"

def _get_connection_params(connection_string: Optional[str] = None) -> Dict[str, Any]:
    """从连接字符串或默认配置获取连接参数"""
    if connection_string:
        # 解析连接字符串
        # postgresql://user:password@host:port/database
        import urllib.parse
        parsed = urllib.parse.urlparse(connection_string)
        return {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip('/'),
            "user": parsed.username,
            "password": parsed.password
        }
    else:
        return POSTGRES_CONFIG

async def database_schema_explorer(
    database_type: str = "postgresql",
    connection_string: Optional[str] = None,
    table_pattern: Optional[str] = None,
    include_columns: bool = True
) -> Dict[str, Any]:
    """
    探索数据库表结构和schema信息
    
    Args:
        database_type: 数据库类型 (postgresql, mysql, sqlite等)
        connection_string: 数据库连接字符串，如果不提供则使用默认配置
        table_pattern: 表名过滤模式 (如 'sales_%', '%_order%' 等)
        include_columns: 是否包含详细的列信息
    
    Returns:
        包含数据库表结构信息的字典
    """
    
    try:
        # 获取连接参数
        conn_params = _get_connection_params(connection_string)
            
        # 使用真实的数据库连接
        schema_info = _query_real_schema(conn_params, table_pattern, include_columns)
        
        # 为跨境电商优化schema建议
        ecommerce_suggestions = _generate_ecommerce_schema_suggestions(schema_info)
        
        # 生成SQL生成提示
        sql_generation_hints = _generate_sql_hints(schema_info)
        
        return {
            "success": True,
            "data": {
                "数据库信息": {
                    "数据库类型": database_type,
                    "表总数": len(schema_info.get("tables", [])),
                    "连接状态": "真实连接",
                    "连接配置": f"{conn_params['host']}:{conn_params['port']}"
                },
                "表结构信息": schema_info,
                "跨境电商建议": ecommerce_suggestions,
                "SQL生成提示": sql_generation_hints
            },
            "suggested_next_steps": [
                "使用 sql_query_executor 执行数据查询",
                "根据表结构生成分析SQL",
                "选择相关的业务表进行分析"
            ]
        }
        
    except Exception as e:
        logging.error(f"数据库schema探索失败: {str(e)}")
        return {
            "success": False,
            "error": f"schema探索失败: {str(e)}",
            "fallback_suggestions": [
                "检查数据库连接配置",
                "确认数据库访问权限",
                "使用 database_initializer 初始化数据库表结构",
                "使用 data_collection_guide 获取手工数据收集指导"
            ]
        }


async def sql_query_executor(
    query: str,
    query_purpose: str,
    database_type: str = "postgresql",
    connection_string: Optional[str] = None,
    limit_rows: int = 1000,
    explain_plan: bool = False
) -> Dict[str, Any]:
    """
    执行SQL查询并返回结果
    
    Args:
        query: 要执行的SQL查询语句
        query_purpose: 查询目的说明 (用于结果解释)
        database_type: 数据库类型
        connection_string: 数据库连接字符串，如果不提供则使用默认配置
        limit_rows: 最大返回行数限制
        explain_plan: 是否显示执行计划
    
    Returns:
        包含查询结果和分析建议的字典
    """
    
    try:
        # 安全检查SQL语句
        safety_check = _validate_sql_safety(query)
        if not safety_check["is_safe"]:
            return {
                "success": False,
                "error": f"SQL安全检查失败: {safety_check['reason']}",
                "suggestions": [
                    "仅使用SELECT语句进行查询",
                    "避免使用DELETE、UPDATE、DROP等危险操作",
                    "联系数据库管理员获取帮助"
                ]
            }
        
        # 添加LIMIT限制（如果查询中没有）
        modified_query = _add_limit_to_query(query, limit_rows)
        
        # 获取连接参数
        conn_params = _get_connection_params(connection_string)
            
        # 执行真实查询
        query_result = _execute_real_query(conn_params, modified_query, query_purpose)
        
        # 生成数据分析建议
        analysis_suggestions = _generate_analysis_suggestions(query_result, query_purpose)
        
        # 生成后续分析工具建议
        next_tools = _suggest_next_analysis_tools(query_result, query_purpose)
        
        return {
            "success": True,
            "data": {
                "查询信息": {
                    "查询目的": query_purpose,
                    "执行SQL": modified_query,
                    "返回行数": query_result.get("row_count", 0),
                    "执行时间": query_result.get("execution_time", "< 1秒"),
                    "连接类型": "真实连接",
                    "连接配置": f"{conn_params['host']}:{conn_params['port']}"
                },
                "查询结果": query_result["data"],
                "数据统计": query_result.get("statistics", {}),
                "分析建议": analysis_suggestions,
                "质量评估": _assess_data_quality(query_result)
            },
            "suggested_next_steps": next_tools
        }
        
    except Exception as e:
        logging.error(f"SQL查询执行失败: {str(e)}")
        return {
            "success": False,
            "error": f"查询执行失败: {str(e)}",
            "troubleshooting": [
                "检查SQL语法是否正确",
                "确认表名和字段名是否存在",
                "验证数据库连接是否正常",
                "使用 database_schema_explorer 重新查看表结构",
                "如果表不存在，使用 database_initializer 初始化数据库"
            ]
        }


def _query_real_schema(conn_params: Dict[str, Any], table_pattern: Optional[str], include_columns: bool) -> Dict[str, Any]:
    """查询真实数据库的schema信息"""
    
    conn = None
    try:
        # 使用psycopg2连接数据库
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 查询所有表
        table_query = """
        SELECT table_name, table_type 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        
        if table_pattern:
            # 转换通配符模式
            postgres_pattern = table_pattern.replace('*', '%').replace('?', '_')
            table_query += f" AND table_name LIKE %s"
            cursor.execute(table_query, (postgres_pattern,))
        else:
            cursor.execute(table_query)
        
        tables_result = cursor.fetchall()
        
        schema_info = {
            "database_type": "postgresql",
            "tables": {},
            "total_tables": len(tables_result),
            "schema_timestamp": "real-time"
        }
        
        for table_row in tables_result:
            table_name = table_row['table_name']
            table_info = {
                "description": f"表类型: {table_row['table_type']}",
                "columns": {}
            }
            
            if include_columns:
                # 查询列信息
                columns_query = """
                SELECT column_name, data_type, is_nullable, column_default,
                       character_maximum_length, numeric_precision, numeric_scale
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
                """
                
                cursor.execute(columns_query, (table_name,))
                columns_result = cursor.fetchall()
                
                for col_row in columns_result:
                    col_name = col_row['column_name']
                    data_type = col_row['data_type']
                    
                    # 构建完整的类型信息
                    if col_row['character_maximum_length']:
                        data_type += f"({col_row['character_maximum_length']})"
                    elif col_row['numeric_precision']:
                        data_type += f"({col_row['numeric_precision']}"
                        if col_row['numeric_scale']:
                            data_type += f",{col_row['numeric_scale']}"
                        data_type += ")"
                    
                    table_info["columns"][col_name] = {
                        "type": data_type.upper(),
                        "nullable": col_row['is_nullable'] == 'YES',
                        "default": col_row['column_default'],
                        "description": f"{data_type.upper()} 字段"
                    }
            
            schema_info["tables"][table_name] = table_info
        
        return schema_info
        
    except Exception as e:
        logging.error(f"查询真实schema失败: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


def _execute_real_query(conn_params: Dict[str, Any], query: str, query_purpose: str) -> Dict[str, Any]:
    """执行真实的SQL查询"""
    
    conn = None
    try:
        # 使用psycopg2连接数据库
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行查询
        cursor.execute(query)
        result = cursor.fetchall()
        
        # 计算执行时间
        execution_time = round(time.time() - start_time, 3)
        
        # 转换结果为字典列表
        data = []
        for row in result:
            row_dict = {}
            for key, value in row.items():
                # 处理特殊数据类型
                if hasattr(value, 'isoformat'):  # datetime对象
                    row_dict[key] = value.isoformat()
                elif isinstance(value, (int, float, str, bool)) or value is None:
                    row_dict[key] = value
                else:
                    row_dict[key] = str(value)
            data.append(row_dict)
        
        # 生成统计信息
        statistics = {}
        if data:
            numeric_columns = []
            for key, value in data[0].items():
                if isinstance(value, (int, float)):
                    numeric_columns.append(key)
            
            for col in numeric_columns:
                values = [row[col] for row in data if row[col] is not None]
                if values:
                    statistics[col] = {
                        "总计": sum(values),
                        "平均值": round(sum(values) / len(values), 2),
                        "最大值": max(values),
                        "最小值": min(values),
                        "记录数": len(values)
                    }
        
        return {
            "data": data,
            "row_count": len(data),
            "execution_time": f"{execution_time}秒",
            "statistics": statistics
        }
        
    except Exception as e:
        logging.error(f"执行真实查询失败: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


def _add_limit_to_query(query: str, limit_rows: int) -> str:
    """给查询添加LIMIT限制"""
    query_upper = query.upper().strip()
    
    # 如果查询已经包含LIMIT，不重复添加
    if 'LIMIT' in query_upper:
        return query
    
    # 如果是SELECT查询，添加LIMIT
    if query_upper.startswith('SELECT'):
        return f"{query.rstrip(';')} LIMIT {limit_rows}"
    
    return query


def _simulate_schema_query(database_type: str, table_pattern: Optional[str], include_columns: bool) -> Dict[str, Any]:
    """模拟数据库schema查询"""
    
    # 跨境电商典型表结构
    ecommerce_tables = {
        "orders": {
            "description": "订单主表",
            "columns": {
                "order_id": {"type": "VARCHAR(50)", "description": "订单ID", "primary_key": True},
                "customer_id": {"type": "VARCHAR(50)", "description": "客户ID"},
                "order_date": {"type": "DATETIME", "description": "订单日期"},
                "order_status": {"type": "VARCHAR(20)", "description": "订单状态"},
                "total_amount": {"type": "DECIMAL(10,2)", "description": "订单总金额"},
                "currency": {"type": "VARCHAR(3)", "description": "货币类型"},
                "platform": {"type": "VARCHAR(20)", "description": "销售平台"},
                "market": {"type": "VARCHAR(20)", "description": "目标市场"},
                "shipping_fee": {"type": "DECIMAL(8,2)", "description": "运费"},
                "tax_amount": {"type": "DECIMAL(8,2)", "description": "税费"},
                "created_at": {"type": "TIMESTAMP", "description": "创建时间"},
                "updated_at": {"type": "TIMESTAMP", "description": "更新时间"}
            } if include_columns else {}
        },
        "order_items": {
            "description": "订单商品明细表",
            "columns": {
                "item_id": {"type": "BIGINT", "description": "明细ID", "primary_key": True},
                "order_id": {"type": "VARCHAR(50)", "description": "订单ID", "foreign_key": "orders.order_id"},
                "product_id": {"type": "VARCHAR(50)", "description": "商品ID"},
                "sku": {"type": "VARCHAR(100)", "description": "商品SKU"},
                "quantity": {"type": "INT", "description": "购买数量"},
                "unit_price": {"type": "DECIMAL(8,2)", "description": "单价"},
                "discount_amount": {"type": "DECIMAL(8,2)", "description": "折扣金额"},
                "total_price": {"type": "DECIMAL(10,2)", "description": "小计金额"}
            } if include_columns else {}
        },
        "products": {
            "description": "商品信息表",
            "columns": {
                "product_id": {"type": "VARCHAR(50)", "description": "商品ID", "primary_key": True},
                "product_name": {"type": "VARCHAR(200)", "description": "商品名称"},
                "category": {"type": "VARCHAR(50)", "description": "商品分类"},
                "brand": {"type": "VARCHAR(50)", "description": "品牌"},
                "cost_price": {"type": "DECIMAL(8,2)", "description": "成本价"},
                "selling_price": {"type": "DECIMAL(8,2)", "description": "售价"},
                "weight": {"type": "DECIMAL(8,3)", "description": "重量(kg)"},
                "dimensions": {"type": "VARCHAR(50)", "description": "尺寸"},
                "status": {"type": "VARCHAR(20)", "description": "商品状态"}
            } if include_columns else {}
        },
        "customers": {
            "description": "客户信息表",
            "columns": {
                "customer_id": {"type": "VARCHAR(50)", "description": "客户ID", "primary_key": True},
                "customer_name": {"type": "VARCHAR(100)", "description": "客户姓名"},
                "email": {"type": "VARCHAR(100)", "description": "邮箱"},
                "country": {"type": "VARCHAR(50)", "description": "国家"},
                "registration_date": {"type": "DATE", "description": "注册日期"},
                "customer_type": {"type": "VARCHAR(20)", "description": "客户类型"},
                "total_orders": {"type": "INT", "description": "总订单数"},
                "total_spent": {"type": "DECIMAL(12,2)", "description": "总消费金额"}
            } if include_columns else {}
        },
        "inventory": {
            "description": "库存管理表",
            "columns": {
                "sku": {"type": "VARCHAR(100)", "description": "商品SKU", "primary_key": True},
                "warehouse": {"type": "VARCHAR(50)", "description": "仓库位置"},
                "stock_quantity": {"type": "INT", "description": "库存数量"},
                "reserved_quantity": {"type": "INT", "description": "预留数量"},
                "reorder_point": {"type": "INT", "description": "补货点"},
                "last_updated": {"type": "TIMESTAMP", "description": "最后更新时间"}
            } if include_columns else {}
        }
    }
    
    # 根据table_pattern过滤表
    filtered_tables = {}
    if table_pattern:
        import fnmatch
        for table_name, table_info in ecommerce_tables.items():
            if fnmatch.fnmatch(table_name, table_pattern):
                filtered_tables[table_name] = table_info
    else:
        filtered_tables = ecommerce_tables
    
    return {
        "database_type": database_type,
        "tables": filtered_tables,
        "total_tables": len(filtered_tables),
        "schema_timestamp": "模拟数据"
    }


def _generate_ecommerce_schema_suggestions(schema_info: Dict[str, Any]) -> Dict[str, Any]:
    """为跨境电商生成schema建议"""
    
    tables = schema_info.get("tables", {})
    table_names = list(tables.keys())
    
    suggestions = {
        "数据完整性建议": [],
        "性能优化建议": [],
        "业务分析建议": []
    }
    
    # 检查关键表是否存在
    key_tables = ["orders", "order_items", "products", "customers"]
    missing_tables = [table for table in key_tables if table not in table_names]
    
    if missing_tables:
        suggestions["数据完整性建议"].append(f"建议添加关键表: {', '.join(missing_tables)}")
    
    # 检查是否有订单相关表
    if any("order" in name.lower() for name in table_names):
        suggestions["业务分析建议"].append("可以进行订单趋势分析和客户购买行为分析")
        suggestions["性能优化建议"].append("为订单表的日期字段创建索引以优化时间范围查询")
    
    # 检查是否有产品相关表
    if any("product" in name.lower() for name in table_names):
        suggestions["业务分析建议"].append("可以进行商品销售分析和库存管理分析")
    
    # 检查是否有客户相关表
    if any("customer" in name.lower() or "user" in name.lower() for name in table_names):
        suggestions["业务分析建议"].append("可以进行客户细分和RFM分析")
        
    # 通用建议
    suggestions["性能优化建议"].extend([
        "为外键字段创建索引",
        "考虑对大表进行分区",
        "定期更新表统计信息"
    ])
    
    return suggestions


def _generate_sql_hints(schema_info: Dict[str, Any]) -> List[Dict[str, str]]:
    """生成SQL编写提示"""
    
    tables = schema_info.get("tables", {})
    hints = []
    
    # 基于现有表生成查询示例
    table_names = list(tables.keys())
    
    if "orders" in table_names:
        hints.append({
            "查询类型": "销售趋势分析",
            "SQL示例": "SELECT DATE(order_date) as date, COUNT(*) as order_count, SUM(total_amount) as revenue FROM orders WHERE order_date >= '2024-01-01' GROUP BY DATE(order_date) ORDER BY date",
            "说明": "按日统计订单数量和收入"
        })
    
    if "order_items" in table_names and "products" in table_names:
        hints.append({
            "查询类型": "商品销售排行",
            "SQL示例": "SELECT p.product_name, SUM(oi.quantity) as total_sold, SUM(oi.total_price) as revenue FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.product_id, p.product_name ORDER BY revenue DESC LIMIT 10",
            "说明": "获取销售额前10的商品"
        })
    
    if "customers" in table_names:
        hints.append({
            "查询类型": "客户分析",
            "SQL示例": "SELECT country, COUNT(*) as customer_count, AVG(total_spent) as avg_spent FROM customers GROUP BY country ORDER BY customer_count DESC",
            "说明": "按国家统计客户数量和平均消费"
        })
    
    # 通用查询提示
    hints.extend([
        {
            "查询类型": "数据质量检查",
            "SQL示例": "SELECT COUNT(*) as total_rows, COUNT(DISTINCT order_id) as unique_orders FROM orders",
            "说明": "检查数据重复情况"
        },
        {
            "查询类型": "表信息查询",
            "SQL示例": "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position",
            "说明": "查看数据库结构信息"
        }
    ])
    
    return hints


def _simulate_query_execution(query: str, query_purpose: str, limit_rows: int) -> Dict[str, Any]:
    """模拟SQL查询执行"""
    
    # 生成模拟数据
    mock_data = []
    
    if "orders" in query.lower():
        mock_data = [
            {"order_id": "ORD001", "platform": "Amazon", "total_amount": 156.78, "order_date": "2024-01-15"},
            {"order_id": "ORD002", "platform": "eBay", "total_amount": 89.50, "order_date": "2024-01-16"},
            {"order_id": "ORD003", "platform": "Shopify", "total_amount": 234.90, "order_date": "2024-01-16"},
            {"order_id": "ORD004", "platform": "Amazon", "total_amount": 67.20, "order_date": "2024-01-17"},
            {"order_id": "ORD005", "platform": "eBay", "total_amount": 145.60, "order_date": "2024-01-17"}
        ]
    elif "customers" in query.lower():
        mock_data = [
            {"customer_id": "CUST001", "country": "US", "total_spent": 456.78, "total_orders": 3},
            {"customer_id": "CUST002", "country": "UK", "total_spent": 234.50, "total_orders": 2},
            {"customer_id": "CUST003", "country": "DE", "total_spent": 567.90, "total_orders": 4},
            {"customer_id": "CUST004", "country": "CA", "total_spent": 123.40, "total_orders": 1},
            {"customer_id": "CUST005", "country": "AU", "total_spent": 789.10, "total_orders": 5}
        ]
    else:
        mock_data = [
            {"id": 1, "name": "示例数据1", "value": 100},
            {"id": 2, "name": "示例数据2", "value": 200},
            {"id": 3, "name": "示例数据3", "value": 150}
        ]
    
    # 应用limit限制
    limited_data = mock_data[:limit_rows]
    
    # 生成统计信息
    statistics = {}
    if limited_data and any(isinstance(v, (int, float)) for v in limited_data[0].values()):
        for key in limited_data[0].keys():
            values = [row[key] for row in limited_data if isinstance(row[key], (int, float))]
            if values:
                statistics[key] = {
                    "总计": sum(values),
                    "平均值": round(sum(values) / len(values), 2),
                    "最大值": max(values),
                    "最小值": min(values),
                    "记录数": len(values)
                }
    
    return {
        "data": limited_data,
        "row_count": len(limited_data),
        "execution_time": "0.05秒",
        "statistics": statistics
    }


def _validate_sql_safety(query: str) -> Dict[str, Any]:
    """验证SQL查询的安全性"""
    
    query_upper = query.upper().strip()
    
    # 危险关键词检查
    dangerous_keywords = [
        'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE',
        'EXEC', 'EXECUTE', 'MERGE', 'REPLACE', 'GRANT', 'REVOKE'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return {
                "is_safe": False,
                "reason": f"查询包含危险关键词: {keyword}",
                "suggestion": "仅允许使用SELECT语句进行数据查询"
            }
    
    # 检查是否为SELECT查询
    if not query_upper.startswith('SELECT') and not query_upper.startswith('WITH'):
        return {
            "is_safe": False,
            "reason": "仅支持SELECT查询语句",
            "suggestion": "请使用SELECT语句进行数据查询"
        }
    
    return {
        "is_safe": True,
        "reason": "查询安全检查通过"
    }


def _generate_analysis_suggestions(query_result: Dict[str, Any], query_purpose: str) -> List[str]:
    """根据查询结果生成分析建议"""
    
    suggestions = []
    data = query_result.get("data", [])
    row_count = query_result.get("row_count", 0)
    
    # 基于数据量的建议
    if row_count == 0:
        suggestions.append("❌ 查询未返回数据，建议检查查询条件或表中是否有数据")
    elif row_count < 10:
        suggestions.append("⚠️ 数据量较少，建议扩大查询范围或检查数据完整性")
    elif row_count >= 1000:
        suggestions.append("📊 数据量较大，建议添加更多筛选条件或使用分页查询")
    else:
        suggestions.append("✅ 数据量适中，可以进行进一步分析")
    
    # 基于查询目的的建议
    if "销售" in query_purpose or "订单" in query_purpose:
        suggestions.append("💰 建议分析销售趋势、平台对比、客户行为等维度")
        suggestions.append("📈 可以使用 chart_type_advisor 选择合适的图表展示销售数据")
    elif "客户" in query_purpose:
        suggestions.append("👥 建议分析客户地域分布、消费行为、复购率等指标")
        suggestions.append("🎯 可以使用 business_problem_analyzer 获取问题分析指导")
    elif "库存" in query_purpose:
        suggestions.append("📦 建议分析库存周转、缺货风险、成本控制等方面")
    
    # 基于数据特征的建议
    if data:
        # 检查是否有时间字段
        time_fields = [k for k in data[0].keys() if 'date' in k.lower() or 'time' in k.lower()]
        if time_fields:
            suggestions.append(f"📅 发现时间字段 {time_fields[0]}，建议进行时间趋势分析")
        
        # 检查是否有金额字段
        amount_fields = [k for k in data[0].keys() if any(word in k.lower() for word in ['amount', 'price', 'cost', 'spent'])]
        if amount_fields:
            suggestions.append(f"💵 发现金额字段 {amount_fields[0]}，建议进行财务分析")
    
    return suggestions


def _suggest_next_analysis_tools(query_result: Dict[str, Any], query_purpose: str) -> List[str]:
    """根据查询结果推荐后续分析工具"""
    
    tools = []
    
    # 基础分析工具
    tools.append("📊 使用 insight_generator 从查询结果中提取业务洞察")
    tools.append("📈 使用 chart_type_advisor 选择合适的图表类型展示数据")
    tools.append("📝 使用 insight_generator 解读分析结果的业务含义")
    
    # 基于查询目的推荐工具
    if "对比" in query_purpose or "比较" in query_purpose:
        tools.append("🔍 使用 sales_comparison_analyzer 进行深度对比分析")
    
    if "趋势" in query_purpose or "变化" in query_purpose:
        tools.append("📅 使用 analysis_method_recommender 获取趋势分析方法")
    
    # 后续行动建议
    tools.append("🎯 使用 action_recommender 获取基于数据的行动建议")
    tools.append("❓ 使用 follow_up_questions 生成进一步分析的问题")
    
    return tools


def _assess_data_quality(query_result: Dict[str, Any]) -> Dict[str, str]:
    """评估查询结果的数据质量"""
    
    data = query_result.get("data", [])
    row_count = query_result.get("row_count", 0)
    
    assessment = {}
    
    # 数据完整性评估
    if row_count == 0:
        assessment["完整性"] = "无数据 - 需要检查数据源"
    elif row_count < 10:
        assessment["完整性"] = "数据量少 - 可能影响分析准确性"
    else:
        assessment["完整性"] = "数据量充足 - 适合进行分析"
    
    # 数据新鲜度评估
    if data:
        time_fields = [k for k in data[0].keys() if 'date' in k.lower() or 'time' in k.lower()]
        if time_fields:
            assessment["时效性"] = "包含时间信息 - 可进行时间序列分析"
        else:
            assessment["时效性"] = "缺少时间字段 - 建议检查数据时效性"
    
    # 数据多样性评估
    if data and len(data) > 1:
        # 检查是否有分类字段
        categorical_fields = []
        for key in data[0].keys():
            values = [row[key] for row in data[:10]]  # 检查前10行
            unique_values = len(set(str(v) for v in values))
            if unique_values > 1 and unique_values < len(values):
                categorical_fields.append(key)
        
        if categorical_fields:
            assessment["多样性"] = f"发现分类字段 {categorical_fields[0]} - 适合分组分析"
        else:
            assessment["多样性"] = "数据相对单一 - 建议扩大查询范围"
    
    return assessment 
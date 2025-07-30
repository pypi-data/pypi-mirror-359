# 智能BI助手 MCP

专为单一数据源（查库）设计的高效数据分析助手，**已优化为7个核心工具**，消除功能重叠，简化使用流程！

## 🚀 新版本亮点 (FastMCP + 优化架构)

- ✨ **架构优化**: 从14个工具精简到7个核心工具，消除功能重叠
- 🧠 **智能分析**: 新增智能问题理解器，自动识别问题类型和分析路径
- 🔧 **开箱即用**: 基于fastmcp框架，无需复杂配置
- 📡 **原生协议支持**: 完整的MCP协议实现，兼容Claude Desktop等客户端
- 🌐 **多传输模式**: 支持STDIO和HTTP两种传输方式
- 🛡️ **类型安全**: 使用fastmcp的类型推断和验证
- 📊 **单一数据源优化**: 专门针对查库场景优化，简化数据获取流程

## 📊 优化后的7个核心工具

### 🔍 智能问题理解
- **business_problem_analyzer**: 智能业务问题分析器
  - 自动识别问题类型（排名、对比、趋势、关联等）
  - 智能拆解复杂问题为子问题
  - 自动规划分析路径和步骤
  - 提取查询要素和时间范围

### 📊 数据获取工具
- **database_schema_explorer**: 数据库结构探索器
  - 探索数据库表结构和字段信息
  - 为SQL查询提供基础信息
- **sql_query_executor**: SQL查询执行器
  - 安全执行SQL查询获取数据
  - 支持各种业务分析场景

### 📈 专业分析工具
- **sales_comparison_analyzer**: 销售对比分析器
  - 完整的销售对比分析流程
  - 自动生成时间对比SQL
  - 集成查询、分析、洞察生成
  - 支持周对周、月对月、年对年对比

### 💡 洞察与决策工具
- **insight_generator**: 增强版洞察生成器
  - 从分析结果中提取关键业务洞察
  - 整合结果解读和数据故事构建功能
  - 提供多层次的业务价值分析
- **action_recommender**: 增强版行动建议器
  - 基于洞察提供具体的行动建议和实施计划
  - 整合后续问题生成功能
  - 提供完整的决策支持
- **chart_type_advisor**: 图表类型顾问
  - 根据数据类型和分析目的推荐最适合的图表类型
  - 帮助选择最佳的数据可视化方案

## 🎯 简化后的使用流程

```
1. business_problem_analyzer → 智能理解问题需求
2. database_schema_explorer → 探索可用数据结构  
3. sql_query_executor/sales_comparison_analyzer → 获取分析数据
4. insight_generator → 生成深度洞察
5. action_recommender → 制定行动方案
6. chart_type_advisor → 选择合适的可视化方式
```

对比优化前的复杂流程（12步骤），现在只需6步即可完成完整分析！

## 📈 优化效果对比

| 指标 | 优化前 | 优化后 | 改善 |
|------|-------|-------|------|
| 工具数量 | 14个 | 7个 | -50% |
| 使用步骤 | 12步 | 6步 | -50% |
| 功能重叠 | 严重 | 最小化 | ✅ |
| 学习成本 | 高 | 低 | ✅ |
| 单一数据源适配 | 一般 | 优秀 | ✅ |

## 🛠️ 安装和运行

### 1. 安装依赖

```bash
# 使用uv (推荐)
uv install

# 或使用pip
pip install -e .
```

### 2. 启动服务器

#### STDIO模式 (Claude Desktop等客户端)
```bash
# 方式1: 直接运行
python main.py

# 方式2: 使用fastmcp CLI
fastmcp run main.py

# 方式3: 使用项目脚本
business-bi-mcp
```

#### HTTP模式 (Web/API客户端)
```bash
# 启动HTTP服务器
python main_sse.py

# 访问地址: http://127.0.0.1:8000/mcp/
```

### 3. Claude Desktop配置

在Claude Desktop的配置文件中添加：

```json
{
  "mcpServers": {
    "business-bi-mcp": {
      "command": "uv",
      "args": ["run", "python", "/path/to/bi_mcp/main.py"]
    }
  }
}
```

## 📱 使用示例

### 智能问题分析

```python
# 使用新的智能问题分析器
result = await client.call_tool("business_problem_analyzer_tool", {
    "question": "分析最近一周销售额比上周下降的原因",
    "business_context": "跨境电商"
})

# 自动识别为对比分析类型
# 自动拆解为子问题
# 自动规划分析路径
```

### 销售对比分析

```python
# 使用销售对比分析器进行完整分析
result = await client.call_tool("sales_comparison_analyzer_tool", {
    "question": "最近一周的销售额比上周怎么样？",
    "comparison_type": "week_over_week",
    "business_context": "跨境电商"
})

# 自动完成：问题理解 → 数据查询 → 结果分析 → 洞察生成 → 行动建议
```

### Python客户端完整示例

```python
from fastmcp import Client
import asyncio

async def bi_analysis_demo():
    async with Client("http://127.0.0.1:8000/mcp/") as client:
        # 1. 智能问题理解
        problem_analysis = await client.call_tool("business_problem_analyzer_tool", {
            "question": "为什么这个月的订单转化率下降了？",
            "business_context": "跨境电商平台"
        })
        
        # 2. 探索数据结构
        schema_info = await client.call_tool("database_schema_explorer_tool", {
            "table_pattern": "orders%"
        })
        
        # 3. 执行数据查询
        query_result = await client.call_tool("sql_query_executor_tool", {
            "query": "SELECT DATE(order_date), COUNT(*), SUM(total_amount) FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY DATE(order_date)",
            "query_purpose": "分析最近30天的订单趋势"
        })
        
        # 4. 生成洞察
        insights = await client.call_tool("insight_generator_tool", {
            "analysis_data": str(query_result),
            "business_goal": "提高订单转化率",
            "stakeholder_interests": "运营团队",
            "include_story": True
        })
        
        # 5. 制定行动计划
        actions = await client.call_tool("action_recommender_tool", {
            "insights": str(insights),
            "business_constraints": "有限预算",
            "implementation_capacity": "小团队",
            "include_follow_up": True
        })

asyncio.run(bi_analysis_demo())
```

## 🧪 测试

运行测试客户端验证服务器功能：

```bash
# 确保服务器运行在HTTP模式
python main_sse.py

# 在另一个终端运行测试
python test_fastmcp_client.py
```

## 📦 项目结构

```
bi_mcp/
├── main.py              # STDIO模式入口
├── main_sse.py          # HTTP模式入口
├── core/
│   └── server.py        # 优化后的FastMCP服务器配置
├── tools/               # 业务工具实现
│   ├── analysis.py      # 业务分析工具 (部分功能已整合)
│   ├── insight.py       # 增强版洞察生成工具
│   ├── recommendation.py # 增强版推荐工具  
│   ├── database_tools.py # 数据库工具
│   ├── universal_question_analyzer.py # 智能问题分析器
│   └── sales_comparison_analyzer.py # 销售对比分析器
└── test_fastmcp_client.py # 测试客户端
```

## 🔄 从传统MCP迁移

如果您之前使用的是传统MCP库版本，新版本提供了以下改进：

### 主要变化
- **导入**: `from mcp.server.fastmcp import FastMCP` → `from fastmcp import FastMCP`
- **工具注册**: 使用`@mcp.tool`装饰器，更简洁的语法
- **HTTP服务**: 无需手动实现FastAPI路由，fastmcp提供原生支持
- **依赖**: 主要依赖简化为`fastmcp>=2.10.1`

### 兼容性
- 所有业务工具功能保持不变
- 所有客户端接口保持兼容
- 传统依赖移动到`legacy`可选依赖组

## 📚 更多资源

- [FastMCP官方文档](https://github.com/jlowin/fastmcp)
- [MCP协议规范](https://spec.modelcontextprotocol.io/)
- [Claude Desktop集成指南](https://claude.ai/docs)

## 🤝 贡献

欢迎提交Issues和Pull Requests！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件 
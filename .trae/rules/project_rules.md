# 新建MCP项目规则

## 项目概述

本规则用于指导在mcp项目中新建和管理MCP（Model Context Protocol）工具。MCP工具是基于Python实现的服务，通过标准输入输出与调用方通信，提供特定功能的工具接口。

## 目录结构

### 基础目录结构

```
mcp/
├── {工具名}_mcp/              # 工具目录，命名格式：{工具名}_mcp
│   ├── {工具名}_mcp.py        # 主文件，命名格式：{工具名}_mcp.py
│   └── [可选] 其他辅助模块.py  # 如需要，可添加辅助模块
└── ... 其他工具目录
```

### 命名规范

1. **工具目录名**：使用小写字母和下划线，格式为 `{工具名}_mcp`
2. **主文件名**：与目录名相同，格式为 `{工具名}_mcp.py`
3. **类名**：使用驼峰命名法（CamelCase）
4. **函数名**：使用小写字母和下划线（snake_case）
5. **变量名**：使用小写字母和下划线（snake_case）

## 代码结构

### 1. 基础导入

```python
#!/usr/bin/env python3
import asyncio
import logging
import sys
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
```

### 2. 日志配置

```python
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{工具名}-server")
```

### 3. 服务器实例创建

```python
# 创建服务器实例
server = Server("{工具名}")
```

### 4. 工具定义与实现

#### 4.1 工具列表定义

使用 `@server.list_tools()`装饰器定义可用工具列表：

```python
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """返回可用工具列表"""
    return [
        Tool(
            name="{工具名}",
            description="{工具描述}",
            inputSchema={
                "type": "object",
                "properties": {
                    "{参数名}": {
                        "type": "{参数类型}",
                        "description": "{参数描述}"
                    }
                },
                "required": ["{必填参数}"]
            },
        ),
        # 可添加多个工具
    ]
```

#### 4.2 工具处理函数

实现每个工具的具体处理逻辑：

```python
async def {工具处理函数名}({参数}) -> dict:
    """{工具描述}"""
    try:
        # 实现工具逻辑
        return {
            "{返回字段}": {返回值},
            "message": "操作成功"
        }
    except Exception as e:
        logger.error(f"{操作}时发生错误: {str(e)}")
        return {
            "{返回字段}": {默认值},
            "message": f"{操作}时发生错误: {str(e)}"
        }
```

#### 4.3 工具调用处理

使用 `@server.call_tool()`装饰器处理工具调用：

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """处理工具调用"""
    if name == "{工具名}":
        if not arguments or "{参数名}" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 {参数名} 参数"}))]
        {参数} = arguments["{参数名}"]
        result = await {工具处理函数名}({参数})
        return [TextContent(type="text", text=str(result))]
    # 可添加多个工具的处理
    else:
        raise ValueError(f"未知工具: {name}")
```

### 5. 主函数

```python
async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## 最佳实践

### 1. 代码质量

- 使用类型注解提高代码可读性和IDE支持
- 实现完整的异常处理，确保服务稳定运行
- 添加适当的文档字符串，说明函数功能和参数

### 2. 工具设计

- 每个工具应专注于单一功能，保持职责清晰
- 工具名称应简洁明了，反映其功能
- 输入参数应使用JSON Schema明确定义，确保参数验证
- 返回值应包含明确的状态信息和结果数据

### 3. 性能与可靠性

- 对于耗时操作，考虑使用异步处理
- 合理使用日志记录，便于问题排查
- 避免在工具中执行长时间阻塞操作

### 4. 扩展性

- 如功能复杂，可将逻辑拆分为多个模块
- 保持接口设计的一致性，便于维护和扩展

## 示例项目结构

以创建一个名为 `demo`的MCP工具为例：

```
mcp/
├── demo_mcp/             # 工具目录
│   ├── demo_mcp.py       # 主文件
│   └── helper.py         # 辅助模块（可选）

└── ... 其他工具目录
```

## 验证与测试

### 基本验证步骤

1. 确保代码能正常运行：`python {工具名}_mcp.py`
2. 验证工具列表返回正确：发送 `{"type": "list_tools"}`到标准输入
3. 验证工具调用功能：发送工具调用请求到标准输入

### 测试示例

```python
# 测试工具列表请求
{"type": "list_tools"}

# 测试工具调用请求
{
  "type": "call_tool",
  "name": "{工具名}",
  "arguments": {
    "{参数名}": "{参数值}"
  }
}
```

## 总结

遵循本规则创建的MCP工具将具有一致的结构和接口，便于管理和使用。每个MCP工具应专注于提供特定功能的工具接口，通过标准输入输出与调用方通信，实现功能的模块化和复用。

在开发过程中，应注重代码质量、工具设计的合理性和服务的可靠性，确保MCP工具能够稳定、高效地运行。

# CLI执行MCP工具实现计划

## 项目概述
创建一个MCP工具，允许AI直接执行CLI指令，默认使用PowerShell 7，如不存在则回退到Windows默认PowerShell。

## 实现步骤

### 1. 创建项目目录结构
- 创建 `cli_mcp` 目录
- 在目录中创建 `cli_mcp.py` 主文件

### 2. 实现核心功能
- 导入必要的模块（asyncio、subprocess、os等）
- 配置日志
- 创建服务器实例
- 定义工具列表，包含执行CLI命令的工具
- 实现命令执行逻辑，包括PowerShell 7检测和回退机制
- 实现工具调用处理函数
- 实现主函数

### 3. 功能特性
- 执行CLI命令并返回结果
- 自动检测PowerShell 7是否存在
- 如PowerShell 7不存在，使用Windows默认PowerShell
- 支持命令执行超时处理
- 完整的错误处理和日志记录

### 4. 技术实现细节
- 使用 `subprocess` 模块执行命令
- 使用 `os.path.exists` 检测PowerShell 7路径
- 支持异步执行命令
- 返回命令执行结果、退出码和错误信息

## 实施检查清单
1. 创建 `cli_mcp` 目录
2. 创建 `cli_mcp.py` 文件
3. 实现基础导入和日志配置
4. 创建服务器实例
5. 实现工具列表定义
6. 实现命令执行函数
7. 实现工具调用处理函数
8. 实现主函数
9. 测试工具功能

## 预期工具接口
工具名称：`run_command`
- 参数：
  - `command`: 要执行的命令字符串
  - `timeout`: 可选，命令执行超时时间（秒）
- 返回值：
  - `stdout`: 命令输出
  - `stderr`: 错误输出
  - `returncode`: 退出码
  - `message`: 执行状态消息
  - `powershell_version`: 使用的PowerShell版本

这个实现将遵循项目的命名规范和代码结构，确保工具的可靠性和易用性。
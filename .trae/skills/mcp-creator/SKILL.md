---
name: "mcp-creator"
description: "Guides users through creating MCP (Model Context Protocol) tools following project rules. Invoke when user wants to create a new MCP tool or needs instructions on MCP tool structure and implementation for both Python and JavaScript."
---

# MCP Creator

This skill provides comprehensive guidance for creating MCP (Model Context Protocol) tools in the project, covering both Python and JavaScript implementations following the established directory structures and code conventions.

## When to Use

Invoke this skill when:
- User wants to create a new MCP tool (Python or JavaScript)
- User needs instructions on MCP tool structure for different languages
- User asks about MCP tool implementation best practices
- User needs help with MCP tool naming conventions
- User wants to understand the MCP tool development workflow
- User needs guidance on JavaScript MCP tool creation with CDP integration

## MCP Tool Structure

### Python MCP Tool Structure

```
mcp/
├── {tool-name}_mcp/              # Tool directory, format: {tool-name}_mcp
│   ├── {tool-name}_mcp.py        # Main file, format: {tool-name}_mcp.py
│   └── [optional] helper modules.py  # Optional helper modules
└── ... other tool directories
```

### JavaScript MCP Tool Structure

```
xiaozhi-mcp/
├── src/
│   ├── index.js              # MCP server entry point
│   ├── cdp-client.js         # CDP client (connects to target application)
│   ├── utils.js              # Utility functions
│   └── tools/                # Tools directory
│       ├── get-page-info.js      # Get page information
│       ├── scan-elements.js      # Scan page elements
│       ├── click-element.js      # Click element
│       ├── input-text.js         # Input text
│       ├── scroll-page.js        # Scroll page
│       └── get-messages.js       # Get chat messages
├── package.json
└── mcp-config.json           # MCP configuration (optional)
```

### Naming Conventions

#### Python Naming Conventions
1. **Tool directory**: Use lowercase letters and underscores, format: `{tool-name}_mcp`
2. **Main file**: Same as directory name, format: `{tool-name}_mcp.py`
3. **Class names**: Use CamelCase
4. **Function names**: Use snake_case (lowercase with underscores)
5. **Variable names**: Use snake_case (lowercase with underscores)

#### JavaScript Naming Conventions
1. **File names**: Use kebab-case (lowercase with hyphens), e.g., `get-page-info.js`
2. **Tool names**: Use snake_case in tool definition, e.g., `get_page_info`
3. **Function names**: Use camelCase
4. **Variable names**: Use camelCase

## Python MCP Tool Implementation

### 1. Basic Imports

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

### 2. Log Configuration

```python
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{tool-name}-server")

# Create server instance
server = Server("{tool-name}")
```

### 3. Tool Implementation Functions

```python
async def {tool-function}(parameters) -> dict:
    """{Tool description}
    
    Args:
        parameters: Tool parameters
        
    Returns:
        dict: Tool execution result
    """
    try:
        # Implement tool logic
        return {
            "result": {result},
            "message": "Operation successful"
        }
    except Exception as e:
        logger.error(f"Error during {operation}: {str(e)}")
        return {
            "result": {default_value},
            "message": f"Error during {operation}: {str(e)}"
        }
```

### 4. Tool List Definition

```python
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return available tools list"""
    return [
        Tool(
            name="{tool-name}",
            description="{Tool description}",
            inputSchema={
                "type": "object",
                "properties": {
                    "{parameter-name}": {
                        "type": "{parameter-type}",
                        "description": "{Parameter description}"
                    }
                },
                "required": ["{required-parameter}"]
            },
        ),
        # Add more tools if needed
    ]
```

### 5. Tool Call Handling

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls"""
    if name == "{tool-name}":
        if not arguments or "{parameter-name}" not in arguments:
            return [TextContent(type="text", text=str({"error": "Missing {parameter-name} parameter"}))]
        {parameter} = arguments["{parameter-name}"]
        result = await {tool-function}({parameter})
        return [TextContent(type="text", text=str(result))]
    # Add more tool handlers if needed
    else:
        raise ValueError(f"Unknown tool: {name}")
```

### 6. Main Function

```python
async def main():
    """Main function"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## JavaScript MCP Tool Implementation

### 1. Project Initialization

```bash
npm init -y
npm install @modelcontextprotocol/sdk chrome-remote-interface
```

### 2. Server Entry Point (index.js)

```javascript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

// Import tools
import { getPageInfo } from './tools/get-page-info.js';
import { scanElements } from './tools/scan-elements.js';
// ... other tools

async function main() {
  // Create server instance
  const server = new Server(
    {
      name: 'your-mcp-name',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Register tool call handler
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      let result;

      switch (name) {
        case 'get_page_info':
          result = await getPageInfo.handler(cdpClient, args || {});
          break;
        case 'scan_elements':
          result = await scanElements.handler(cdpClient, args || {});
          break;
        // ... other tools
        default:
          return {
            content: [{ type: 'text', text: `未知的工具: ${name}` }],
            isError: true
          };
      }

      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: JSON.stringify({ success: false, error: error.message }, null, 2) }],
        isError: true
      };
    }
  });

  // Register tool list handler ⚠️ Must use ListToolsRequestSchema
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: 'get_page_info',
          description: '获取页面信息',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        // ... other tool definitions
      ]
    };
  });

  // Start server
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(error => {
  console.error('启动失败:', error);
  process.exit(1);
});
```

### 3. Create Tool (tools/your-tool.js)

```javascript
export const yourTool = {
  name: 'your_tool_name',
  description: '工具描述',

  async handler(cdpClient, args) {
    // Parse parameters
    const { param1, param2 } = args;

    try {
      // Use cdpClient.evaluate to execute JavaScript
      const result = await cdpClient.evaluate(`
        (function(param1, param2) {
          // Code executed in target application context
          return {
            success: true,
            data: '结果数据'
          };
        })(${JSON.stringify(param1)}, ${JSON.stringify(param2)})
      `);

      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
};
```

### 4. MCP Configuration (mcp-config.json)

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "node",
      "args": ["D:/path/to/your-mcp/src/index.js"],
      "env": {
        "CUSTOM_VAR": "value"
      }
    }
  }
}
```

## Key Best Practices

### JavaScript MCP Specific Best Practices

#### 1. Correct Schema Import

```javascript
// ❌ Wrong: Using string format will cause errors
server.setRequestHandler('tools/list', async () => { ... });

// ✅ Correct: Use Schema constant
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

server.setRequestHandler(ListToolsRequestSchema, async () => { ... });
```

#### 2. Module System Consistency

**package.json must be set to ES Module:**
```json
{
  "type": "module"
}
```

**Use import/export for module system:**
```javascript
// ✅ ES Module
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
export const tool = { ... };

// ❌ CommonJS (will cause errors)
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
module.exports = { ... };
```

#### 3. Cross-context Data Passing

Code executed in `cdpClient.evaluate` runs in the target application context:

```javascript
// ❌ External variables cannot be directly accessed
const externalVar = 'hello';

const result = await cdpClient.evaluate(`
  function() {
    console.log(externalVar);  // ❌ undefined - external variable not accessible
    return externalVar;        // ❌ undefined
  }
`);

// ✅ Correct way: Pass through function parameters
const result = await cdpClient.evaluate(`
  (function(arg) {
    console.log(arg);  // ✅ 'hello'
    return arg;        // ✅ 'hello'
  })(${JSON.stringify(externalVar)})
`);
```

#### 4. JSON.stringify Handling

Properly serialize complex data types:

```javascript
// ✅ Simple types
await cdpClient.evaluate(`(function(x) { return x; })(${JSON.stringify('hello')})`);

// ✅ Object types
const obj = { name: 'test', value: 123 };
await cdpClient.evaluate(`(function(x) { return x; })(${JSON.stringify(obj)})`);

// ✅ Array types
const arr = [1, 2, 3];
await cdpClient.evaluate(`(function(x) { return x; })(${JSON.stringify(arr)})`);

// ❌ Direct variable passing (invalid)
await cdpClient.evaluate(`(function(x) { return x; })(obj)`);  // obj doesn't exist in target context
```

#### 5. Selector Validation

CSS selectors in tools must match the actual DOM structure of the target application:

```javascript
// ❌ Wrong selector
const messageRows = document.querySelectorAll('.msg_row');  // Returns 0 elements

// ✅ Correct selector (needs testing first)
const messageRows = document.querySelectorAll('.msg_box');  // Correct class name
```

**Debug tip:** Test selectors in the target application's DevTools console first.

#### 6. Asynchronous Handling

```javascript
// ❌ Error: Async inside evaluate needs Promise
const result = await cdpClient.evaluate(`
  function() {
    const data = fetchData();  // If fetchData is async
    return data;              // Will return Promise instead of result
  }
`);

// ✅ Correct: Handle async inside evaluate
const result = await cdpClient.evaluate(`
  (async function() {
    const data = await fetchData();
    return data;
  })()
`);
```

#### 7. Error Handling

```javascript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await executeTool(request.params);
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
    };
  } catch (error) {
    // ✅ Return error information
    return {
      content: [{ type: 'text', text: JSON.stringify({ success: false, error: error.message }, null, 2) }],
      isError: true
    };
  }
});
```

#### 8. Tool Return Format

```javascript
// ✅ Standard success return
return {
  success: true,
  data: { /* Your data */ }
};

// ✅ Standard error return
return {
  success: false,
  error: 'Error description'
};

// ❌ Don't throw exceptions directly (will crash server)
throw new Error('Error');  // Will interrupt server
```

## Validation and Testing

### Python MCP Validation
1. Ensure code runs correctly: `python {tool-name}_mcp.py`
2. Verify tool list returns correctly: Send `{"type": "list_tools"}` to stdin
3. Verify tool call functionality: Send tool call requests to stdin

### JavaScript MCP Validation
1. Ensure dependencies are installed: `npm install`
2. Start server: `node src/index.js`
3. Test tool functionality with MCP client
4. Verify CDP connection to target application

### Test Examples

#### Python MCP Test
```python
# Test tool list request
{"type": "list_tools"}

# Test tool call request
{
  "type": "call_tool",
  "name": "{tool-name}",
  "arguments": {
    "{parameter-name}": "{parameter-value}"
  }
}
```

#### JavaScript MCP Test
Create a test script to verify tool functionality:

```javascript
import { CDPClient } from './src/cdp-client.js';
import { yourTool } from './src/tools/your-tool.js';

async function test() {
  const cdpClient = new CDPClient({ host: 'localhost', port: 9225 });
  
  await cdpClient.connect();
  
  const result = await yourTool.handler(cdpClient, {
    param1: 'test',
    param2: 100
  });
  
  console.log('结果:', result);
  
  await cdpClient.disconnect();
}

test();
```

## Example MCP Tools

### Python MCP Tool Example

```
mcp/
├── demo_mcp/             # Tool directory
│   ├── demo_mcp.py       # Main file
│   └── helper.py         # Optional helper module

└── ... other tool directories
```

### JavaScript MCP Tool Example

```
xiaozhi-mcp/
├── src/
│   ├── index.js              # MCP server entry
│   ├── cdp-client.js         # CDP client
│   ├── utils.js              # Utility functions
│   └── tools/
│       ├── get-page-info.js  # Get page info tool
│       └── click-element.js  # Click element tool
├── package.json
└── mcp-config.json
```

## Summary

This skill provides comprehensive guidance for creating MCP tools in both Python and JavaScript. Whether you're building simple Python tools or JavaScript tools with CDP integration for browser automation, following these guidelines will ensure consistent structure, reliable performance, and maintainable code.

Key considerations:
- Choose the appropriate language based on your use case
- Follow language-specific best practices and conventions
- Implement proper error handling and validation
- Test thoroughly before deployment
- Maintain clear documentation for your tools

By following these recommendations, you'll create MCP tools that are robust, efficient, and easy to integrate with AI systems.
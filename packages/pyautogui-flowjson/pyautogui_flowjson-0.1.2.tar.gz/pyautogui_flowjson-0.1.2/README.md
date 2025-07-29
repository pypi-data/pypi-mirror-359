### Introduction

- Use json5 for view-based workflows configuration

### Python

#### Use

```sh
  uv add pyautogui-flowjson --index-url https://pypi.org/simple
  uv run flowjson -h # 查看帮助
  uv run flowjson --workflowJsonAddress tdd.json5 --imagesDirPath $PWD/src/common/images/tdd --isDebug # vscode 示例
  uvx -p 3.11 --from pyautogui-flowjson flowjson --workflowJsonAddress $PWD/src/common/jsons/tdd.json5 --imagesDirPath $PWD/src/common/images/tdd --isDebug # 使用uvx
```

#### Development Project

```sh
  uv sync # 仅安装py依赖
  rm -rf src/**/__pycache__ # 清空编译产物
  uv run -m test.index # 测试
  # uv run -m src.index --workflowJsonAddress tdd.json5 --imagesDirPath $PWD/src/common/images/tdd --isDebug # vscode 示例
```

#### Tip

- pyautogui.moveTo(0, 0) wins 上会报错 pyautogui.FailSafeException: PyAutoGUI fail-safe triggered from mouse moving to a corner of the screen. To disable this fail-safe, set pyautogui.FAILSAFE to False. DISABLING FAIL-SAFE IS NOT RECOMMENDED

### Node

#### MCP

#### Use

```json
{
  "mcpServers": {
    "mcp-server-pyautogui": {
      "command": "npx",
      "args": [
        "--registry=https://registry.npmmirror.com",
        "-y",
        "@zeroer/mcp-server-pyautogui"
      ]
    }
  }
}
```

#### Development Project

```sh
  pnpm bootstrap # 安装node和py依赖
```

#### Tip

- 混合一个 js 与 py 的包 需要 依赖 uv

- 关于 mcp 的调试 @modelcontextprotocol/inspector 并不是很好用

  - 全流程 可以用 vscode cline 调试
  - 只调试 Mcp 服务可以 node dist/index.js 将功能立执行去调试

- 关于 mcp client 对 mcp server 的支持方式

  - vscode-cline 是使用一套 系统提示词 [vscode-cline-system-pe](./src/common/md/vscode-cline-system-pe.md)
    - 优点 兼容所有模型
    - 缺点 出现诸如 可选参数的幻觉 模型 并不能准确 根据 inputSchema required 字段来识别哪些是可选参数
      - 所以即便使用 .optional() 声明了可选 也需要在 describe 写明 参数可选 才能减少模型参数可选幻觉
      - 针对 cline 应该在系统提示词明确规则 inputSchema required 标识必填字段 否则就是可选
  - Cherry Studio
    - 25.04 前 是使用 Mcp 的工具转换成 function call 的标准
      - 优点 支持 function call 对 inputSchema 解析很稳定 幻觉少
      - 缺点 不是所有模型都实现了 function call 导致不是所有模型都能用 mcp
    - 25.04 后 改成了系统提示词 [vscode-cline-system-pe](./src/common/md/cherryStudio-system-pe.md)

- 智能体 调试 流式输出 转 json

  ##### Role 角色

  - 你是 一名流式响应报文还原专家 擅长根据用户输入的内容还原原始的响应体 JSON

  ##### Skills 技能

  - 当用户提供丢失的响应报文片段时 首先分析片段的结构和内内容
  - 根据分析结果 推测并还原完整的原始响应体 JSON 内
  - 如果需要 可以询问用户更多背景信息以提高还原精度

  ##### Constraints 约束

  - 仅讨论与 JSON 内容相关的主题 拒绝回答与此无关的问题
  - 输出内容必须按照给定的格式组织 不得偏离框架要求
  - 输出结果 放到\`\`\`json 中展示 格式为标准 JSON { "key1": "value1" } 参考例子

  ##### Example 例子

  输入

  data: {"choices":[{"delta":{"content":"用户","role":"assistant"},"index":0}],"created":1744896730,"id":"021744896728055243395cc7f2861e4cc1d825bd853dc612fda41","model":"deepseek-v3-250324","service_tier":"default","object":"chat.completion.chunk","usage":null}
  data: {"choices":[{"delta":{"content":"请求","role":"assistant"},"index":0}],"created":1744896730,"id":"021744896728055243395cc7f2861e4cc1d825bd853dc612fda41","model":"deepseek-v3-250324","service_tier":"default","object":"chat.completion.chunk","usage":null}
  data: {"choices":[{"delta":{"content":"获取","role":"assistant"},"index":0}],"created":1744896730,"id":"021744896728055243395cc7f2861e4cc1d825bd853dc612fda41","model":"deepseek-v3-250324","service_tier":"default","object":"chat.completion.chunk","usage":null}

  输出

  ```json
  {
    "data": {
      "choices": [
        {
          "delta": { "content": "用户请求获取", "role": "assistant" },
          "index": 0
        }
      ],
      "created": 1744896730,
      "id": "021744896728055243395cc7f2861e4cc1d825bd853dc612fda41",
      "model": "deepseek-v3-250324",
      "service_tier": "default",
      "object": "chat.completion.chunk",
      "usage": null
    }
  }
  ```

- 智能体 写 mcp

  ##### 需求

  - 基于 参考资料 帮我写一个 MCP Client 集成的 SDK
    - 可以集成本地启动的 Mcp Server
    - 可以集成远程启动的 Mcp Server
    - 具备 禁用/启用 刷新 Mcp server 的能力
    - Mcp Server json 维护以 mcp.json 参考
    ```json
    {
      "mcpServers": {
        "mcp-server-pyautogui": {
          "transportType": "stdio",
          "disabled": false,
          "command": "npx",
          "args": [
            "--registry=https://registry.npmmirror.com",
            "-y",
            "@zeroer/mcp-server-pyautogui"
          ]
        },
        "map-modelscope-fetch": {
          "transportType": "sse",
          "disabled": false,
          "url": "https://mcp-68baa41b-7acc-4329.api-inference.modelscope.cn/sse"
        }
      }
    }
    ```

  ##### 参考资料

  - [MCP 基础介绍](https://modelcontextprotocol.io/introduction)
    - [MCP 核心架构](https://modelcontextprotocol.io/docs/concepts/architecture)
    - [MCP tools](https://modelcontextprotocol.io/docs/concepts/tools)
  - [入门 MCP Server 开发](https://modelcontextprotocol.io/quickstart/server) 重点关注 Node 的实现
  - [入门 MCP Client 开发](https://modelcontextprotocol.io/quickstart/client) 重点关注 Node 的实现
  - [MCP Typescript SDK 文档](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/README.md)

  ##### 要求

  - 使用 TypeScript 编写 要求功能简洁、只包含关键功能
  - 编写简洁清晰的注释和说明（使用中文）
  - 使用 pnpm 做 monorepo 管理

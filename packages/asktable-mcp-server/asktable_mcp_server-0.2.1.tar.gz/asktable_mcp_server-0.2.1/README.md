# Asktable-MCP-Server
![Case](https://s3.bmp.ovh/imgs/2025/07/02/a16c161e3570120b.png )

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/asktable-mcp-server.svg)](https://pypi.org/project/asktable-mcp-server/)



`asktable-mcp-server` 是为 [AskTable](https://www.asktable.com/) 提供的 MCP 服务，支持通过 Stdio 或 SSE 协议与 AskTable SaaS 或本地部署服务交互。


![Case](https://s3.bmp.ovh/imgs/2025/07/02/7de2a851031f6913.png)
## 快速开始

### 安装与配置
本地先安装uv配置工具。
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 参数说明

- `api_key`：AskTable API 密钥（必需，环境变量）
- `datasource_id`：数据源ID（必需，环境变量）
- `base_url`：本地IP服务地址（可选，填写则走本地部署，不填则走SaaS）
- `role_id` ：角色id（可选，填写则只能访问该角色被允许的数据，不填则即可查询所有数据）

---

## 工具介绍
 - gen_sql ， 根据用户查询生成对应的SQL语句
   - 输入：生成可以找出销售额前10的产品的sql
   - 输出：对应的sql语句
 - gen_conclusion ， 根据用户的问题，直接返回数据结果
   - 输入：用户问题，如："请给我出销售额前10的产品"
   - 输出：对应的数据结果
 - list_available_datasources ， 获取当前APIKEY下的用户（role_id）所有可用数据库（数据源）信息
   - 输入：我数据库中有哪些数据源？
   - 输出：对应的数据源信息，包括数据源id、数据库引擎、数据库描述

---
## 启动命令示例
在使用之前需先进行以下配置

- Stdio 模式（本地或SaaS）：
  ```bash
  uvx asktable-mcp-server@latest --transport stdio
  ```

- SSE 模式（本地或SaaS）：
  ```bash
  #sass版
  uvx --from asktable-mcp-server@latest python -m asktable_mcp_server.sse_server
  ```
  ```bash
  #本地版
  #开启服务后会占用本地的8095端口
  uvx --from asktable-mcp-server@latest python -m asktable_mcp_server.sse_server --base_url http://your_local_ip:port/api
  ```
  


## 配置示例

### 配置mcpServers_json
>以下对应需要对 `mcpServers json”进行配置的情况，根据你不同的启动命令和平台兼容的方式来选择对应的模式。
<details>
<summary>Stdio + SaaS</summary>

```json
{
  "mcpServers": {
    "asktable-mcp-server": {
      "command": "uvx",
      "args": ["asktable-mcp-server@latest"],
      "env": {
        "api_key": "your_api_key",            // 必填
        "datasource_id": "your_datasource_id", // 必填
        // "role_id": "your_role_id"           // 可选：如需限定角色权限，请填写
      }
    }
  }
}
```
</details>

<details>
<summary>Stdio + 本地部署</summary>

```json
{
  "mcpServers": {
    "asktable-mcp-server": {
      "command": "uvx",
      "args": ["asktable-mcp-server@latest"],
      "env": {
        "api_key": "your_api_key",           // 必填
        "datasource_id": "your_datasource_id",// 必填
        "base_url": "http://your_local_ip:port/api", // 必填
        // "role_id": "your_role_id"           // 可选：如需限定角色权限，请填写
      }
    }
  }
}
```
</details>

<details>
<summary>SSE</summary>

```json
{
  "mcpServers": {    
    "asktable-mcp-server": {
      // role_id 为可选参数，不指定则使用默认权限
      "url": "http://localhost:8095/sse/?apikey=your_apikey&datasouce_id=your_datasouce_id&role_id=your_role_id",
      "headers": {},
      "timeout": 300,
      "sse_read_timeout": 300
    }
  }
}
```
</details>


### 配置SSE URL
```bash
http://localhost:8095/sse/?apikey=your_apikey&datasouce_id=your_datasouce_id
```
---

如需进一步帮助，请查阅官方文档或联系我们。

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
- `role_id`：角色ID（可选，用于权限控制）

---

## 工具介绍

### 可用工具

1. **list_available_datasources** - 获取当前APIKEY下的所有可用数据库（数据源）信息
   - **输入示例**：我数据库中有哪些数据源？
   - **输出**：数据源信息列表，包含数据源ID、数据库引擎、数据库描述
   - **使用场景**：查看用户权限下的所有数据源，获取数据源ID用于后续查询

2. **gen_conclusion** - 根据用户的问题，直接返回数据结果
   - **输入示例**：
     - "请给我出销售额前10的产品"
     - "昨天的订单总金额是多少"
     - "每个部门有多少员工"
   - **输出**：查询的实际数据结果
   - **使用场景**：需要直接获取查询答案，不关心SQL细节

3. **gen_sql** - 根据用户查询生成对应的SQL语句
   - **输入示例**：
     - "生成可以找出销售额前10的产品的sql"
     - "我需要查询昨天的订单总金额的sql"
     - "统计每个部门的员工数量的sql"
   - **输出**：生成的SQL语句
   - **使用场景**：需要查看生成的SQL语句，进行SQL审查或调试

---

## 用户配置指南

### 方式一：Stdio 模式（推荐个人用户）

Stdio 模式适合个人用户使用，通过标准输入输出与MCP客户端通信。

#### 1. 安装包
```bash
# 使用 uv 安装
uvx asktable-mcp-server@latest

# 或使用 pip 安装
pip install asktable-mcp-server
```

#### 2. 配置 MCP 客户端

根据您使用的MCP客户端，选择对应的配置方式：

<details>
<summary>Claude Desktop</summary>

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "asktable-mcp-server": {
      "command": "uvx",
      "args": ["asktable-mcp-server@latest"],
      "env": {
        "API_KEY": "your_api_key",
        "DATASOURCE_ID": "your_datasource_id",
        "BASE_URL": "http://your_local_ip:port/api"
      }
    }
  }
}
```

</details>

<details>
<summary>Cursor</summary>

在 Cursor 的配置文件中添加：

```json
{
  "mcpServers": {
    "asktable-mcp-server": {
      "command": "asktable-mcp-server",
      "env": {
        "API_KEY": "your_api_key",
        "DATASOURCE_ID": "your_datasource_id",
        "BASE_URL": "http://your_local_ip:port/api"
      }
    }
  }
}
```

</details>

<details>
<summary>其他 MCP 客户端</summary>

```json
{
  "mcpServers": {
    "asktable-mcp-server": {
      "command": "python",
      "args": ["-m", "asktable_mcp_server.server"],
      "env": {
        "API_KEY": "your_api_key",
        "DATASOURCE_ID": "your_datasource_id",
        "BASE_URL": "http://your_local_ip:port/api"
      }
    }
  }
}
```

</details>

### 方式二：SSE 模式（推荐团队用户）

SSE 模式适合团队使用，可以部署为独立的HTTP服务，支持多用户访问。

#### 1. 直接运行
```bash
# 安装包
pip install asktable-mcp-server

# 启动 SSE 服务器
python -m asktable_mcp_server.server --transport sse --port 8095
```

#### 2. 配置 MCP 客户端

```json
{
  "mcpServers": {
    "asktable-mcp-server": {
      "url": "http://your_server_ip:8095/sse/?apikey=your_api_key&datasource_id=your_datasource_id",
      "headers": {},
      "timeout": 300,
      "sse_read_timeout": 300
    }
  }
}
```

---

## 系统管理员部署指南

### Docker 部署（推荐）

#### 使用官方镜像
```bash
# 拉取镜像
docker pull registry.cn-shanghai.aliyuncs.com/datamini/asktable-mcp-server:latest

# 运行容器
docker run -d \
  --name asktable-mcp-server \
  -p 8095:8095 \
  -e API_KEY=your_api_key \
  -e DATASOURCE_ID=your_datasource_id \
  -e BASE_URL=http://your_local_ip:port/api \
  registry.cn-shanghai.aliyuncs.com/datamini/asktable-mcp-server:latest
```


---

如需进一步帮助，请查阅官方文档或联系我们。

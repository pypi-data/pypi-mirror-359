# XVI MCP Server

A Model Context Protocol (MCP) server for XVI vulnerability platform integration.

## 简介

XVI MCP Server 是一个基于 Model Context Protocol (MCP) 的服务器，用于与 XVI 漏洞平台集成。它提供了一系列工具函数，可以通过 MCP 协议调用 XVI 平台的各种功能。

## 功能特性

- **漏洞查询**: 支持通过关键词、CVE编号、时间范围等条件查询漏洞信息
- **漏洞类型过滤**: 支持按漏洞类型进行筛选
- **风险等级筛选**: 支持按严重程度筛选漏洞
- **结果数量控制**: 可自定义返回结果数量
- **详细漏洞信息**: 返回包括漏洞描述、危害、修复建议等详细信息

## 安装

### 使用 uvx (推荐)

```bash
uvx xvi-mcp
```

### 使用 pip

```bash
pip install xvi-mcp
```

## 使用方法

### 作为 MCP 服务器运行

```bash
# 使用 uvx
uvx xvi-mcp

# 或使用 pip 安装后
xvi-mcp
```

### 在 MCP 客户端中配置

在你的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "xvi-mcp": {
      "command": "uvx",
      "args": ["xvi-mcp"]
    }
  }
}
```

## 可用工具函数

### get_vulns

查询漏洞信息的主要函数。

**参数：**
- `keyword` (str, 可选): 模糊查询关键词
- `cve` (str, 可选): CVE编号
- `publishTimeStart` (str, 可选): 起始时间，格式为 yyyy-MM-dd HH:mm:ss
- `publishTimeEnd` (str, 可选): 截止时间，格式为 yyyy-MM-dd HH:mm:ss
- `vulnType` (str, 可选): 漏洞类型
- `riskLevels` (list, 可选): 风险等级列表，可选值："serious", "high_risk", "medium_risk", "low_risk", "unknown"
- `resultSize` (int, 可选): 返回结果数量，范围 1-100，默认为 1

**返回值：**
返回包含漏洞详细信息的字符串，包括：
- 漏洞链接
- 漏洞ID
- 漏洞名称
- 风险等级
- CVE/CNVD/CNNVD编号
- CVSS3评分和字符串
- 漏洞描述
- 漏洞危害
- CWE类型
- 修复建议

## 配置要求

本服务器需要访问 XVI 平台的 API，使用了预配置的客户端凭据。如果需要使用自己的凭据，请修改源代码中的相关配置。

## 开发

### 本地开发安装

```bash
git clone https://github.com/WACHI/xvi-mcp.git
cd xvi-mcp
pip install -e .
```

### 运行测试

```bash
python -m pytest
```

### 构建包

```bash
python -m build
```

### 发布到 PyPI

```bash
twine upload dist/*
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 安全注意事项

- 本工具包含硬编码的 API 凭据，仅用于演示目的
- 在生产环境中使用时，请确保使用环境变量或安全的配置管理方式
- 请遵守 XVI 平台的使用条款和 API 限制

## 联系方式

- 作者: WACHI
- 邮箱: wachi@example.com
- 项目地址: https://github.com/WACHI/xvi-mcp
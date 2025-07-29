#!/usr/bin/env python3
"""
XVI MCP Server 使用示例

本文件演示了如何使用 xvi-mcp 包的各种功能。
"""

import json

# XVI MCP Server 使用示例
print("="*60)
print("XVI MCP Server 使用示例")
print("="*60)

print("\n1. 安装方式:")
print("   使用 uvx (推荐):")
print("   uvx xvi-mcp")
print("\n   使用 pip:")
print("   pip install xvi-mcp")

print("\n2. 包信息:")
print("   包名: xvi-mcp")
print("   版本: 0.1.0")
print("   描述: XVI MCP Server - XVI漏洞平台的MCP协议服务器")
print("   作者: WACHI")

print("\n3. 使用方法:")
print("   作为 MCP 服务器运行:")
print("   uvx xvi-mcp")
print("\n   或者:")
print("   xvi-mcp")

print("\n4. MCP 客户端配置示例:")
mcp_config = {
    "mcpServers": {
        "xvi-mcp": {
            "command": "uvx",
            "args": ["xvi-mcp"]
        }
    }
}
print(json.dumps(mcp_config, indent=2, ensure_ascii=False))

print("\n5. 可用的 MCP 工具函数:")
print("   - get_vulns: 查询漏洞信息")
print("     参数:")
print("     * keyword (str): 模糊查询关键词")
print("     * cve (str): CVE编号")
print("     * publishTimeStart (str): 起始时间 (yyyy-MM-dd HH:mm:ss)")
print("     * publishTimeEnd (str): 截止时间 (yyyy-MM-dd HH:mm:ss)")
print("     * vulnType (str): 漏洞类型")
print("     * riskLevels (list): 风险等级 ['serious', 'high_risk', 'medium_risk', 'low_risk', 'unknown']")
print("     * resultSize (int): 返回结果数量 (1-100)")

print("\n6. 使用示例:")
print("   查询关键词为'Apache'的漏洞:")
print("   get_vulns(keyword='Apache', resultSize=5)")
print("\n   查询特定CVE:")
print("   get_vulns(cve='CVE-2023-1234')")
print("\n   查询高危漏洞:")
print("   get_vulns(riskLevels=['serious', 'high_risk'], resultSize=10)")

print("\n7. 返回信息包括:")
print("   - 漏洞链接 (vulnLink)")
print("   - 漏洞ID (id)")
print("   - 漏洞名称 (vulnName)")
print("   - 风险等级 (riskLevel)")
print("   - CVE/CNVD/CNNVD编号")
print("   - CVSS3评分和字符串")
print("   - 漏洞描述 (vulnDesc)")
print("   - 漏洞危害 (vulnHarm)")
print("   - CWE类型 (cwes)")
print("   - 修复建议 (fixes)")

print("\n8. 注意事项:")
print("   - 需要网络连接访问XVI平台API")
print("   - 使用了预配置的API凭据")
print("   - 请遵守XVI平台的使用条款")
print("   - 建议在生产环境中使用环境变量管理凭据")

print("\n9. 支持的漏洞类型 (部分):")
vuln_types = [
    "SQL注入", "跨站点脚本", "命令注入", "路径遍历", "文件包含",
    "缓冲区溢出", "权限提升", "信息泄露", "拒绝服务", "代码注入"
]
for i, vtype in enumerate(vuln_types, 1):
    print(f"   {i:2d}. {vtype}")

print("\n10. 项目信息:")
print("    GitHub: https://github.com/WACHI/xvi-mcp")
print("    PyPI: https://pypi.org/project/xvi-mcp/")
print("    许可证: MIT License")
print("    联系方式: wachi@example.com")

print("\n" + "="*60)
print("XVI MCP Server 已准备就绪！")
print("使用 'uvx xvi-mcp' 启动服务器")
print("="*60)
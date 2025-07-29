import asyncio
import hashlib
import json
import logging
import os
import time
from os.path import exists

from Levenshtein import distance
import requests
from mcp.server import FastMCP

# 初始化 FastMCP 服务器
app = FastMCP('xvi')

log_file_path = 'app.log'
if exists(log_file_path) is False:
    with open(log_file_path, 'w') as file:
        pass

vulnTypeList = [
    "代码",
    "源代码",
    "不正确的输入验证",
    "路径名遍历",
    "路径遍历",
    "相对路径遍历",
    "链接关注",
    "符号链接跟随",
    "文件包含",
    "注射",
    "命令注入",
    "操作系统命令注入",
    "跨站点脚本",
    "基本的跨站点脚本",
    "参数注入",
    "SQL注入",
    "LDAP注入",
    "XML 注入",
    "CRLF注射",
    "代码注入",
    "资源标识符控制不当",
    "HTTP 响应拆分",
    "输出转义",
    "不正确的日志输出中和",
    "范围错误",
    "内存损坏",
    "缓冲区溢出",
    "基于堆栈的缓冲区溢出",
    "基于堆的缓冲区溢出",
    "写什么位置条件",
    "越界读取",
    "数组索引的不正确验证",
    "格式化字符串",
    "不正确的空终止",
    "编码错误",
    "不完整的黑名单",
    "不正确的正则表达式",
    "数字错误",
    "整数溢出",
    "整数下溢",
    "整数强制错误",
    "一对一",
    "信息管理错误",
    "信息披露",
    "在发送的数据中插入敏感信息",
    "通过差异暴露信息",
    "可观察到的时序差异",
    "通过错误信息暴露信息",
    "使用不必要的权限执行",
    "未检查的返回值",
    "7PK 安全功能",
    "凭证管理",
    "未受保护的凭证存储",
    "使用硬编码密码",
    "不正确的访问控制",
    "沙盒问题",
    "不正确的权限分配",
    "权限管理不当",
    "不正确检查删除的权限",
    "权限不足处理不当",
    "权限问题",
    "不正确的默认权限",
    "权限不足处理不当",
    "权限保留",
    "不正确的访问控制",
    "不正确的授权",
    "不正确的认证",
    "使用备用通道绕过身份验证",
    "通过欺骗绕过身份验证",
    "通过捕获重放绕过身份验证",
    "不正确的证书验证",
    "证书与主机不匹配",
    "非端点可访问的通道",
    "通过主要弱点绕过身份验证",
    "缺少身份验证",
    "对过度认证尝试的不当限制",
    "密码问题",
    "敏感数据缺少加密",
    "敏感信息的明文存储",
    "敏感信息的明文传输",
    "密钥管理错误",
    "使用硬编码的加密密钥",
    "重用随机数",
    "加密强度不足",
    "有风险的密码算法",
    "随机值不足",
    "熵不足",
    "PRNG中的熵不足",
    "PRNG 中的种子使用不正确",
    "加密弱PRNG",
    "从先前值的可预测值范围",
    "数据真实性验证不足",
    "来源验证错误",
    "不正确的密码签名验证",
    "依赖反向 DNS 解析",
    "跨站请求伪造",
    "不正确的完整性检查值验证",
    "标准的安全检查",
    "7PK时间和状态",
    "竞争条件",
    "检查时间使用时间",
    "除以零",
    "状态问题",
    "不安全的临时文件",
    "会话固定",
    "7PK错误",
    "资源管理不当",
    "资源消耗",
    "内存泄漏",
    "拒绝服务",
    "低效的算法复杂性",
    "双自由",
    "免费使用",
    "路径错误",
    "直接请求",
    "不受信任的搜索路径",
    "不受控制的搜索路径",
    "不带引号的搜索路径",
    "无限制上传",
    "意外的中介",
    "HTTP 请求走私",
    "点击劫持",
    "不完全清理",
    "空指针取消引用",
    "下载没有完整性检查的代码",
    "反序列化",
    "弱密码要求",
    "凭据保护不足",
    "日志文件中的敏感信息",
    "通过调试日志文件暴露信息",
    "文件和目录信息暴露",
    "文件或目录可访问",
    "未经验证的 Cookie",
    "打开重定向",
    "外部控制参考",
    "XML 外部实体参考",
    "会话到期",
    "没有安全属性的敏感cookie",
    "可达断言",
    "授权绕过",
    "弱密码恢复",
    "PHP弱点",
    "终身资源控制不当",
    "不正确的初始化",
    "锁定不当",
    "资源曝光",
    "资源传输不正确",
    "不正确的控制流程",
    "资源过期后的操作",
    "不受控制的递归",
    "数值类型之间的转换不正确",
    "计算错误",
    "保护机构故障",
    "不正确的比较",
    "类型转换不正确",
    "名称解析不正确",
    "无效化不当",
    "权限分配不正确",
    "暴露的危险套路",
    "异常情况检查不正确",
    "异常情况的处理",
    "算法降级",
    "无盐单向哈希",
    "释放参考",
    "不受控制的文件描述符消耗",
    "资源分配",
    "缺少资源释放",
    "XML 实体扩展",
    "越界写入",
    "不受控制的内存分配",
    "硬编码凭证",
    "未初始化的指针",
    "包含来自不受信任控制领域的功能",
    "僵局",
    "过度迭代",
    "无限循环",
    "行为工作流程的执行",
    "类型混乱",
    "缺少授权",
    "不正确的授权",
    "未初始化的资源",
    "缺少资源初始化",
    "后门",
    "动态管理的代码资源",
    "动态确定的对象属性",
    "计算量不足的密码哈希",
    "服务器端请求伪造",
    "敏感信息的不安全存储",
    "消息完整性执行不当",
    "具有不受信任域的宽松跨域策略",
    "没有“HttpOnly”标志的 Cookie",
    "管理用户会话",
    "渲染 UI 层的不当限制",
    "使用未初始化的资源",
    "不安全的资源默认初始化",
    "CSV 注入",
    "比较逻辑容易受到侧信道攻击",
    "配置"

]


def find_most_similar(query, strings):
    return min(strings, key=lambda x: distance(query, x))


def vulnType_to_cweCode(vulnType: str):
    map = {
        "CWE-17": "代码",
        "CWE-18": "源代码",
        "CWE-20": "不正确的输入验证",
        "CWE-21": "路径名遍历",
        "CWE-22": "路径遍历",
        "CWE-23": "相对路径遍历",
        "CWE-59": "链接关注",
        "CWE-61": "符号链接跟随",
        "CWE-73": "文件包含",
        "CWE-74": "注射",
        "CWE-77": "命令注入",
        "CWE-78": "操作系统命令注入",
        "CWE-79": "跨站点脚本",
        "CWE-80": "基本的跨站点脚本",
        "CWE-88": "参数注入",
        "CWE-89": "SQL注入",
        "CWE-90": "LDAP注入",
        "CWE-91": "XML 注入",
        "CWE-93": "CRLF注射",
        "CWE-94": "代码注入",
        "CWE-99": "资源标识符控制不当",
        "CWE-113": "HTTP 响应拆分",
        "CWE-116": "输出转义",
        "CWE-117": "不正确的日志输出中和",
        "CWE-118": "范围错误",
        "CWE-119": "内存损坏",
        "CWE-120": "缓冲区溢出",
        "CWE-121": "基于堆栈的缓冲区溢出",
        "CWE-122": "基于堆的缓冲区溢出",
        "CWE-123": "写什么位置条件",
        "CWE-125": "越界读取",
        "CWE-129": "数组索引的不正确验证",
        "CWE-134": "格式化字符串",
        "CWE-170": "不正确的空终止",
        "CWE-172": "编码错误",
        "CWE-184": "不完整的黑名单",
        "CWE-185": "不正确的正则表达式",
        "CWE-189": "数字错误",
        "CWE-190": "整数溢出",
        "CWE-191": "整数下溢",
        "CWE-192": "整数强制错误",
        "CWE-193": "一对一",
        "CWE-199": "信息管理错误",
        "CWE-200": "信息披露",
        "CWE-201": "在发送的数据中插入敏感信息",
        "CWE-203": "通过差异暴露信息",
        "CWE-208": "可观察到的时序差异",
        "CWE-209": "通过错误信息暴露信息",
        "CWE-250": "使用不必要的权限执行",
        "CWE-252": "未检查的返回值",
        "CWE-254": "7PK 安全功能",
        "CWE-255": "凭证管理",
        "CWE-256": "未受保护的凭证存储",
        "CWE-259": "使用硬编码密码",
        "CWE-264": "不正确的访问控制",
        "CWE-265": "沙盒问题",
        "CWE-266": "不正确的权限分配",
        "CWE-269": "权限管理不当",
        "CWE-273": "不正确检查删除的权限",
        "CWE-274": "权限不足处理不当",
        "CWE-275": "权限问题",
        "CWE-276": "不正确的默认权限",
        "CWE-280": "权限不足处理不当",
        "CWE-281": "权限保留",
        "CWE-284": "不正确的访问控制",
        "CWE-285": "不正确的授权",
        "CWE-287": "不正确的认证",
        "CWE-288": "使用备用通道绕过身份验证",
        "CWE-290": "通过欺骗绕过身份验证",
        "CWE-294": "通过捕获重放绕过身份验证",
        "CWE-295": "不正确的证书验证",
        "CWE-297": "证书与主机不匹配",
        "CWE-300": "非端点可访问的通道",
        "CWE-305": "通过主要弱点绕过身份验证",
        "CWE-306": "缺少身份验证",
        "CWE-307": "对过度认证尝试的不当限制",
        "CWE-310": "密码问题",
        "CWE-311": "敏感数据缺少加密",
        "CWE-312": "敏感信息的明文存储",
        "CWE-319": "敏感信息的明文传输",
        "CWE-320": "密钥管理错误",
        "CWE-321": "使用硬编码的加密密钥",
        "CWE-323": "重用随机数",
        "CWE-326": "加密强度不足",
        "CWE-327": "有风险的密码算法",
        "CWE-330": "随机值不足",
        "CWE-331": "熵不足",
        "CWE-332": "PRNG中的熵不足",
        "CWE-335": "PRNG 中的种子使用不正确",
        "CWE-338": "加密弱PRNG",
        "CWE-343": "从先前值的可预测值范围",
        "CWE-345": "数据真实性验证不足",
        "CWE-346": "来源验证错误",
        "CWE-347": "不正确的密码签名验证",
        "CWE-350": "依赖反向 DNS 解析",
        "CWE-352": "跨站请求伪造",
        "CWE-354": "不正确的完整性检查值验证",
        "CWE-358": "标准的安全检查",
        "CWE-361": "7PK时间和状态",
        "CWE-362": "竞争条件",
        "CWE-367": "检查时间使用时间",
        "CWE-369": "除以零",
        "CWE-371": "状态问题",
        "CWE-377": "不安全的临时文件",
        "CWE-384": "会话固定",
        "CWE-388": "7PK错误",
        "CWE-399": "资源管理不当",
        "CWE-400": "资源消耗",
        "CWE-401": "内存泄漏",
        "CWE-404": "拒绝服务",
        "CWE-407": "低效的算法复杂性",
        "CWE-415": "双自由",
        "CWE-416": "免费使用",
        "CWE-417": "路径错误",
        "CWE-425": "直接请求",
        "CWE-426": "不受信任的搜索路径",
        "CWE-427": "不受控制的搜索路径",
        "CWE-428": "不带引号的搜索路径",
        "CWE-434": "无限制上传",
        "CWE-441": "意外的中介",
        "CWE-444": "HTTP 请求走私",
        "CWE-451": "点击劫持",
        "CWE-459": "不完全清理",
        "CWE-476": "空指针取消引用",
        "CWE-494": "下载没有完整性检查的代码",
        "CWE-502": "反序列化",
        "CWE-521": "弱密码要求",
        "CWE-522": "凭据保护不足",
        "CWE-532": "日志文件中的敏感信息",
        "CWE-534": "通过调试日志文件暴露信息",
        "CWE-538": "文件和目录信息暴露",
        "CWE-552": "文件或目录可访问",
        "CWE-565": "未经验证的 Cookie",
        "CWE-601": "打开重定向",
        "CWE-610": "外部控制参考",
        "CWE-611": "XML 外部实体参考",
        "CWE-613": "会话到期",
        "CWE-614": "没有安全属性的敏感cookie",
        "CWE-617": "可达断言",
        "CWE-639": "授权绕过",
        "CWE-640": "弱密码恢复",
        "CWE-661": "PHP弱点",
        "CWE-664": "终身资源控制不当",
        "CWE-665": "不正确的初始化",
        "CWE-667": "锁定不当",
        "CWE-668": "资源曝光",
        "CWE-669": "资源传输不正确",
        "CWE-670": "不正确的控制流程",
        "CWE-672": "资源过期后的操作",
        "CWE-674": "不受控制的递归",
        "CWE-681": "数值类型之间的转换不正确",
        "CWE-682": "计算错误",
        "CWE-693": "保护机构故障",
        "CWE-697": "不正确的比较",
        "CWE-704": "类型转换不正确",
        "CWE-706": "名称解析不正确",
        "CWE-707": "无效化不当",
        "CWE-732": "权限分配不正确",
        "CWE-749": "暴露的危险套路",
        "CWE-754": "异常情况检查不正确",
        "CWE-755": "异常情况的处理",
        "CWE-757": "算法降级",
        "CWE-759": "无盐单向哈希",
        "CWE-763": "释放参考",
        "CWE-769": "不受控制的文件描述符消耗",
        "CWE-770": "资源分配",
        "CWE-772": "缺少资源释放",
        "CWE-776": "XML 实体扩展",
        "CWE-787": "越界写入",
        "CWE-789": "不受控制的内存分配",
        "CWE-798": "硬编码凭证",
        "CWE-824": "未初始化的指针",
        "CWE-829": "包含来自不受信任控制领域的功能",
        "CWE-833": "僵局",
        "CWE-834": "过度迭代",
        "CWE-835": "无限循环",
        "CWE-841": "行为工作流程的执行",
        "CWE-843": "类型混乱",
        "CWE-862": "缺少授权",
        "CWE-863": "不正确的授权",
        "CWE-908": "未初始化的资源",
        "CWE-909": "缺少资源初始化",
        "CWE-912": "后门",
        "CWE-913": "动态管理的代码资源",
        "CWE-915": "动态确定的对象属性",
        "CWE-916": "计算量不足的密码哈希",
        "CWE-918": "服务器端请求伪造",
        "CWE-922": "敏感信息的不安全存储",
        "CWE-924": "消息完整性执行不当",
        "CWE-942": "具有不受信任域的宽松跨域策略",
        "CWE-1004": "没有“HttpOnly”标志的 Cookie",
        "CWE-1018": "管理用户会话",
        "CWE-1021": "渲染 UI 层的不当限制",
        "CWE-1187": "使用未初始化的资源",
        "CWE-1188": "不安全的资源默认初始化",
        "CWE-1236": "CSV 注入",
        "CWE-1255": "比较逻辑容易受到侧信道攻击",
        "CWE-16": "配置"

    }
    for k, v in map.items():
        if vulnType == v:
            return k


def oauth():
    logging.info("oauth")
    url = "https://vip.tophant.com/api/oauth/token"
    data = {
        "client_id": "43c1cef8d9371268",
        "client_secret": "1734e5262a3299a44f769e842bdace4d68060fe0a1caf05fdfb80cf66b3fe00a",
        "grant_type": "client_credentials",
    }
    response = requests.post(url, data=data)
    return response.json()['access_token']


def generate_sign(params: dict, client_secret: str) -> str:
    """
    生成签名（sign）

    :param params: 字典参数，参与签名的键值对（不应包含 'sign' 字段）
    :param client_secret: 客户端密钥
    :return: 生成的签名字符串（大写 SHA-256 HEX）
    """

    if not params:
        raise ValueError("参数不能为空")

    # 添加 clientSecret
    params_with_secret = dict(params)  # 复制原始参数，避免修改原字典
    params_with_secret['clientSecret'] = client_secret

    # 构造源串
    items = sorted(params_with_secret.items())
    sign_string = ""
    items.pop()
    for key, value in items:
        if not key or key.strip().lower() == "sign":
            continue
        sign_string += f"{key.lower()}={value}&"

    # 去掉末尾多余的 &
    # if sign_string.endswith("&"):
    #     sign_string = sign_string[:-1]
    # print("需要sha-256的字符串" + sign_string)
    # SHA256 加密并转大写
    sign = hashlib.sha256(sign_string.encode('utf-8')).hexdigest().upper()
    return sign


def filter_items(items: list) -> list:
    allow = {"serious", "high_risk", "medium_risk", "low_risk", "unknown"}
    filtered_items = [item for item in items if item in allow]
    return filtered_items


@app.tool()
async def get_vulns(keyword: str = "", cve: str = "", publishTimeStart: str = "", publishTimeEnd: str = "",
                    vulnType: str = "", riskLevels: list = [], resultSize: int = 1) -> str:
    """
    :param keyword:可选模糊查询关键词，不传入该参数默认查询所有漏洞
    :param cve:可选漏洞的cve编号,可以不传该参数
    :param publishTimeStart:可选起始时间，查询起始时间后的漏洞,格式为yyyy-MM-dd HH:mm:ss
    :param publishTimeEnd:可选截止时间，查询截止时间前的漏洞,格式为yyyy-MM-dd HH:mm:ss
    :param vulnType:漏洞类型，可有可无，默认情况下不传该参数会查询所有类型。
    :param riskLevels:可选漏洞等级，类型为list,，其中只允许"serious","high_risk","medium_risk","low_risk","unknown"这五个元素存在，按
            顺序分别代表"严重，高危，中危，低危，未知"。
    :param resultSize:可选返回漏洞条数，默认情况下返回十条，resultSize的值只能是1-100。
    :return:查询结果
    """
    logging.root.handlers = []
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',  # 设置输出格式
        filename=log_file_path,  # 设置输出到文件
        filemode='w'  # 写入模式
    )
    # 获取token
    token = oauth()
    dict_parm = {
        'Authorization': 'Bearer {0}'.format(token),
        'ClientId': '43c1cef8d9371268',
        'Timestamp': int(time.time() * 1000),
        'Nonce': '00000',
    }
    # 生成签名
    sign = generate_sign(dict_parm, token)
    url = "https://vip.tophant.com/api/open/v2/vulns"
    headers = {
        'Authorization': f'Bearer {token}',
        'ClientId': '43c1cef8d9371268',
        'Timestamp': f"{int(time.time() * 1000)}",
        'Nonce': '00000',
        'sign': sign,
        'Content-Type': 'application/json',
    }

    data = {}
    if cve != "" and cve is not None:
        data['cve'] = [cve]
    if keyword != "" and keyword is not None:
        data['keyword'] = keyword
    if publishTimeStart != "" and publishTimeStart is not None:
        data['publishTimeStart'] = publishTimeStart
    if publishTimeEnd != "" and publishTimeEnd is not None:
        data['publishTimeEnd'] = publishTimeEnd
    if len(riskLevels) > 0 and riskLevels is not None:
        data['riskLevels'] = filter_items(riskLevels)
    if vulnType != "" and vulnType is not None:
        data['cweCodes'] = [vulnType_to_cweCode(find_most_similar(vulnType, vulnTypeList))]
    if resultSize > 1 and resultSize < 100:
        data['resultsPerPage'] = str(resultSize)
    logging.info(data)
    response = requests.post(url, headers=headers, json=data)
    res: dict = response.json()
    resultContent=[]
    for item in res['data']['records']:
        tmp={
            # 拼接XVI平台漏洞链接
            "vulnLink":"https://xvi.vulbox.com/detail/"+item['id'],
            # 漏洞id
            "id": item['id'],
            # 漏洞名
            "vulnName": item['vulnName'],
            # 漏洞等级
            "riskLevel": item['riskLevel'],
            # 漏洞相关编号
            "vulnCveCode":item['vulnCveCode'],
            "vulnCnvdCode":item['vulnCnvdCode'],
            "vulnCnnvdCode":item['vulnCnnvdCode'],
            # 漏洞CVSS3字符串
            "cvss3String": item['cvss3String'],
            # 漏洞CVSS3评分
            "cvss3Score": item['cvss3Score'],
            # 漏洞描述
            "vulnDesc": item['vulnDesc'],
            # 漏洞危害
            "vulnHarm":item['vulnHarm'],
            # 漏洞类型
            "cwes": item['cwes'],
            # 漏洞修复建议
            "fixes": item['fixes'],
        }
        resultContent.append(tmp)
        # del item['relateFormal']
    return resultContent.__str__()


def main():
    """Entry point for uvx package."""
    app.run(transport='stdio')
    asyncio.run(get_vulns(keyword="泛微"))

if __name__ == "__main__":
    main()
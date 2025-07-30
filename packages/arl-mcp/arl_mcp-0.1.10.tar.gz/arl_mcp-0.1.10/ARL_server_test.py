# ARL_server.py
import re
import time
import requests
import tldextract
import urllib3
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务，命名为 Math，可根据业务场景自定义名称
mcp = FastMCP("ARLMCP")

# 关闭 urllib3 的 HTTPS 不安全请求警告（用于测试阶段）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# BurpSuite 或其他代理配置（用于调试）
# proxies = {
#     'http': '127.0.0.1:8080',
#     'https': '127.0.0.1:8080'
# }

# 全局语言设置，默认为中文
REPLY_IN_CHINESE = True


@mcp.tool()
def extract_main_domain(RequestBody: str) -> str:
    """
    从原始 HTTP 数据包中提取主域名。

    参数：
    - RequestBody：包含 Host 字段的原始 HTTP 请求包

    返回：
    - 主域名，例如 'baidu.com'、'dzhsj.cn'。
    """
    match = re.search(r"Host:\s*([^\s:]+)", RequestBody)
    if not match:
        return "host not found"

    host = match.group(1).strip()
    extracted = tldextract.extract(host)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    return host  # fallback，当 tldextract 无法正确提取时


@mcp.tool()
def extract_domain_or_ip(text: str) -> str:
    """
    功能：根据输入文本判断并返回主域名、IP 地址或 IP 段。
    支持输入：域名字符串、IP 地址、IP 段（如 192.168.0.0/24）。
    注意：不解析完整 URL，只提取纯域名/IP。。

    参数：
    - text: str，用户输入，如 www.baidu.com、1.1.1.1、192.168.0.0/24

    返回：
    - str：提取出的主域名或 IP 内容。
    """
    if "/" in text or re.match(r"^\d+\.\d+\.\d+\.\d+", text):
        return text.strip()
    else:
        extracted = tldextract.extract(text)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        return text


@mcp.tool()
def detect_reply_language(user_prompt: str) -> str:
    """
    根据用户输入自动检测语言，设置全局 REPLY_IN_CHINESE 标志。

    参数：
    - user_prompt: 用户输入的原始提示

    返回：
    - 确认设置的语言提示信息
    """
    global REPLY_IN_CHINESE
    if re.search(r"[\u4e00-\u9fff]", user_prompt):
        REPLY_IN_CHINESE = True
        return "已自动切换为中文回复模式。"
    else:
        REPLY_IN_CHINESE = False
        return "Auto-switched to English reply mode."


@mcp.tool()
def add_scan_task_and_prompt(
    name: str,
    target: str,
    domain_brute: bool = True,
    alt_dns: bool = True,
    dns_query_plugin: bool = True,
    arl_search: bool = True,
    port_scan: bool = True,
    skip_scan_cdn_ip: bool = True,
    site_identify: bool = True,
    search_engines: bool = True,
    site_spider: bool = True,
    file_leak: bool = True,
    findvhost: bool = True
) -> dict:
    """
    工具名称：add_scan_task_and_prompt
    功能：向 ARL 平台提交扫描任务，并向用户返回预计完成时间提示。
    调用时机：
    - 用户首次请求扫描时调用。
    - 调用后应终止 AI 会话，等待用户后续手动查询。
    参数：
    - name: str
      任务名称，建议唯一，如 'scan-example.com'。
    - target: str
      扫描目标，支持主域名、IP 地址、IP 段。
    - domain_brute: bool
      是否启用子域名爆破（推荐目标为域名时启用）。
    - alt_dns: bool
      是否启用备用 DNS 查询（辅助子域名发现）。
    - dns_query_plugin: bool
      是否启用 DNS 查询插件（用于增强域名解析能力）。
    - arl_search: bool
      是否启用 ARL 历史资产查询（快速聚合已有数据）。
    - port_scan: bool
      是否启用端口扫描（推荐目标为 IP 或 IP 段时启用）。
    - skip_scan_cdn_ip: bool
      是否跳过已识别为 CDN 的 IP 端口扫描。
    - site_identify: bool
      是否启用站点指纹识别（推荐 Web 资产目标时启用）。
    - search_engines: bool
      是否启用搜索引擎资产搜索（辅助信息收集）。
    - site_spider: bool
      是否启用站点爬虫（对站点页面进行爬取和数据采集）。
    - file_leak: bool
      是否启用文件泄露检测（检测常见泄露路径和文件）。
    - findvhost: bool
      是否启用 VHOST 碰撞（辅助识别虚拟主机）。
    返回：
    - dict，包含任务提交结果、下一步提示。
    AI 建议：
    - 返回内容应直接展示给用户，告知预计等待时间，并提示后续输入如何触发状态查询。
    """
    url = "https://39.105.57.223:5003/api/task/"
    headers = {
        "Content-Type": "application/json",
        "Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg",
        "Accept": "application/json"
    }
    payload = {
        "name": name,
        "target": target,
        "domain_brute_type": "big",
        "port_scan_type": "top1000",
        "domain_brute": domain_brute,
        "alt_dns": alt_dns,
        "dns_query_plugin": dns_query_plugin,
        "arl_search": arl_search,
        "port_scan": port_scan,
        "service_detection": False,
        "os_detection": False,
        "ssl_cert": False,
        "skip_scan_cdn_ip": skip_scan_cdn_ip,
        "site_identify": site_identify,
        "search_engines": search_engines,
        "site_spider": site_spider,
        "site_capture": False,
        "file_leak": file_leak,
        "findvhost": findvhost,
        "nuclei_scan": False
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, verify=False)
        if resp.status_code != 200:
            return {
                "status": "fail",
                "reason": f"HTTP {resp.status_code}",
                "next_step": "请稍后手动查询任务状态"
            }

        data = resp.json()
        msg = (
            f"任务已成功创建：{name}\n"
            f"目标：{target}\n"
            f"预估子域名枚举完成时间：5-10 分钟\n"
            f"预估文件泄露检测完成时间：15-30 分钟\n"
            f"请稍后输入：查询任务状态 {name}\n"
            f"以检查扫描进度并决定是否提取数据。"
        )
        return {
            "status": "success",
            "task_info": data,
            "message": msg
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
            "next_step": "请稍后手动查询任务状态"
        }

@mcp.tool()
def query_task_status(name: str) -> dict:
    """
    工具名称：query_task_status
    参数：
    - name (str)：任务名称，例如 'scan-example.com'。

    工具名称：查询任务状态

    功能：
    查询指定任务的四大核心模块（子域名、IP、站点、文件泄露）的完成情况，返回清晰进度与下一步操作建议。


    返回：
    - 任务名
    - 各模块“已完成”或“未完成”标志
    - 友好的下一步操作提示

    使用示例 Prompt：
    - 查询任务状态 scan-vulbox.com
    - 任务 scan-vulbox.com 现在进展到哪一步了？
    - 当前扫描进度如何？

    返回结构样例：
    {
        "任务名": "scan-vulbox.com",
        "子域名爆破": "已完成",
        "IP收集": "未完成",
        "站点探测": "未完成",
        "文件泄露检测": "未完成",
        "下一步": "部分模块尚未完成：IP收集, 站点探测, 文件泄露检测。请稍后再次查询。全部完成后可输入：提取任务结果 scan-vulbox.com vulbox.com 获取详细结果。"
    }

    用途：
    - 适合首次任务提交后，立即反馈任务状态给用户，结束会话。
    - 用户可后续手动再次调用 query_task_status 检查进度。
    """
    url = "https://39.105.57.223:5003/api/task/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    params = {"name": name, "size": "1"}

    try:
        resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
        if resp.status_code != 200:
            return {
                "state": "error",
                "reason": f"HTTP {resp.status_code}"
            }
        data = resp.json()
        items = data.get("items", [])
        if not items:
            return {
                "state": "not_found"
            }

        item = items[0]
        completed_services = [s.get("name") for s in item.get("service", []) if s.get("name")]

        status_map = {
            "子域名爆破": "arl_search" in completed_services,
            "IP收集": "port_scan" in completed_services,
            "站点探测": "site_spider" in completed_services,
            "文件泄露检测": "file_leak" in completed_services
        }

        all_done = all(status_map.values())
        if all_done:
            next_step = f"全部模块已完成！请输入：提取任务结果 {name} vulbox.com 获取全部扫描数据。"
        else:
            next_step = f"部分模块尚未完成，请稍后再次查询。全部完成后可输入：提取任务结果 {name} vulbox.com 获取详细结果。"

        return {
            "任务名": name,
            "子域名爆破": "已完成" if status_map["子域名爆破"] else "未完成",
            "IP收集": "已完成" if status_map["IP收集"] else "未完成",
            "站点探测": "已完成" if status_map["站点探测"] else "未完成",
            "文件泄露检测": "已完成" if status_map["文件泄露检测"] else "未完成",
            "next_step": next_step
        }
    except Exception as e:
        return {
            "state": "exception",
            "reason": str(e)
        }

@mcp.tool()
def query_and_extract(name: str, domain: str) -> dict:
    """
       工具名称：提取任务结果

       功能：
       查询指定任务的状态，并自动获取所有已完成模块的数据（子域名、IP、站点、文件泄露）。未完成的模块自动提示等待。

       参数：
       - name: 任务名称，如 'scan-vulbox.com'
       - domain: 主域名，如 'vulbox.com'

       返回：
       - status: "done" 或 "running"
       - extracted_data: {各模块的数据列表}
       - 已完成模块
       - 未完成模块
       - 友好的下一步操作建议

       使用示例 Prompt：
       - 提取任务结果 scan-vulbox.com vulbox.com
       - 任务 scan-vulbox.com 的所有扫描结果是什么？
       - 获取 scan-vulbox.com 相关的全部子域名、IP、站点和文件泄露数据

       返回结构样例：
       {
           "status": "running",
           "extracted_data": {
               "subdomains": [...],
               "ips": [...]
           },
           "已完成模块": ["子域名爆破", "IP收集"],
           "未完成模块": ["站点探测", "文件泄露检测"],
           "next_step": "以下模块尚未完成：站点探测, 文件泄露检测。请等待其完成后再次输入：提取任务结果 scan-vulbox.com vulbox.com 获取最终数据。"
       }
       """
    status = query_task_status(name)

    # 异常或未找到直接返回
    if status.get("状态") in ["error", "exception", "not_found"]:
        return {
            "status": status.get("状态"),
            "reason": status.get("原因", "任务未找到或出错"),
            "next_step": f"请检查任务名称或稍后重新调用 提取任务结果 {name} {domain}"
        }

    # 已完成/未完成模块结构
    extracted_data = {}
    pending_modules = []

    # 子域名
    if status.get("子域名爆破") == "已完成":
        extracted_data["subdomains"] = get_all_subdomains(domain)
    else:
        pending_modules.append("子域名爆破")
    # IP
    if status.get("IP收集") == "已完成":
        extracted_data["ips"] = query_ip_list(domain)
    else:
        pending_modules.append("IP收集")
    # 站点
    if status.get("站点探测") == "已完成":
        extracted_data["sites"] = query_site_list(domain)
    else:
        pending_modules.append("站点探测")
    # 文件泄露
    if status.get("文件泄露检测") == "已完成":
        extracted_data["fileleaks"] = query_fileleak_list(domain)
    else:
        pending_modules.append("文件泄露检测")

    all_done = len(pending_modules) == 0

    return {
        "status": "done" if all_done else "running",
        "已完成模块": [k for k in ["子域名爆破", "IP收集", "站点探测", "文件泄露检测"] if k not in pending_modules],
        "未完成模块": pending_modules,
        "extracted_data": extracted_data,
        "next_step":
            ("全部数据已提取，无需再次查询。" if all_done
             else f"以下模块尚未完成：{', '.join(pending_modules)}。请等待其完成后再次输入：提取任务结果 {name} {domain} 获取最终数据。")
    }


@mcp.tool()
def get_all_subdomains(domain: str) -> list[str]:
    """
    工具名称：get_all_subdomains
    功能：获取指定主域名下所有已发现的子域名（需确保子域名爆破模块已完成）。
    调用时机：
    - 仅在任务状态为 domain_brute_done 或 done 时调用，确保子域名枚举已完成。
    参数：
    - domain: 主域名，例如 'baidu.com'，'vulbox.com'
    返回：
    - 子域名列表，例如 ['a.baidu.com', 'b.baidu.com', ...]
    """
    url = "https://39.105.57.223:5003/api/domain/"
    headers = {
        "Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"
    }
    page = 1
    size = 100
    subdomains = []

    try:
        while True:
            params = {
                "domain": domain,
                "page": page,
                "size": size
            }
            response = requests.get(url, headers=headers, params=params,verify=False)
            #response = requests.get(url, headers=headers, params=params, verify=False)
            if response.status_code != 200:
                return [f"Request failed: {response.status_code}"]

            json_data = response.json()
            items = json_data.get("items", [])
            if not items:
                break

            subdomains += [item.get("domain") for item in items if item.get("domain")]

            if len(items) < size:
                break

            page += 1

        return list(set(subdomains))
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def query_ip_list(domain: str) -> list[str]:
    """
    工具名称：query_ip_list
    功能：获取指定主域名下所有已发现的IP地址（需确保端口扫描模块已完成）。
    调用时机：
    - 仅在任务状态为 ip_done 或 done 时调用，确保 IP 数据已收集完成。
    参数：
    - domain: 主域名，例如 'dzhsj.cn'，'vulbox.com'
    返回：
    - IP 地址列表，例如 ['1.2.3.4', ...]
    """
    url = "https://39.105.57.223:5003/api/ip/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_ips = []

    try:
        while True:
            params = {"domain": domain, "page": page, "size": size}
            resp = requests.get(url, headers=headers, params=params,verify=False, timeout=10)
            #resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
            data = resp.json()
            items = data.get("items", [])
            all_ips.extend([item.get("ip") for item in items if item.get("ip")])
            if len(items) < size:
                break
            page += 1
        return all_ips
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def query_site_list(domain: str) -> list[str]:
    """
    工具名称：query_site_list
    功能：获取指定主域名下所有已发现的站点URL（需确保站点识别模块已完成）。
    调用时机：
    - 仅在任务状态为 site_done 或 done 时调用，确保站点识别已完成。
    参数：
    - domain: 主域名，例如 'dzhsj.cn'，'vulbox.com'
    返回：
    - 站点URL列表，例如 ['http://a.dzhsj.cn', ...]
    """
    url = "https://39.105.57.223:5003/api/site/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_sites = []

    try:
        while True:
            params = {"site": domain, "page": page, "size": size}
            resp = requests.get(url, headers=headers, params=params,verify=False, timeout=10)
            #resp = requests.get(url, headers=headers, params=params,verify=False, timeout=10)
            data = resp.json()
            items = data.get("items", [])
            all_sites.extend([item.get("site") for item in items if item.get("site")])
            if len(items) < size:
                break
            page += 1
        return all_sites
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def query_fileleak_list(domain: str) -> list[str]:
    """
    工具名称：query_fileleak_list
    功能：获取指定主域名下所有已发现的泄露文件URL（需确保文件泄露模块已完成）。
    调用时机：
    - 仅在任务状态为 fileleak_done 或 done 时调用，确保文件泄露扫描已完成。
    参数：
    - domain: 主域名，例如 'baidu.com'，'vulbox.com'
    返回：
    - 泄露文件URL列表，例如 ['http://a.baidu.com/.git/config', ...]
    """

    url = "https://39.105.57.223:5003/api/fileleak/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_urls = []

    try:
        while True:
            params = {"url": domain, "page": page, "size": size}
            resp = requests.get(url, headers=headers, params=params,verify=False, timeout=10)
            #resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
            data = resp.json()
            items = data.get("items", [])
            all_urls.extend([item.get("url") for item in items if item.get("url")])
            if len(items) < size:
                break
            page += 1
        return all_urls
    except Exception as e:
        return [f"Error: {str(e)}"]


if __name__ == "__main__":
    print("[+] mcp demo 正在运行11")
    mcp.run(transport="sse")

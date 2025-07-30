# ARL_server.py
import re
import time
import requests
import tldextract
import urllib3
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务，命名为 Math，可根据业务场景自定义名称
mcp = FastMCP("Math")

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
def sleep_for(seconds: int) -> str:
    """
    用于 LangGraph / MCP 自动化流程中节流调用频率。建议与 query_task_status 搭配使用，每次轮询间隔 60~120 秒。

    参数：
    - seconds: int，休眠时长（秒）

    返回：
    - 提示信息字符串，如 "slept for 60 seconds"
    """
    time.sleep(seconds)
    return f"slept for {seconds} seconds" if not REPLY_IN_CHINESE else f"已休眠 {seconds} 秒"


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
def add_scan_task(
    name: str,
    target: str,
    domain_brute: bool,
    alt_dns: bool,
    dns_query_plugin: bool,
    arl_search: bool,
    port_scan: bool,
    skip_scan_cdn_ip: bool,
    site_identify: bool,
    search_engines: bool,
    site_spider: bool,
    file_leak: bool,
    findvhost: bool
):
    """
    根据传入的参数，先创建一个 ARL 平台的扫描任务。

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
    - 包含任务提交状态和响应内容的字典
    """
    url = "https://127.0.0.1:5003/api/task/"
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
        data = resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else resp.text
        msg = "Task created successfully" if not REPLY_IN_CHINESE else "任务创建成功"
        return {"status_code": resp.status_code, "message": msg, "response": data}
    except Exception as e:
        return {"status_code": -1, "error": str(e)}


@mcp.tool()
def query_task_status(name: str) -> dict:
    """
    先创建任务,再查询 ARL 扫描任务的当前执行状态，返回详细模块完成标志。：
    - domain_brute_done：可调用 get_all_subdomains
    - ip_done：可调用 query_ip_list
    - site_done：可调用 query_site_list,该模块完成时间较长,sleep时间较长时(30分钟),可先断开会话并提示用户输入继续时，再次执行query_task_status方法查询任务状态，根据状态判断是否可以调用query_site_list
    - fileleak_done：可调用 query_fileleak_list。该模块完成时间较长,sleep时间较长时(30分钟),可先断开会话并提示用户输入继续时，再次执行query_task_status方法查询任务状态，根据状态判断是否可以调用query_fileleak_list
    - done：所有模块均已完成，可提取全部数据
    - running：任务进行中，建议 sleep 后重试

    参数：
    - name: str，任务名称，如 'scan-example.com'

    - dict 格式：
      {
        "state": str，状态关键词，可为：
            - "done"：所有模块已执行完成，全部数据可提取；
            - "running"：任务仍在执行中，建议 sleep 后轮询；

        "current_module": str，当前正在执行的模块名称（例如 "port_scan"、"site_spider"），
            如果任务已完成则可能为 "done"。

        "completed_modules": list[str]，已完成模块名称列表，
            例如 ["arl_search", "port_scan"]，可用于判断各模块完成进度。

        "domain_brute_done": bool，是否已完成域名爆破或聚合任务；
            True 表示已完成，可调用 get_all_subdomains；
            False 表示尚未完成。

        "ip_done": bool，是否已完成端口扫描或 IP 数据收集；
            True 表示已完成，可调用 query_ip_list；
            False 表示尚未完成。

        "site_done": bool，是否已完成站点探测；
            True 表示已完成，可调用 query_site_list；
            False 表示尚未完成。

        "fileleak_done": bool，是否已完成文件泄露扫描；
            True 表示已完成，可调用 query_fileleak_list；
            False 表示尚未完成。
      }
    推荐用途：
    - LangGraph 条件节点判断是否允许调用具体查询函数（如 get_all_subdomains）
    - 配合 sleep 节流避免 MCP 递归过快触发 RecursionError

    节流建议：
    - 若返回 running 状态，请间隔 30~60 秒调用；
    - 若状态为 *_done 或 done，即可安全执行后续步骤；
    - 超过 10 分钟未完成应终止流程并提示。
    """
    url = "https://127.0.0.1:5003/api/task/"
    headers = {
        "Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg",
        "Accept": "application/json"
    }
    params = {"name": name, "size": "1"}

    try:
        resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
        if resp.status_code != 200:
            return {"state": "error", "reason": f"HTTP {resp.status_code}"}

        data = resp.json()
        items = data.get("items", [])
        if not items:
            return {"state": "not_found"}

        item = items[0]
        current_status = item.get("status", "unknown")
        completed_services = [s.get("name") for s in item.get("service", []) if s.get("name")]

        return {
            "state": "done" if current_status == "done" else "running",
            "current_module": current_status,
            "completed_modules": completed_services,
            "domain_brute_done": "arl_search" in completed_services,
            "ip_done": "port_scan" in completed_services,
            "site_done": "site_spider" in completed_services,
            "fileleak_done": "file_leak" in completed_services
        }

    except Exception as e:
        return {"state": "exception", "reason": str(e)}


@mcp.tool()
def get_all_subdomains(domain: str) -> list[str]:
    """
    工具名称：get_all_subdomains
    功能：在确认 ARL 子域名爆破或聚合任务完成（state = domain_brute_done 或 done）后调用。分页获取指定主域名下发现的所有子域名。

    调用时机：
    - 仅在任务状态为 domain_brute_done 或 done 时调用，确保子域名枚举已完成。
    - 若状态尚未完成，建议等待后重试（配合 query_task_status 和 sleep_for 工具）。

    调用时机：
    - 仅在任务状态为 ip_done 或 done 时调用，确保 IP 数据已收集完成。
    - 若状态尚未完成，建议等待后重试（配合 query_task_status 和 sleep_for 工具）。


    参数：
    - domain: 主域名，例如 'baidu.com'

    返回：
    - 子域名列表，例如 ['a.baidu.com', 'b.baidu.com', ...]
    """
    url = "https://127.0.0.1:5003/api/domain/"
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
            response = requests.get(url, headers=headers, params=params,  verify=False)
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
    功能：在确认 ARL 端口扫描模块完成（state = ip_done 或 done）后调用。分页获取指定主域名下其余IP 地址。

    调用时机：
    - 仅在任务状态为 ip_done 或 done 时调用，确保 IP 数据已收集完成。
    - 若状态尚未完成，建议等待后重试（配合 query_task_status 和 sleep_for 工具）。
    参数：
    - domain: 主域名，例如 'dzhsj.cn'

    返回：
    - IP 地址列表
    """
    url = "https://127.0.0.1:5003/api/ip/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_ips = []

    try:
        while True:
            params = {"domain": domain, "page": page, "size": size}
            resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
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
    功能：在确认 ARL 任务中站点识别模块完成（state = site_done 或 done）后调用。分页获取指定主域名下发现的站点 URL 列表。
    调用时机：
    - 仅在任务状态为 site_done 或 done 时调用，确保站点识别已完成。
    - 若状态尚未完成，建议等待后重试（配合 query_task_status 和 sleep_for 工具）。
    参数：
    - domain: 主域名，例如 'dzhsj.cn'

    返回：
    - 站点 URL 列表
    """
    url = "https://127.0.0.1:5003/api/site/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_sites = []

    try:
        while True:
            params = {"site": domain, "page": page, "size": size}
            resp = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
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
    功能：在确认 ARL 文件泄露扫描模块完成（state = fileleak_done 或 done）后调用。分页获取指定主域名下发现的泄露文件链接。

    调用时机：
    - 仅在任务状态为 fileleak_done 或 done 时调用，确保文件泄露扫描已完成。
    - 若状态尚未完成，建议等待后重试（配合 query_task_status 和 sleep_for 工具）。

    参数：
    - domain: 主域名，例如 'baidu.com'

    返回：
    - 泄露链接列表
    """
    url = "https://127.0.0.1:5003/api/fileleak/"
    headers = {"Token": "7AEwZC3eOJ6A4rLjXqRZ0PVx00L8EfkeVg"}
    page, size = 1, 100
    all_urls = []

    try:
        while True:
            params = {"url": domain, "page": page, "size": size}
            resp = requests.get(url, headers=headers, params=params,  verify=False, timeout=10)
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



def main():
    print("[+] mcp demo 正在运行0.1.9")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
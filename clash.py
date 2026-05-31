#!python3.9
# -*- encoding: utf-8 -*-

import requests, re, yaml
from re import Pattern
from typing import Any, Dict, List, Set, Tuple

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

rss_url:str = 'https://www.cfmem.com/feeds/posts/default?alt=rss'
# clash_reg:Pattern = re.compile(r'clash订阅链接：(?:&lt;/span&gt;&lt;span style=&quot;background-color: white; color: #111111; font-size: 15px;&quot;&gt;)?(https?.+?)(?:&lt;|<)/span(?:&gt;|>)')
clash_reg:Pattern = re.compile(r'href=&quot;(https?://[^&]+?\.yaml)&quot;.*?&gt;Clash')
# v2ray_reg:Pattern = re.compile(r'v2ray订阅链接：(?:&lt;/span &gt;&lt;/span &gt;&lt;/span &gt;&lt;span style=&quot;color: #111111;&quot;&gt;&lt;span style=&quot;font-size: 15px;&quot;&gt;)?(https?.+?)(?:&lt;|<)/span(?:&gt;|>)')

clash_output_file:str = './dist/clash_config.yaml'
clash_output_tpl:str = './clash.config.template.yaml'
# v2ray_output_file:str = './dist/v2ray.config.txt'

clash_extra:List[str] = ['https://free886.herokuapp.com/clash/proxies']

blacklist:Set[Tuple[str, str]] = set()
for line in open('blacklists.txt', encoding='utf-8'):
    line = line.strip()
    if not line or ':' not in line:
        continue
    server, port = line.rsplit(':', 1)
    blacklist.add((server, port))

def normalize_proxy_name(name:str) -> str:
    '''
    Use landing location for relay node names like US->HK, so country filters match
    the visible exit IP rather than the relay entry.
    '''
    for arrow in ('->', '→'):
        if arrow in name:
            return name.split(arrow)[-1].strip() + ' ⇽中转'
    if name.startswith('Relay_') and '-' in name:
        return name.rsplit('-', 1)[-1].strip() + ' ⇽中转'
    return name

def proxy_key(proxy:Dict[str, Any]) -> Tuple[str, str] | None:
    server = proxy.get('server')
    port = proxy.get('port')
    if server is None or port is None:
        return None
    return (str(server), str(port))

def clash_urls(html:str) -> List[str]:
    '''
    Fetch URLs For Clash
    '''
    # return clash_extra
    return clash_reg.findall(html)[0:2]

def v2ray_urls(html:str) -> List[str]:
    '''
    Fetch URLs For V2Ray
    '''
    # return v2ray_reg.findall(html)

def fetch_html(url:str) -> str | None:
    '''
    Fetch The Content Of url
    '''
    try:
        resp:requests.Response = requests.get(url, verify=False, timeout=10)
        if resp.status_code != 200:
            print(f'[!] Got HTTP Status Code {resp.status_code}')
            return None
        return resp.text
    except Exception as e:
        print(f'[-] Error Occurs When Fetching Content Of {url}')
        return None

def merge_clash(configs:List[str]) -> str:
    '''
    Merge Multiple Clash Configurations
    '''
    config_template:Dict[str, Any] = yaml.safe_load(open(clash_output_tpl, encoding='utf-8').read())
    proxies:List[Dict[str, Any]] = []
    seen:Set[Tuple[str, str]] = set()
    for i in range(len(configs)):
        try:
            tmp_config:Dict[str, Any] = yaml.safe_load(configs[i])
        except Exception:
            continue
        if not isinstance(tmp_config, dict): continue
        tmp_proxies = tmp_config.get('proxies')
        if not isinstance(tmp_proxies, list): continue
        for j in range(len(tmp_proxies)):
            raw_proxy = tmp_proxies[j]
            if not isinstance(raw_proxy, dict): continue
            key = proxy_key(raw_proxy)
            if key is None or key in blacklist or key in seen: continue
            proxy:Dict[str, Any] = dict(raw_proxy)
            seen.add(key)
            nm:str = normalize_proxy_name(str(proxy.get('name', '')))
            proxy['name'] = nm + f'_{i}@{j}'
            proxies.append(proxy)
    config_template['proxies'] = proxies

    return yaml.safe_dump(config_template, indent=1, allow_unicode=True, sort_keys=False)

def merge_v2ray(configs:List[str]) -> str:
    '''
    Merge Multiple V2Ray Configurations
    '''
    return '\n'.join(configs)

def main():
    rss_text:str = fetch_html(rss_url)
    if rss_text is None or len(rss_text) <= 0: 
        print('[-] Failed To Fetch Content Of RSS')
        return
    clash_url_list:List[str] = clash_urls(rss_text)
    # v2ray_url_list:List[str] = v2ray_urls(rss_text)
    print(f'[+] Got {len(clash_url_list)} Clash URLs')

    clash_configs:List[str] = list(filter(lambda h: h is not None and len(h) > 0, map(lambda u: fetch_html(u), clash_url_list)))
    # v2ray_configs:List[str] = list(filter(lambda h: h is not None and len(h) > 0, map(lambda u: fetch_html(u), v2ray_url_list)))

    clash_merged:str = merge_clash(clash_configs)
    # v2ray_merged:str = merge_v2ray(v2ray_configs)

    with open(clash_output_file, 'w', encoding='utf-8') as f: f.write(clash_merged)
    # with open(v2ray_output_file, 'w') as f: f.write(v2ray_merged)

if __name__ == '__main__':
    main()

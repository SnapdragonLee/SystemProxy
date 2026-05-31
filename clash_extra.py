import requests
import yaml
import urllib3
import concurrent.futures
from typing import Any, Dict, List, Set, Tuple

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

clash_output_file: str = './dist/clash_config_extra.yaml'
clash_output_file_usa: str = './dist/clash_config_extra_US.yaml'
clash_output_tpl: str = './clash.config.template.yaml'

clash_extra: List[str] = [
    'https://fetchjiedian.feisu360.xyz/clash/proxies',
    'http://150.230.195.209:12580/clash/proxies',
    'http://175.178.182.178:12580/clash/proxies',
    'http://66.42.50.118:12580/clash/proxies',
    'http://beetle.lander.work/clash/proxies',
    'https://proxy.yiun.xyz/clash/proxies',
    'https://proxy.fldhhhhhh.top/clash/proxies',
    'https://proxy.yugogo.xyz/clash/proxie',
    'https://proxy.crazygeeky.com/clash/proxies',
    'https://proxypool1999.banyunxiaoxi.icu/clash/proxies',
    'https://pxypool.131433.xyz/clash/proxies',
    'https://proxypool.link/clash/proxies',
    'https://pool.sagithome.com/clash/proxies',
    'https://clashe.eu.org/clash/proxies',
    'https://laxcity.pages.dev/clash/proxies',
    'https://rvorch.treze.cc/clash/proxies',
    'https://free.dsdog.tk/clash/proxies',
    'https://free.jingfu.cf/clash/proxies',
    'https://free.iam7.tk/clash/proxies',
]

blacklist: Set[Tuple[str, str]] = set()
for line in open('blacklists.txt', encoding='utf-8'):
    line = line.strip()
    if not line or ':' not in line:
        continue
    server, port = line.rsplit(':', 1)
    blacklist.add((server, port))


def normalize_proxy_name(name: str) -> str:
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


def proxy_key(proxy: Dict[str, Any]) -> Tuple[str, str] | None:
    server = proxy.get('server')
    port = proxy.get('port')
    if server is None or port is None:
        return None
    return (str(server), str(port))


def clash_urls() -> List[str]:
    '''
    Fetch URLs For Clash
    '''
    return clash_extra


def fetch_html(url: str) -> str | None:
    '''
    Fetch The Content Of url
    '''
    try:
        resp: requests.Response = requests.get(url, verify=False, timeout=10)
        if resp.status_code != 200:
            print(f'[!] Got HTTP Status Code {resp.status_code} at {url}')
            return None
        return resp.text
    except Exception as e:
        print(f'[-] Error Occurs When Fetching Content Of {url}: {e}')
        return None


def fetch_multiple_urls(urls: List[str]) -> List[str | None]:
    '''
    Fetch Multiple URLs Concurrently
    '''
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(fetch_html, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                results.append(data)
            except Exception as e:
                print(f'[-] Fetching {url} generated an exception: {e}')

    return results


def merge_clash(configs: List[str], filter_usa: bool) -> str:
    '''
    Merge Multiple Clash Configurations

    :param filter_usa: A boolean indicating whether to keep only US landing proxies
    '''
    config_template: Dict[str, Any] = yaml.safe_load(open(clash_output_tpl, encoding='utf-8').read())
    proxies: List[Dict[str, Any]] = []
    seen: Set[Tuple[str, str]] = set()
    for i in range(len(configs)):
        try:
            tmp_config: Dict[str, Any] = yaml.safe_load(configs[i])
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
            proxy: Dict[str, Any] = dict(raw_proxy)
            seen.add(key)

            nm: str = normalize_proxy_name(str(proxy.get('name', '')))

            if filter_usa and "🇺🇸" not in nm and "US" not in nm: continue

            proxy['name'] = nm + f'_{i}@{j}'
            proxies.append(proxy)
    config_template['proxies'] = proxies

    return yaml.safe_dump(config_template, indent=1, allow_unicode=True, sort_keys=False)


def main():
    clash_url_list: List[str] = clash_urls()
    print(f'[+] Got {len(clash_url_list)} Clash URLs')

    clash_configs: List[str] = fetch_multiple_urls(clash_url_list)

    clash_configs = list(filter(lambda h: h is not None and len(h) > 0, clash_configs))

    # 调用 merge_clash 函数时指定是否过滤 🇺🇸
    clash_merged_all: str = merge_clash(clash_configs, filter_usa=False)

    with open(clash_output_file, 'w', encoding='utf-8') as f:
        f.write(clash_merged_all)

    clash_merged_all_usa: str = merge_clash(clash_configs, filter_usa=True)
    with open(clash_output_file_usa, 'w', encoding='utf-8') as f:
        f.write(clash_merged_all_usa)


if __name__ == '__main__':
    main()

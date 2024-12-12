import requests
import yaml
import urllib3
import concurrent.futures
from typing import Any, Dict, List

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

blacklist: List[str] = list(
    map(lambda l: l.replace('\r', '').replace('\n', '').split(':'), open('blacklists.txt').readlines()))


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


def fetch_multiple_urls(urls: List[str]) -> List[str]:
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

    :param filter_usa: A boolean indicating whether to filter out proxies with names starting with 🇺🇸
    '''
    config_template: Dict[str, Any] = yaml.safe_load(open(clash_output_tpl, encoding='utf-8').read())
    proxies: List[Dict[str, Any]] = []
    for i in range(len(configs)):
        try:
            tmp_config: Dict[str, Any] = yaml.safe_load(configs[i])
        except Exception:
            continue
        if 'proxies' not in tmp_config: continue
        for j in range(len(tmp_config['proxies'])):
            proxy: Dict[str, Any] = tmp_config['proxies'][j]
            if any(filter(lambda p: p[0] == proxy['server'] and str(p[1]) == str(proxy['port']), blacklist)): continue
            if any(filter(lambda p: p['server'] == proxy['server'] and p['port'] == proxy['port'], proxies)): continue

            if filter_usa and "🇺🇸" not in proxy['name'] and "US" not in proxy['name']: continue

            proxy['name'] = proxy['name'] + f'_{i}@{j}'
            proxies.append(proxy)
    node_names: List[str] = list(map(lambda n: n['name'], proxies))
    config_template['proxies'] = proxies
    for grp in config_template['proxy-groups']:
        if 'xxx' in grp['proxies']:
            grp['proxies'].remove('xxx')
            grp['proxies'].extend(node_names)

    return yaml.safe_dump(config_template, indent=1, allow_unicode=True)


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

import urllib3
from bs4 import BeautifulSoup
import pickle
import requests

proxies = [
    '83.97.119.51:8085',
    '193.233.248.85:8085',
    '193.233.248.160:8085',
    '83.97.119.95:8085',
    '185.14.194.234:8085',
    '193.233.248.153:8085',
    '5.133.122.228:8085',
    '83.97.119.62:8085',
    '193.233.248.50:8085',
    '83.97.119.89:8085',
    '5.133.122.138:8085',
    '79.110.31.94:8085',
    '193.233.248.146:8085'
]

def get_html(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    return response.data

def check_proxy(px):
    try:
        requests.get("https://google.com/", proxies = {"http": "http://" + px})
        print(px)
    except Exception as x:
        print('--'+px + ' невалидный: '+ x.__class__.__name__)

def get_proxy(scrap = False):
    global px_list
    if scrap or len(px_list) < 6:
            px_list = scrap_proxy()
    while True:
        if len(px_list) < 6:
            px_list = scrap_proxy()
        px = px_list.pop()
        if check_proxy(px):
            break
    print('-'+px+' is alive. ({} left)'.format(str(len(px_list))))
    with open('proxis.pickle', 'wb') as f:
            pickle.dump(px_list, f)
    return px

def scrap_proxy():
    global px_list
    px_list = set()
    source_code = get_html('https://hidemy.name/en/proxy-list/')
    soup = BeautifulSoup(source_code, features="html.parser", from_encoding="utf-8")
    print(soup)
    # proxies = soup.findAll('tr', class_='spy1x')
    # for index, proxy in enumerate(proxies):
    #     print(proxy)

    #     proxy_ip = proxy.findAll('td')[0].text
    #     proxy_port = proxy.findAll('td')[1].text
    #     proxy_https = proxy.findAll('td')[6].text
    #     if proxy_https == 'no':
    #         continue
    #     px_list.add(':'.join([proxy_ip, proxy_port]))
    # return list(px_list)

if __name__ == '__main__':
    for proxy in proxies:
        proxy = proxy.strip()
        check_proxy(proxy)
import math
import re
import os
import time
import sys, traceback
import codecs
import urllib.request
import requests
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Proxy
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from multiprocessing.pool import ThreadPool
import queue
import concurrent.futures
import random
import pymysql.cursors
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from .models import Result_8, Needs_8

# Учетные данные autodoc
login = ''
password = ''

accounts = [
    {'user' : '', 'password' : ''},
    {'user' : '', 'password' : ''},
    {'user' : '', 'password' : ''},
    {'user' : '', 'password' : ''},
    {'user' : '', 'password' : ''}
]

MAX_WORKERS = 5

def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver

def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )

def click_through_to_new_page(link_text, browser):
    link = browser.find_element_by_link_text('my link')
    link.click()

    def link_has_gone_stale():
        try:
            # poll the link with an arbitrary call
            link.find_elements_by_id('doesnt-matter')
            return False
        except StaleElementReferenceException:
            return True

    wait_for(link_has_gone_stale)

class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)

class AutoApi():
    def __init__(self, login, password, **kwargs):
        self.login = login
        self.password = password
        self.api_url = 'https://autodoc.ru'
        # chromeOptions = Options()
        chromeOptions = webdriver.ChromeOptions()
        self.manufacturers = []
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-setuid-sandbox")
        chromeOptions.add_argument("--disable-dev-shm-using")
        chromeOptions.add_argument("--disable-extensions")
        chromeOptions.add_argument("--disable-gpu")
        chromeOptions.add_argument("start-maximized")
        chromeOptions.add_argument("disable-infobars")
        chromeOptions.add_argument("--headless")
        # print(kwargs)
        if 'useragent' in kwargs:
            chromeOptions.add_argument(f'user-agent={kwargs["useragent"]}')
            self.userAgent = kwargs["useragent"]
        if 'proxy' in kwargs:
            self.proxy = kwargs['proxy']
            # chromeOptions.add_argument(f'--proxy-server=http://{self.proxy}')
        else:
            self.proxy = 'No proxy detected'

        if self.check_proxy(self.proxy) != False:
            settings = {
                "httpProxy": self.proxy,
                "sslProxy": self.proxy
            }
            proxy = Proxy(settings)
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            cap = DesiredCapabilities.CHROME.copy()
            proxy.add_to_capabilities(cap)
            self.driver = webdriver.Chrome('/home/parser/autodoc/autodoc/auto/chromedriver',
                                       options=chromeOptions,
                                       desired_capabilities=cap
                                       )
        else:
            self.driver = webdriver.Chrome('/home/parser/autodoc/autodoc/auto/chromedriver',
                                       options=chromeOptions
                                       )
        self.parse_man()

    def __repr__(self):
        return id(self)

    def driver_quit(self):
        self.driver.quit()

    def auth(self):
        try:
            self.driver.get(self.api_url)
            time.sleep(1)
            # performance_log = self.driver.get_log('performance')
            # print(str(performance_log).strip('[]'))
            #
            # for entry in self.driver.get_log('performance'):
            #     print(entry)
            btn_lk = self.driver.find_element_by_class_name('cabinet').find_element_by_tag_name('a')
            # btn_lk = WebDriverWait(self.driver, 20).until(
            #     EC.visibility_of_element_located((By.CLASS_NAME,
            #           # "/html/body/main-app/main-layout/div/header-layout/header/div[2]/div[1]/a"
            #           "cabinet"
            #     ))
            # )
            self.driver.execute_script('arguments[0].click();', btn_lk)
            # btn_lk = self.driver.find_element_by_xpath('/html/body/main-app/main-layout/div/header-layout/header/div[2]/div[1]/a').click()
            time.sleep(1)
            username = self.driver.find_element_by_xpath('//*[@id="Login"]').send_keys(self.login)
            passw = self.driver.find_element_by_xpath('//*[@id="Password"]').send_keys(self.password)
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="submit_logon_page"]').click()
            time.sleep(1)
            print('Авторизовались ' + self.login + ' : ' + self.password)
        except Exception as x:
            print('Ошибка авторизации: ' + x.__class__.__name__)
            self.driver.quit()
            return False

    def parse_man(self):
        self.driver.get(self.api_url + '/man')
        time.sleep(1)
        source = self.driver.page_source
        soup = BeautifulSoup(source, features="html.parser", from_encoding="utf-8")
        man_items = soup.findAll('div', class_='man-item')
        self.manufacturers.append({'name' : 'DAIHATSU', 'code' : '517'})
        self.manufacturers.append({'name': 'HINO', 'code': '615'})
        self.manufacturers.append({'name': 'BRILLIANCE', 'code': '6092'})
        self.manufacturers.append({'name': 'HAITUO', 'code': '6001'})
        self.manufacturers.append({'name': 'FAW', 'code': '6069'})
        for item in man_items:
            man_code = item.find('a', class_='man-item-link').get('href').replace('/man/', '')
            self.manufacturers.append({'name' : item.find('a').text, 'code' : man_code})

    def get_detail_code(self, company_name):
        for company in self.manufacturers:
            if company_name == company['name']:
                return company['code']

    def get_detail_info(self, pos):
        positions = []
        for position in pos:
            detail_link, company_name, sku = position
            try:
                self.driver.get(detail_link)
                # Нажимаем на кнопку Показать ещё, если она есть
                try:
                    btn = WebDriverWait(self.driver, 2).until(
                        EC.visibility_of_element_located((By.XPATH,
                      "/html/body/main-app/white-layout/div/div/price-component-app/div[2]/div[2]/div[1]/div/div/app-price-table/div/div[2]/app-price-inner-table/div/div/a"))
                    )
                    self.driver.execute_script('arguments[0].click();', btn)
                except Exception as x:
                    pass

                main_layout = WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((By.XPATH,
                      "/html/body/main-app/white-layout/div/div"))
                ).get_attribute('innerHTML')
                # time.sleep(random.randint(2,5))
                # main_layout = self.driver.find_element_by_xpath(
                #         '/html/body/main-app/white-layout/div/div'
                # ).get_attribute('innerHTML')
                soup = BeautifulSoup(main_layout, features="html.parser", from_encoding="utf-8")
                brand_head = soup.find('h1', class_='ng-star-inserted')
                brand_head.find('b').decompose()
                brand_head = brand_head.text.strip()
                not_details = soup.find('p', class_='notice-text')
                if not_details is None:
                    # tables = soup.findAll('table', class_='striped-price')
                    tables = soup.findAll('div', class_='box-original')
                    if len(tables) > 1:
                        table = tables[-1]
                    else:
                        table = tables[0]
                    brand = table.find('div', class_='pro-header-layout').find('div', class_='title-part').find('a', class_='company_info_link').text.strip()
                    detail_name = table.find('div', class_='pro-header-layout').find('div', class_='title-name').text
                    items = table.find('table', class_='striped-price').findAll('tr')
                    for item in items:
                        try:
                            item.find('div', class_='presence-mob').decompose()
                        except:
                            pass
                        price = re.sub('\.\d{2}', '', item.find('td', class_='price').text.replace(' ', ''))
                        count = item.find('td', class_='presence').text.strip()
                        if count == ' ' or count == '':
                            continue
                        delivery = item.find('td', class_='delivery').find('span', class_='delivery-number').text
                        diler = item.find('td', class_='direction').find('span').text
                        positions.append({'sku': sku,
                                          'name': detail_name,
                                          'manufacture': brand,
                                          'price': price,
                                          'delivery': delivery,
                                          'diler': diler,
                                          'qty': int(count),
                                          'source': 'Original'})
                else:
                    print(f'Нет предложений {sku} {brand_head} {detail_link}')
                    pass
            except Exception as x:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(x).__name__, x)
                print(f'Error {sku}. {login} {password}| {self.proxy}')
                print(f'Нет предложений {sku} {detail_link}')
                print(position)
                self.driver.save_screenshot(f'/home/parser/screens/{sku}.png')
                pass

        if len(positions) == 0:
            return False
        else:
            return positions

    def restart_code(self, sku):
        self.driver.get(self.api_url)
        search_field = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "partNumberSearch"))
        )
        search_field.clear()
        search_field.send_keys(sku)
        time.sleep(random.randint(1,2))
        search_btn = self.driver.find_element_by_class_name('search-button').find_element_by_class_name('sub')
        self.driver.execute_script("arguments[0].click();", search_btn)
        time.sleep(random.randint(2, 5))
        # Кликаем на кнопку Показать всех производителей
        try:
            btn_all = self.driver.find_element_by_id('buttonShowAll')
            self.driver.execute_script("arguments[0].click();", btn_all)
        except:
            pass

    def search_details(self, sku):
        self.driver.get(self.api_url)
        search_field = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.ID, "partNumberSearch"))
        )
        search_field.clear()
        search_field.send_keys(sku)
        time.sleep(random.randint(1,2))
        # with wait_for_page_load(self.driver):
        search_btn = self.driver.find_element_by_class_name('search-button').find_element_by_class_name('sub')
        self.driver.execute_script("arguments[0].click();", search_btn)
        self.driver.implicitly_wait(random.randint(13, 15))
        man_list = []
        try:
            company = self.driver.find_element_by_class_name('choose-company')
            # Кликаем на кнопку Показать всех производителей
            try:
                btn_all = self.driver.find_element_by_id('buttonShowAll')
                self.driver.execute_script("arguments[0].click();", btn_all)
            except:
                pass
            time.sleep(random.randint(1, 3))
            manufacters = company.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            manufacter_xpath = '/html/body/main-app/main-layout/div/header-layout/div[1]/header/search-spare-part-component/atd-popup/div/div/div[1]/div[2]/div/table/tbody/tr'
            for index, man in enumerate(manufacters):
                company_name = self.driver.find_element_by_xpath(manufacter_xpath + '[' + str(index + 1) + ']').find_element_by_class_name('company').text.strip()
                company_element = self.driver.find_element_by_xpath(manufacter_xpath + '[' + str(index + 1) + ']')
                code = self.get_detail_code(company_name)
                if code is None:
                    company_element.click()
                    self.driver.implicitly_wait(random.randint(10, 15))
                    man_code = self.driver.find_element_by_class_name('company_info_link').get_attribute('href').replace('https://www.autodoc.ru/man/','').strip()
                    self.manufacturers.append({'name': company_name, 'code': man_code})
                    code = man_code
                    self.restart_code(sku)
                detail_link = self.api_url + '/price/' + code + '/' + sku
                man_list.append([detail_link, company_name, sku])
            return man_list
        except Exception as x:
            # time.sleep(random.randint(2, 4))
            current_url = self.driver.current_url
            self.driver.implicitly_wait(random.randint(10, 15))
            man_list.append([current_url, '', sku])
            return man_list
            # return self.get_detail_info(current_url, '', sku)

    def check_proxy(self, proxy):
        try:
            r = requests.get("https://api.ipify.org", proxies={"http": "http://" + proxy})
            proxy_ip = proxy.split(':')[0]
            if proxy_ip == r.text:
                print('Подключились к прокси ' + proxy)
                return True
            else:
                return False
        except Exception as x:
            print('Не подключились к ' + proxy + ' Ошибка: ' + x.__class__.__name__ + ' Берём прокси из файла')
            with open(str(settings.BASE_DIR) + '/auto/proxy.txt', 'r', encoding='utf-8') as f:
                proxy_list = f.readlines()
                for proxy in proxy_list:
                    self.check_proxy(proxy)

def get_chuncked_sku_list(file):
    print(settings.BASE_DIR)
    with open(str(settings.BASE_DIR) + '/auto/' + str(file), 'r', encoding='utf-8') as f:
        skus_list = f.readlines()
        chuncks_list = []
        for j in range(0, len(skus_list), 40):
            next = j + 40
            ch_list = []
            for i in range(j, next):
                skus_list[i] = re.sub('\n|\r|\t', '', skus_list[i])
                ch_list.append(skus_list[i])
            chuncks_list.append(ch_list)
        return chuncks_list

chuncked_list = get_chuncked_sku_list('skus.txt')

def run_worker(log, passw, chuncked_list):
    selected_indexes = []
    for i in range(1,5):
        try:
            index = random.randint(0, len(chuncked_list))
            selected_indexes.append(index)
        except IndexError:
            continue
    print('Выбрали следующие элементы из спика:' + str(selected_indexes))
    print('------------------------------------------------------------------')
    api = AutoApi(login, password)
    auth = api.auth()
    if not auth is False:
        for index in selected_indexes:
            ch = chuncked_list[index]
            chuncked_list.remove(chuncked_list[index])
            time.sleep(random.randint(1,3))
            for ind, sku in enumerate(ch):
                pos = api.search_details(sku)
                print(str(ind) + ' ---- ' + str(pos))
            time.sleep(random.randint(600, 1200))

            print('Отпарсили подмассив')
        api.driver_quit()



# if __name__ == '__main__':
#     run_worker(login, password, chuncked_list)
    # chuncked_list = get_chuncked_sku_list('skus.txt')
    # with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    #     tasks = {executor.submit(AutoApi, login, password): i for i in range(1,MAX_WORKERS)}
    # api = AutoApi(login, password)
    # auth = api.auth()
    # if not auth is False:
    #     for skus in chuncked_list:
    #         for index, sku in enumerate(skus):
    #             pos = api.search_details(sku)
    #             print(str(index) + ' ---- ' + str(pos))
    #         time.sleep(random.randint(600,1200))
    #     api.driver_quit()


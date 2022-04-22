from celery.utils.log import get_task_logger
from celery import Celery, shared_task
from celery_progress.backend import ProgressRecorder
from autodoc.celery import app
import os
from .main import AutoApi, chuncked_list, accounts
from .models import Result_8, Needs_8, User
import time
from datetime import datetime
import random
import pickle
import redis
import json
import sys
import subprocess
from selenium import webdriver
from fake_useragent import UserAgent
logger = get_task_logger(__name__)

@shared_task(bind=True)
def start(self,login, password, proxy):
    try:
        useragent = UserAgent().random
    except:
        useragent = UserAgent().random

    api = AutoApi(login, password, useragent=useragent, proxy=proxy)
    r = redis.Redis(host='localhost', port=6379, db=0)

    print('-----------')
    print('Получили таску ' + login)
    json_data = {
        'user': login,
        'password': password,
        'useragent': api.userAgent,
        'proxy': api.proxy,
        'pid': api.driver.service.process.pid,
        'sucsess': False,
        'ban': False
    }
    json_data = json.dumps(json_data)
    acc_data_name = 'acc_data_' + str(api.driver.service.process.pid)
    r.set(acc_data_name, json_data)
    print('Авторизовываемся ' + login)
    auth = api.auth()
    if not auth is False:
        start_index = int(json.loads(r.get(login + '_chuncks'))['start_index'])
        chunck_size = int(float(r.get('chunck_size').decode('utf8')))

        list_for_parse = r.lrange('unparsed', start_index, start_index + chunck_size)

        wait_index = start_index + 40

        for index, item in enumerate(list_for_parse):
            self.update_state(state='PROGRESS',
                              meta={'current': item, 'total': len(list_for_parse)})
            if index == wait_index:
                wait_index = wait_index + 40
                time.sleep(random.randint(200, 600))

            value = Needs_8.objects.get(part_sought = item.decode('utf8'))
            time.sleep(random.randint(1, 3))
            pos = api.search_details(value.part_sought)
            print('------------------------------')
            print(pos)
            print('------------------------------')
            time.sleep(random.randint(5,10))
            details = api.get_detail_info(pos)
            if details != False:
                for detail in details:
                    new = Result_8(
                        id_1c_part=value.id_1c_part,
                        id_1c_doc=value.id_1c_doc,
                        part_sought=value.part_sought,
                        brand_sought=value.brand_sought,
                        part_result=detail['sku'],
                        brand_result=detail['manufacture'],
                        title=detail['name'],
                        price=float(detail['price']),
                        day=int(detail['delivery']),
                        qty=int(detail['qty']),
                        supplier=detail['diler'],
                        location='Москва',
                        source=detail['source'],
                        datetime=datetime.now()
                    )
                    new.save()
                Needs_8.objects.filter(part_sought=item.decode('utf8')).update(status=0)
                # Если в множестве unparsed_skus есть этот артикул, тогда удаляем его из unparsed_skus
                unparsed_obj = json.loads(json.dumps({
                    "login": login,
                    "value": value.part_sought
                }))
                for key in r.smembers('unparsed_skus'):
                    key = key.decode('utf8')
                    if key == unparsed_obj:
                        r.srem('unparsed_skus', key)
                time.sleep(random.randint(5,15))
            else:
                json_unparsed = {
                    "login": login,
                    "value": value.part_sought
                }
                r.sadd('unparsed_skus', str(json_unparsed))
                r.sadd('unparsed_middle', value.part_sought)
                r.rpush('data_process_'+login, value.part_sought)

            # Проверяем аккаунт на бан
            if r.llen('data_process_'+login) > 7:
                print(f'Возможно аккаунт забанили {login}:{password}  |  {proxy}')
                unparsed_list = r.lrange('data_process_'+login,0, -1)
                print(unparsed_list)
                json_data = {
                    'user': login,
                    'password': password,
                    'useragent': api.userAgent,
                    'proxy': api.proxy,
                    'pid': api.driver.service.process.pid,
                    'sucsess': False,
                    'ban': True
                }
                json_data = json.dumps(json_data)
                r.set(acc_data_name, json_data)
                self.update_state(state='BAN',
                                  meta={'current': item, 'total': len(list_for_parse)})

        # Если успешно спарсили указанные артикулы, обновляем данные аккаунта
        json_data = {
            'user': login,
            'password': password,
            'useragent': api.userAgent,
            'proxy': api.proxy,
            'pid': api.driver.service.process.pid,
            'sucsess': True,
            'ban': False
        }
        json_data = json.dumps(json_data)
        r.set(acc_data_name, json_data)
        api.driver_quit()

@shared_task(bind=True)
def kill_chrome(self):
    os.system('pkill -f "chrome"')
    os.system('pkill -f "chromedriver"')

@shared_task(bind=True)
def shutdown(self):
    app.control.broadcast('shutdown', destination=[self.request.hostname])



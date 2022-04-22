import time
import ast
from datetime import datetime
import random
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from .main import login, password
from .tasks import start, shutdown, kill_chrome
from autodoc.celery import app
from celery import group
from celery import result, Celery

from celery import current_app
from .main import AutoApi, attach_to_session
from .models import Result_8, Needs_8, User
# from .dbconn import DB_api
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
from celery.result import AsyncResult
import os
import pickle
import sys
import redis
import json
import re
import ctypes

tasks = []

port = '20080'

import gc

def objects_by_id(id_):
    for obj in gc.get_objects():
        if id(obj) == id_:
            return obj

def str_to_class(classname):
    return getattr(sys.modules[__name__], str(classname))

def init(request, **kwargs):
    server_host = 'https://' + str(get_current_site(request).domain) + f':{port}'
    os.system('pkill -f "celery worker"')
    context = {'host': server_host}
    return render(request, 'index.html', context=context)

def index(request, **kwargs):
    # async_result = start.delay(login, password)
    # current_app.loader.import_default_modules()
    # Определяем зарегестрированные таски
    # tasks = list(sorted(name for name in current_app.tasks
    #                     if not name.startswith('celery.')))
    server_host = 'https://' + str(get_current_site(request).domain) + f':{port}'
    r = redis.Redis(host='localhost', port=6379, db=0)

    if r.get('running').decode('utf') == 'no':
        os.system('pkill -f "chrome"')
        os.system('pkill -f "chromedriver"')
    try:
        time_run = r.get('time_run').decode('utf8')
        time_run = re.sub('\.\d{4,}','', time_run)
        time_run_object = datetime.strptime(time_run, "%Y-%m-%d %H:%M:%S")
    except:
        time_run = ''
        time_run_object = datetime.now()
    try:
        accs = []
        running_accs = []
        for key in r.scan_iter():
            key = key.decode('utf8')
            if 'acc_data_' in key:
                running_accs.append(key)
        for key in running_accs:
            acc_data = json.loads(r.get(key))
            accs.append(acc_data)
    except:
        accs = ''

    details = ''
    details_chuncks = []
    try:
        details = Result_8.objects.filter(datetime__range=[time_run_object, datetime.now()])
    except:
        pass

    unparsed_skus = [json.loads(value.decode('utf-8').replace("'",'"')) for value in list(r.smembers('unparsed_skus'))]
    unparsed_middle = [value for value in list(r.smembers('unparsed_middle'))]
    success_tasks = []
    pending_tasks = []
    ban_tasks = []
    for task in tasks:
        # res = result.AsyncResult(task.task_id, app=app)
        if task.state == 'PROGRESS':
            pending_tasks.append(task.task_id)
        if task.state == 'SUCCESS':
            success_tasks.append(task.task_id)
        if task.state == 'BAN':
            ban_tasks.append(task.task_id)
    print('Success tasks count:' + str(len(success_tasks)))
    print('Pending tasks count:' + str(len(pending_tasks)))

    # Отправляем неспарсенные артикулы на перепарс
    print('ban_tasks ' + str(len(ban_tasks)))
    print('success_tasks ' + str(len(success_tasks)))
    print('tasks ' + str(len(tasks)))
    print('unparsed_skus '+str(len(unparsed_skus)))

    if r.get('perepars').decode('utf-8') != 'no':
        if len(unparsed_skus) > 0:
            for l in range(2):
                if l == 2:
                    r.set('perepars', 'no')
                else:
                    if len(ban_tasks) + len(success_tasks) == len(tasks) and len(tasks) > 0:
                        for y in range(3):
                            os.system('pkill -f "chrome"')
                            os.system('pkill -f "chromedriver"')
                        time.sleep(random.randint(2,7))
                        print('Отправляем на перепарс')
                        return HttpResponseRedirect("/run/")

    if len(unparsed_skus) > 10:
        unparsed_skus = unparsed_skus[len(unparsed_skus) - 10: len(unparsed_skus)]

    if len(details) > 50:
        details_chuncks = details[len(details) - 50: len(details)]
    context = {'host': server_host,
               'tasks': accs,
               'details': details,
               'time_run': time_run,
               'count': len(details),
               'count_bd': len(Result_8.objects.all()),
               'unparsed_skus': unparsed_skus
               }
        # print(f'Task ID: {task.task_id}, Task state: {task.state}, Task status: {task.status}')
    return render(request, 'index.html', context=context)

def run(request, **kwargs):
    # Удаляем данные аккаунтов, если они есть
    r = redis.Redis(host='localhost', port=6379, db=0)

    # for key in r.scan_iter():
    #     key = key.decode('utf8')
    #     if 'acc_data_' in key:
    #         r.delete(key)
    # acc = accounts[random.randint(0, len(accounts) - 1)]
    server_host = 'https://' + str(get_current_site(request).domain) + f':{port}'
    # result = start.delay(acc['user'], acc['password'])
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.set('running', 'yes')
    r.set('perepars', 'yes')
    datenow = datetime.now()
    r.set('time_run', str(datenow))
    accounts = User.objects.all()

    # Собираем список неспаршенных артикулов и выдаём артикулы аккаунтам
    count_unparsed = len(Needs_8.objects.filter(status=1))
    if count_unparsed > 0:
        for unparsed in Needs_8.objects.filter(status=1):
            r.rpush('unparsed', unparsed.part_sought)
    r.set('count_unparsed', count_unparsed)

    chunck_size = count_unparsed / int(len(accounts))
    r.set('chunck_size', chunck_size)

    j = 0
    for acc in accounts.iterator():
        try:
            json_data = {
                'user': acc.username,
                'start_index': j
            }
            j = j + chunck_size
            json_data = json.dumps(json_data)
            r.set(acc.username+'_chuncks', json_data)
        except:
            pass
        # tasks_group_list.append(start.s(acc.username, acc.password, acc.proxy))
        # res = start.apply_async(args=(acc.username, acc.password, acc.proxy,), countdown=0)
        res = start.delay(acc.username, acc.password, acc.proxy)
        # res2 = result.AsyncResult(id=res.task_id)
        tasks.append(res)

    context = {'host': server_host, 'count_bd': len(Result_8.objects.all())}
    return render(request, 'index.html', context=context)

def stop(request, **kwargs):
    shutdown.delay()
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.flushdb()
    r.set('running', 'no')
    r.set('perepars', 'no')
    # identifier = str_to_class(obj)
    # obj = getattr(sys.modules[__name__], 'AutoApi')
    # obj.driver_quit(obj)
    # print(ctypes.cast(id(obj), ctypes.py_object).value)
    server_host = 'https://' + str(get_current_site(request).domain) + f':{port}'
    print(server_host)
    context = {'host': server_host, 'count_bd': len(Result_8.objects.all())}
    return render(request, 'index.html', context=context)
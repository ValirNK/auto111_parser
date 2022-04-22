import requests
from celery import Celery, shared_task
from celery.utils.log import get_task_logger
import os
import random
import time
from .settings import INSTALLED_APPS
# from .main import AutoApi, chuncked_list

parsed = []

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autodoc.settings')
BROKER_URL = 'redis://localhost:6379/0'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
# CELERY_SEND_TASK_SENT_EVENT = True
app = Celery('autodoc', broker=BROKER_URL, backend='redis')
# app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: INSTALLED_APPS)
# class MyTask(celery.Task):
#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         print('{0!r} failed: {1!r}'.format(task_id, exc))
logger = get_task_logger(__name__)

# @shared_task
# def start(login, password):
#     print('-------------')
#     logger.info('Adding {0} + {1}'.format(login, password))
#     print('-------------')
#     selected_indexes = []
#     for i in range(1, 5):
#         try:
#             index = random.randint(0, len(chuncked_list))
#             selected_indexes.append(index)
#         except IndexError:
#             continue
#     print('Выбрали следующие элементы из спика:' + str(selected_indexes))
#     print('------------------------------------------------------------------')
#     api = AutoApi(login, password)
#     auth = api.auth()
#     if not auth is False:
#         for index in selected_indexes:
#             ch = chuncked_list[index]
#             chuncked_list.remove(chuncked_list[index])
#             time.sleep(random.randint(1, 3))
#             for ind, sku in enumerate(ch):
#                 pos = api.search_details(sku)
#                 print(str(ind) + ' ---- ' + str(pos))
#                 # requests.post('http://127.0.0.1:8000/', data={'APIsuk' : '11', 'fgi' : '22'})
#                 # parsed.append(pos)
#                 # new = Detail(manufacture=pos['manufacture'], price=pos['price'], delivery=pos['delivery'],
#                 #              diler=pos['diler'])
#                 # new.save()
#             time.sleep(random.randint(600, 1200))
#
#             print('Отпарсили подмассив')
#         api.driver_quit()
#
# @shared_task(bind=True)
# def shutdown(self):
#     app.control.broadcast('shutdown', destination=[self.request.hostname])



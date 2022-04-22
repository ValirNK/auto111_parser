# from django.shortcuts import render
# from django.shortcuts import render
# from django.contrib.sites.shortcuts import get_current_site
# from .main import login, password
# from .celery import start, shutdown
# from celery import current_app
# from .main import accounts
#
# def index(request, **kwargs):
#     # async_result = start.delay(login, password)
#     current_app.loader.import_default_modules()
#     # Определяем зарегестрированные таски
#     tasks = list(sorted(name for name in current_app.tasks
#                         if not name.startswith('celery.')))
#     server_host = 'http://' + str(get_current_site(request).domain)
#     from .celery import parsed
#     print(parsed)
#     context={'host': server_host, 'details': parsed}
#     return render(request, 'index.html', context=context)
#
# def run(request, **kwargs):
#     for acc in accounts:
#         start.delay(acc['user'], acc['password'])
#     return render(request, 'index.html')
#
# def stop(request, **kwargs):
#     shutdown.delay()
#     return render(request, 'index.html')
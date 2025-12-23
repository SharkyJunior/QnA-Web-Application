import os

bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
workers = int(os.getenv('GUNICORN_WORKERS', 2))
threads = int(os.getenv('GUNICORN_THREADS', 2))
timeout = int(os.getenv('GUNICORN_TIMEOUT', 30))
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

wsgi_app = 'ask_sharkevich.wsgi.application'

worker_class = "sync"
worker_connections = 1000
keepalive = 2

reload = False

preload_app = True

max_requests = 1000
max_requests_jitter = 50
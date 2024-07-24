
# start redis
redis-server &

# start celery
celery -A celery_worker.celery worker --loglevel=info &

# start gunicorn
gunicorn --config gunicorn.conf.py app:app

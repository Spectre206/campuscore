import redis
from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    status_code = 200
    statuses = {
        'database': 'ok',
        'redis': 'ok',
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception as e:
        statuses['database'] = f'error: {str(e)}'
        status_code = 503

    # Check Redis
    try:
        redis_url = settings.CELERY_BROKER_URL
        r = redis.from_url(redis_url)
        r.ping()
    except Exception as e:
        statuses['redis'] = f'error: {str(e)}'
        status_code = 503

    return JsonResponse(
        {'ready': status_code == 200, 'services': statuses},
        status=status_code,
    )

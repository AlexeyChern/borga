from .models import Investor

from celery import shared_task

import time


@shared_task
def investor_task(investor_id):
    investor = Investor.objects.get(pk=investor_id)
    investor.processed = True
    investor.save()
    return investor.processed

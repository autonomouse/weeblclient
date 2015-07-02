from django.utils import timezone
from uuid import uuid4

def time_now():
    return timezone.now()

def generate_uuid():
    return str(uuid4())

import uuid
from .models import Order

def generate_unique_token():
    while True:
        token = str(uuid.uuid4())[:8]
        if not Order.objects.filter(token=token).exists():
            return token
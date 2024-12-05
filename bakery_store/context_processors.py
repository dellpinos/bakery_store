from datetime import datetime
from decouple import config # Environment Variables (.env) - Python Decouple

def current_year(request):
    return {
        'current_year': datetime.now().year
    }

def app_name(request):
    return {
        'app_name': config('APP_NAME', default='testApp')
    }

from django.conf import settings

URL = getattr(settings, 'WURFL_URL', 'localhost')

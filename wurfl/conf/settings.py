from django.conf import settings

URL = getattr(settings, 'WURFL_URL', 'localhost')
USE_CACHE = getattr(settings, 'WURFL_USE_CACHE', False)
CACHE_PREFIX = getattr(settings, 'WURFL_CACHE_PREFIX', 'wurfl_')
CACHE_TIMEOUT = getattr(settings, 'WURFL_CACHE_TIMEOUT', None)

UA_PREFIX_MATCHING = getattr(settings, 'WURFL_UA_PREFIX_MATCHING', False)
UA_PREFIX_MATCHING_MAX_DISTANCE = getattr(settings, 'WURFL_UA_PREFIX_MATCHING_MAX_DISTANCE', 20)
UA_PREFIX_MATCHING_LIMIT = getattr(settings, 'WURFL_UA_PREFIX_MATCHING_LIMIT', 10)
UA_GENERIC_FALLBACK = getattr(settings, 'WURFL_UA_GENERIC_FALLBACK', False)

USE_PATCH = getattr(settings, 'WURFL_USE_PATCH', False)

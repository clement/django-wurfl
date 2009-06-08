from django.db import models
from django.utils.simplejson.decoder import JSONDecoder
from wurfl.conf import settings
from wurfl.exceptions import NoMatch

from os.path import commonprefix
from md5 import new as md5


class Update(models.Model):
    version = models.CharField(max_length=255)
    url = models.URLField()
    update_date = models.DateTimeField(auto_now_add=True)
    time_for_update = models.IntegerField()
    nb_devices = models.IntegerField()
    errors = models.TextField()
    
class Device(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    user_agent = models.CharField(max_length=255, blank=True, db_index=True)
    fall_back = models.CharField(max_length=128, blank=True, db_index=True)
    actual_device_root = models.BooleanField()
    json_capabilities = models.TextField()
    
    @classmethod
    def get_from_id(cls, device_id):
        d = cls.objects.get(id=device_id)
        d._build_full_capabilities()
        return d
        
    @classmethod
    def get_from_user_agent(cls, user_agent):
        # try the cache
        if settings.USE_CACHE:
            from django.core.cache import cache
            cache_key = settings.CACHE_PREFIX + md5(user_agent).hexdigest()
            device = cache.get(cache_key)
            if device:
                return device
        
        # fallback to actual computation
        device = cls._match_user_agent(user_agent)    
        device._build_full_capabilities()
        
        # cache the result
        if settings.USE_CACHE:
            cache.set(cache_key, device)
        
        return device
        
    @classmethod
    def _match_user_agent(cls, user_agent):
        device = cls.objects.filter(user_agent=user_agent).order_by('-actual_device_root')[:1]

        if len(device):
            return device[0]
        else:
            if settings.UA_PREFIX_MATCHING:
                # Try more flexible matching
                ds_user_agent = user_agent.split('/')[0]
                devices = cls.objects.filter(user_agent__startswith=ds_user_agent)
                devices = devices.order_by('-actual_device_root')[:settings.UA_PREFIX_MATCHING_LIMIT]
                
                if len(devices):
                    best_match = 0
                    best_device = None
                    for device in devices:
                        match = len(commonprefix([user_agent,device.user_agent]))
                        if match > best_match:
                            best_match = match
                            best_device = device
                    return best_device
            
            if settings.UA_GENERIC_FALLBACK:
                # Try to match with generic properties
                # :TODO:
                raise NotImplemented

        raise NoMatch, "Can't find a match in currently installed WURFL table for user_agent `%s`" % user_agent

    def _build_full_capabilities(self):
        # Iteratively build capabilities list
        capabilities = [self.json_capabilities]
        parent = self
        while parent.id != 'generic':
            parent = self.__class__.objects.get(id=parent.fall_back)
            capabilities.append(parent.json_capabilities)

        # JSON decoder
        d = JSONDecoder()
        capabilities.reverse()
        def red_cap(x,y):
            x.update(y)
            return x
        self.capabilities = reduce(red_cap, [d.decode(c) for c in capabilities])



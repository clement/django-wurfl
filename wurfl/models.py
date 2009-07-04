from django.db import models
from django.utils.simplejson.decoder import JSONDecoder
from django.utils.simplejson.encoder import JSONEncoder
from wurfl.conf import settings
from wurfl.exceptions import NoMatch

from os.path import commonprefix
from md5 import new as md5


class Update(models.Model):
    UPDATE_TYPE_WURFL = 0
    UPDATE_TYPE_PATCH = 1
    UPDATE_TYPE_HYBRID = 2
    UPDATE_TYPE_CHOICES = {
        UPDATE_TYPE_WURFL: 'WURFL',
        UPDATE_TYPE_PATCH: 'Patch',
        UPDATE_TYPE_HYBRID: 'Hybrid',
    }

    update_type = models.IntegerField(choices=UPDATE_TYPE_CHOICES.items())
    version = models.CharField(max_length=255)
    url = models.URLField()
    update_date = models.DateTimeField(auto_now_add=True)
    time_for_update = models.IntegerField()
    nb_devices = models.IntegerField()
    nb_merges = models.IntegerField()
    errors = models.TextField()
    
    def no_errors(self):
        return self.errors == ''
    no_errors.boolean = True
    no_errors.short_description = 'Status'
    
    @property
    def summary(self):
        return '\n'.join([
            '- %s : %s' %(Update._meta.get_field(field).verbose_name, getattr(self,field))
            for field in ['time_for_update', 'nb_devices', 'nb_merges', 'errors']
            if getattr(self,field)
        ])

class Patch(models.Model):
    name = models.CharField(max_length=255)
    priority = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    patch = models.TextField()
    active = models.BooleanField()
    
class BaseDevice(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    user_agent = models.CharField(max_length=255, blank=True, db_index=True)
    fall_back = models.CharField(max_length=128, blank=True, db_index=True)
    actual_device_root = models.BooleanField()
    json_capabilities = models.TextField()
    
    class Meta:
        abstract = True
    
    def __getitem__(self, key):
        group = self.capabilities.get(key, None)
        if not group:
            return self.get_capability(key)
        else:
            return group

    def get_capability(self, name):
        """
        Get a capability from its name, without knowing the group
        it belongs too
        """
        group = {}
        for group in self.capabilities.values():
            if group.has_key(name):
                break
        return group.get(name)


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

    def merge_json_capabilities(self, merge):
        d = JSONDecoder()
        e = JSONEncoder()
        
        capabilities = d.decode(self.json_capabilities)
        capabilities_merge = d.decode(merge)
        
        for (group, props) in capabilities_merge.items():
            if capabilities.has_key(group):
                capabilities[group].update(props)
            else:
                capabilities[group] = props

        self.json_capabilities = e.encode(capabilities)

class StandardDevice(BaseDevice):
    pass

    
class HybridDevice(BaseDevice):
    pass


class PatchDevice(BaseDevice):
    pass

    
Device = settings.USE_PATCH and HybridDevice or StandardDevice

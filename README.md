How to use
----------

    from wurfl import Device
    device = Device.get_from_ua(ua, fallback=True)
    device = Device.get_from_id()
    
Views for updating, patching, testing

Settings reference
------------------

- `WURFL_USE_CACHE` : True to use django cache backend ... `False`
- `WURFL_CACHE_PREFIX` : prefix for key `wurfl_`
- `WURFL_CACHE_TIMEOUT` : timeout for cached values, None = timeout for project, 0 = infinite
- `WURFL_USE_PATCH` : ??
- `WURFL_URL` : the url to the XML wurfl file

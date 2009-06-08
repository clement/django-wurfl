from wurfl.models import Device
from wurfl.middleware import DeviceMiddleware

def device(view):
    """
    Modifies the `request` object, adding the detected
    WURFL device object in `request.device`
    """
    def _decorator(request, *args, **kwargs):
        if not hasattr(request, "device"):
            m = DeviceMiddleware()
            m.process_request(request)
        return view(request, *args, **kwargs)

    _decorator.__doc__ = view.__doc__
    _decorator.__name__ = view.__name__

    return _decorator

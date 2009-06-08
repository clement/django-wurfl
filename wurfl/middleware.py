from wurfl.models import Device
from wurfl.exceptions import NoMatch

class DeviceMiddleware(object):
    def process_request(self, request):
        """
        Detect the accessing device from the user agent
        and add it to the request
        """
        try:
            request.device = Device.get_from_user_agent(request.META.get('HTTP_USER_AGENT',''))
        except NoMatch:
            request.device = None

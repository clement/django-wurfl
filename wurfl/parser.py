from wurfl.conf import settings
from wurfl.models import Update, Device

from xml import sax
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.simplejson.decoder import JSONDecoder
from time import time


class _Handler(sax.ContentHandler):
    def __init__(self):
        # Parsing version flag
        self.parse_version = False
        # JSON encoder and decoder
        self.e = JSONEncoder()
        self.d = JSONDecoder()
        
    def startElement(self, name, attrs):
        if name == 'wurfl':
            self.start_time = time()
            self.stats = {'nb_devices':0, 'url':settings.URL, 'errors':0}
        elif name == 'ver':
            self.stats['version'] = ''
            self.parse_version = True
        elif name == 'device':
            self.device = {}
            self.device['id'] = attrs.get('id', '')
            self.device['user_agent'] = attrs.get('user_agent', '')
            self.device['fall_back'] = attrs.get('fall_back', '')
            self.device['actual_device_root'] = attrs.get('actual_device_root', False) and True
            # Prepare the capabilities
            self.capabilities = {}
        elif name == 'group':
            self.current_group = attrs.get('id','')
            self.capabilities[self.current_group] = {}
        elif name == 'capabilities':
            value = attrs.get('value', '')
            if value == 'true' or value == 'false':
                value = (value == 'true')
            if value.isdigit():
                value = int(value)
                
            self.capabilities[self.current_group][attrs.get('id','')] = value
        
    def endElement(self, name):
        if name == 'device':
            # Process the capabilities
            self.device['capabilities'] = self.e.encode(self.capabilities)
            
            # Save the device model
            Device.objects.create(**self.device)
            
            # Update the stats
            self.stats['nb_devices'] += 1
            
            print "Device with id : %s" % self.device['id']
        elif name == 'wurfl':
            # End of the update
            self.stats['time_for_update'] = time() - self.start_time
            Update.objects.create(**self.stats)
        elif name == 'ver':
            self.parse_version = False
            
        
    def characters(self, ch):
        if self.parse_version:
            self.stats['version'] += ch
        
def parse_wurfl(file_name):
    parser = sax.make_parser()
    handler = _Handler()
    parser.setContentHandler(handler)
    parser.parse(open(file_name))
    


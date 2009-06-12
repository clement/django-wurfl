from StringIO import StringIO
from wurfl.models import StandardDevice, PatchDevice, HybridDevice, Patch, Update
from wurfl.parser import parse_wurfl

from django.db import IntegrityError

def build_patch():
    # First, truncate the patch table
    # :TODO: rewrite if/when a objects.truncate() becomes available
    PatchDevice.objects.all().delete()
    
    # Get all active patches to apply in order
    patches = Patch.objects.filter(active=True).order_by('priority', 'created')
    
    for patch in patches:
        parse_wurfl(StringIO(patch.patch), device_class=PatchDevice, update_class=None, merge=True)
        
def build_hybrid():
    # We assume both standard and and patch tables have been constructed successfully
    # First truncate, the hybrid table
    HybridDevice.objects.all().delete()
    
    # Then insert all the standard devices
    for device in StandardDevice.objects.all():
        # Dirty hack
        HybridDevice.objects.create(**device.__dict__)
        
    # Now, process all records from the patched device,
    # if it doesn't exist in the hybrid yet, insert,
    # otherwise, merge
    for device in PatchDevice.objects.all():
        try:
            HybridDevice.objects.create(**device.__dict__)
        except IntegrityError:
            target_device = HybridDevice.objects.get(id=device.id)
            target_device.merge_json_capabilities(device.json_capabilities)
            target_device.save()
            

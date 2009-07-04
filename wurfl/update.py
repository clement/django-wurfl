from wurfl.models import PatchDevice, HybridDevice, StandardDevice, Patch, Update
from wurfl.parser import parse_wurfl
from wurfl.exceptions import ParseError

from django.db import IntegrityError

from time import time
from StringIO import StringIO


def hybrid():
    updates = []
    # First, truncate then build the patch table
    # :TODO: rewrite if/when a objects.truncate() becomes available
    PatchDevice.objects.all().delete()
    # Get all active patches to apply in order
    patches = Patch.objects.filter(active=True).order_by('priority', 'created')
    
    stats = {'errors':[]}
    for patch in patches:
        try:
            stats_patch = parse_wurfl(StringIO(patch.patch), device_class=PatchDevice, merge=True)
            for (key, val) in stats_patch.items():
                if key in stats:
                    stats[key] += stats_patch[key]
                else:
                    stats[key] = stats_patch[key]
        except Exception, err:
            stats['errors'].append('In patch `%s` : %s' % (patch.name,err,))
    
    # Save the patching stats
    updates.append(
        Update.objects.create(
            update_type=Update.UPDATE_TYPE_PATCH,
            nb_devices=stats.get('nb_devices',0),
            nb_merges=stats.get('nb_merges',0),
            errors='\n'.join(stats['errors']),
            url='',
            version='',
            time_for_update=stats.get('time_for_update',0),
        )
    )
    
    if stats.get('errors', False):
        # Bail out early
        return updates

    # Prepare stats for hybrid
    stats = {'nb_devices':0, 'nb_merges':0, 'time_for_update':time(), 'errors':[]}
    # We assume both standard and and patch tables have been constructed successfully
    # First truncate, the hybrid table
    HybridDevice.objects.all().delete()
    
    # Then insert all the standard devices
    for device in StandardDevice.objects.all():
        try:
            # Dirty hack
            HybridDevice.objects.create(**device.__dict__)
            stats['nb_devices'] += 1
        except Exception, err:
            stats['errors'].append(str(err))
        
    # Now, process all records from the patched device,
    # if it doesn't exist in the hybrid yet, insert,
    # otherwise, merge
    for device in PatchDevice.objects.all():
        try:
            try:
                HybridDevice.objects.create(**device.__dict__)
                stats['nb_devices'] += 1
            except IntegrityError:
                target_device = HybridDevice.objects.get(id=device.id)
                target_device.merge_json_capabilities(device.json_capabilities)
                target_device.save()
                stats['nb_merges'] += 1
        except Exception, err:
            stats['errors'].append(str(err))
        
    stats['time_for_update'] = time() - stats['time_for_update']
    stats['errors'] = '\n'.join(stats['errors'])
    # Save the hybrid stats
    updates.append(
        Update.objects.create(
            update_type=Update.UPDATE_TYPE_HYBRID,
            url='',
            version='',
            **stats
        )
    )
        
    return tuple(updates)

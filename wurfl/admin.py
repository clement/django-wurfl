from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect

from StringIO import StringIO
from time import time
from wurfl.models import StandardDevice, PatchDevice, HybridDevice, Update, Patch
from wurfl.parser import parse_wurfl

from django.db import IntegrityError


from django.shortcuts import render_to_response
from django.template import RequestContext


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('update_type', 'update_date', 'nb_devices', 'nb_merges', 'time_for_update', 'no_errors',)
    list_filter = ('update_date',)
    ordering = ('-update_date',)
    
    def update_hybrid_view(self, request):
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
        Update.objects.create(
            update_type=Update.UPDATE_TYPE_PATCH,
            nb_devices=stats.get('nb_devices',0),
            nb_merges=stats.get('nb_merges',0),
            errors='\n'.join(stats['errors']),
            url='',
            version='',
            time_for_update=stats.get('time_for_update',0),
        )
        
        if stats.get('errors', False):
            request.user.message_set.create(message=_('There was some errors when processing patches, please check the error report'))        
            return HttpResponseRedirect(request.path + "../")

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
        Update.objects.create(
            update_type=Update.UPDATE_TYPE_HYBRID,
            url='',
            version='',
            **stats
        )
            
        if stats.get('errors', False):
            request.user.message_set.create(message=_('There was some errors when computing the hybrid table, please check the error report'))        
            return HttpResponseRedirect(request.path + "../")
        else:
            request.user.message_set.create(message=_('Hybrid table build successfully'))        
            return HttpResponseRedirect(request.path + "../")
        
    def update_wurfl_view(self, request):
        request.user.message_set.create(message=_('WURFL build successfully'))        
        return HttpResponseRedirect(request.path + "../")
        
    def get_urls(self):
        urls = super(UpdateAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(.+)/hybrid/$', self.admin_site.admin_view(self.build_hybrid_view), name="admin_wurfl_update_hybrid"),
            url(r'^(.+)/wurfl/$', self.admin_site.admin_view(self.build_wurfl_view), name="admin_wurfl_update_wurfl"),
        )
        return my_urls + urls
    
class PatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'updated', 'created', 'active')
    list_filter = ('active', 'priority',)
    search_fields = ('name',)


# Register WURFL Admins
admin.site.register(Update, UpdateAdmin)
admin.site.register(Patch, PatchAdmin)


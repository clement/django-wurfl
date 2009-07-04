from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect

from django.shortcuts import render_to_response
from django.template import RequestContext

from wurfl import update
from wurfl.models import Update, Patch

import operator

class UpdateAdmin(admin.ModelAdmin):
    list_display = ('update_type', 'update_date', 'nb_devices', 'nb_merges', 'time_for_update', 'no_errors',)
    list_filter = ('update_date',)
    ordering = ('-update_date',)
    
    def update_hybrid_view(self, request):
        updates = update.hybrid()

        if any(map(operator.attrgetter('errors'), updates)):
            message = _('There was some errors when computing the hybrid table, please check the error report')
        else:
            message = _('Hybrid table build successfully')

        request.user.message_set.create(message=message)
        return HttpResponseRedirect(request.path + "../")
        
    def update_wurfl_view(self, request):
        request.user.message_set.create(message=_('WURFL build successfully'))        
        return HttpResponseRedirect(request.path + "../")
        
    #def change_view(self, request, object_id, extra_context=None):
    #    up = Update.objects.get(pk=object_id)
    #    return render_to_response('admin/wurfl/update/change_form.html',
    #        {'object':up,
    #         'opts':self.model._meta},context_instance=RequestContext(request))
    
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


from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response
from django.template import RequestContext

from wurfl.decorators import device
from wurfl.admin import UpdateAdmin
from wurfl.models import Update

@device
def test(request):
    return render_to_response('wurfl/test.html', {}, context_instance=RequestContext(request))
    
def update_hybrid(request):
    return UpdateAdmin(Update, admin.site).update_hybrid_view(request)
update_hybrid = user_passes_test(lambda user: user.is_superuser)(update_hybrid)
    
def update_wurfl(request):
    return UpdateAdmin(Update, admin.site).update_wurfl_view(request)
update_wurfl = user_passes_test(lambda user: user.is_superuser)(update_wurfl)

from django.shortcuts import render_to_response
from django.template import RequestContext
from wurfl.decorators import device

@device
def test(request):
    return render_to_response('wurfl/test.html', {}, context_instance=RequestContext(request))

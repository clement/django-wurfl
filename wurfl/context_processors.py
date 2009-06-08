def device(request):
    # No exception thrown here, as the user might activate
    # the detection on a per-view basis, but still use the
    # context processor at a global level
    return {'device': hasattr(request,'device') and request.device or None}

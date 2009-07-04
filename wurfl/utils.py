class FieldSubscript(object):
    """
    Dirty hack-class for allowing access to fields from
    a model inside a template (see admin/change_form)
    without having to go for the templatetags like it's
    done in the original admin site.
    
    The class is bound to a model, and define just
    the read [] operator, getting a field from the model
    _meta class based on its name
    """
    model = None
    
    def __init__(self, model):
        self.model = model
        
    def __getitem__(self, key):
        try:
            return self.model._meta.get_field(key)
        except:
            return None

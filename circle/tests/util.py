from rest_framework.reverse import reverse

def url(name, **kwargs):
    return "http://testserver" + reverse(name, kwargs=kwargs)

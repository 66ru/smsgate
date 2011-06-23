from django.http import HttpResponse

def user_passes_test_or_403(test_func):
    """
    Decorator for views that checks that the user passes the given test.

    Anonymous users will be redirected to login_url, while users that fail
    the test will be given a 403 error.
    """
    def _dec(view_func):
        def _checklogin(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                #resp = render_to_response('403.html', context_instance=RequestContext(request))
                resp = HttpResponse()
                resp.status_code = 403
                return resp
        _checklogin.__doc__ = view_func.__doc__
        _checklogin.__dict__ = view_func.__dict__
        return _checklogin
    return _dec

def permission_required_or_403(perm):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page or rendering a 403 as necessary.
    """
    return user_passes_test_or_403(lambda u: u.has_perm(perm))


def _ipv4_to_int(ip):
    """
    >>> f = _ipv4_to_int
    >>> f('0.0.0.0')
    0L
    >>> f('255.255.255.255')
    4294967295L
    """
    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
    return long(hexn, 16)


def ip_in_range(input_ip, ip_range_from, ip_range_to='255.255.255.255'):
    """
    >>> f = ip_in_range
    >>> f('127.0.0.1', '0.0.0.0', '255.255.255.255')
    True
    >>> f('127.0.0.1', '127.0.0.0', '255.255.255.255')
    True
    >>> f('127.0.0.1', '100.1.1.1', '255.255.255.255')
    True
    >>> f('127.0.0.1', '127.0.0.1')
    True
    >>> f('127.0.0.1', '127.0.0.0')
    True
    """
    return _ipv4_to_int(ip_range_from) <= _ipv4_to_int(input_ip) <= _ipv4_to_int(ip_range_to)
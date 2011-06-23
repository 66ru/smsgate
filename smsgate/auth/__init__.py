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

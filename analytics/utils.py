from functools import wraps


def count_visit(view_func):
    """
    Compatibility no-op.

    Visit tracking has been globally disabled, but existing imports and
    decorators stay in place so we do not have to touch every call site.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        return view_func(request, *args, **kwargs)

    return wrapper

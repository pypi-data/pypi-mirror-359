import hashlib
import logging
from functools import wraps

from django.core.cache import cache

logger = logging.getLogger(__name__)


def skip_raw(func):
    """
    For many pre_save/post_save signals, we want to skip actions when loading a
    raw value from a fixture. This allows us to more consistantly handle those cases.
    """

    @wraps(func)
    def _wrapper(*, raw=False, instance, **kwargs):
        if raw:
            logger.debug("Skipping %s:%s for raw %s", __name__, func.__name__, instance)
            return
        else:
            logger.debug("Running %s:%s for %s", __name__, func.__name__, instance)
            return func(raw=raw, instance=instance, **kwargs)

    return _wrapper


def cache_method(key=None, *, timeout=60):
    def outer(f):
        @wraps(f)
        def wrapper(view, *args, **kwds):
            prefix = key if key else f"{f.__module__}:{f.__qualname__}"

            # We start with our user for our buffer string
            buff = str(view.request.user)
            # Then add in each kwds to make it unique
            for k in kwds:
                buff += f"{k}:{kwds[k]}"

            hash = hashlib.sha1(buff.encode()).hexdigest()
            cache_key = f"{prefix}||{hash}"

            logger.debug("Using key %s for %s", cache_key, f)
            return cache.get_or_set(
                key=cache_key,
                default=lambda: f(view, *args, **kwds),
                timeout=timeout,
            )

        return wrapper

    return outer

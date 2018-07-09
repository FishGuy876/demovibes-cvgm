from django.core.cache import cache

import time

def atomic (key, timeout = 30, wait = 60):
    """
    Lock a function so it can not be run in parallell

    Key value identifies function to lock
    """

    lockkey = "lock-" + key
    def func1(func):
        def func2(*args, **kwargs):
            c = 0
            has_lock = cache.add(lockkey, 1, timeout)
            while not has_lock and c < wait * 10:
                c = c + 1
                time.sleep(0.1)
                has_lock = cache.add(lockkey, 1, timeout)
            if has_lock:
                try:
                    return func(*args, **kwargs)
                finally:
                    cache.delete(lockkey)
        return func2
    return func1


def cached_method (key, timeout = 60):
    """
        Cache computation result regardless of arguments.
    """

    def func1 (func):
        def func2 (*args, **kwargs):
            result = cache.get (key)

            if result == None:
                result = func (*args, **kwargs)
                cache.set (key, result, timeout)

            return result
        return func2
    return func1

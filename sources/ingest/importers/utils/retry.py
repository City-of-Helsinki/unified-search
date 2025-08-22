import time


def retry_twice_5s_intervals(callable, *args, **kwargs):
    """
    Retry given callable (e.g. function or class) with given arguments
    twice with 5s intervals (i.e. max. 3 tries = max. 2 retries)
    if it raises an exception, otherwise return first successful result.

    :return: The first successful result is returned
             (i.e. the value of `callable(*args, **kwargs)`),
             or the last exception is raised if all attempts fail.

    :param callable: The callable to be retried.
    :param args: Positional arguments to pass to the callable.
    :param kwargs: Keyword arguments to pass to the callable.
    """
    for nth_attempt in 1, 2, 3:
        try:
            return callable(*args, **kwargs)
        except Exception as e:
            if nth_attempt == 3:
                raise e
            time.sleep(5)  # Wait in seconds

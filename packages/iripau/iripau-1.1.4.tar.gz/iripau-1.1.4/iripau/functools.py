"""
Function utilities with similar philosophy as the :mod:`subprocess` module.
"""

import sys
import uuid
import operator

from functools import wraps
from inspect import getsource, isgeneratorfunction
from time import time, sleep

from typing import Callable, Union, Tuple, Type


def wait_for(
    condition: Callable, *args,
    _timeout: float = None,
    _outcome: bool = True,
    _poll_time: float = 10,
    _stop_condition: Callable[[], bool] = None,
    **kwargs
):
    """ Wait for ``condition(*args, **kwargs)`` to be ``_outcome``.

        Args:
            condition: Call this function many times with ``*args`` and
                ``**kwargs`` until its return value is ``_outcome``.
            *args: Pass these arguments to ``condition``.
            **kwargs: Pass these keyword arguments to ``condition``.
            _timeout: Max time in seconds to continue on calling ``condition``.
            _outcome: The desired outcome to gracefully stop waiting.
            _poll_time: Seconds in between ``condition`` calls.
            _stop_condition: Stop waiting if the result of calling this function
                is ``True``.

        Raises:
            TimeoutError: If timeout reached.
            InterruptedError: If ``_stop_condition()`` returns ``True``.

        Examples:
            Wait for a network interface to have an IP address::

                import netifaces


                def iface_is_connected(iface):
                    \"\"\" ``iface`` has an IP v4 address \"\"\"
                    return netifaces.AF_INET in netifaces.ifaddresses(iface)


                wait_for(iface_is_connected, "eth0", _timeout=10)

            Wait for a process to finish, but stop waiting if there is an error
            log::

                import psutil


                def log_file_contains_error():
                    \"\"\" The log informs the process has stalled \"\"\"
                    with open("/tmp/events.log") as f:
                        return "Error: Process stalled" in f.read()


                wait_for(
                    psutil.pid_exists, 12345,
                    _outcome=False,
                    _timeout=3600,
                    _poll_time=600,
                    _stop_condition=log_file_contains_error
                )

        Tip:
            Create ``condition`` and ``_stop_condition`` functions that read
            nicely when used in `if` statements, not in questions.
            For example, prefer ``host_is_reachable()`` instead of
            ``is_host_reachable()``.
    """
    last = time()
    end = _timeout and last + _timeout
    operation = operator.not_ if _outcome else operator.truth
    while operation(condition(*args, **kwargs)):
        if _stop_condition and _stop_condition():
            message = "No reason to keep waiting since the following condition was met:\n{0}"
            raise InterruptedError(message.format(getsource(_stop_condition)))
        now = time()
        if end and now > end:
            message = "The following condition was not {0} after {1} seconds: \n{2}"
            raise TimeoutError(
                message.format(_outcome, _timeout, getsource(condition))
            )
        sleep_time = max(0, _poll_time - (now - last))
        sleep(sleep_time)
        last = now + sleep_time


def retry(
    tries: int,
    exceptions: Union[Type[Exception], Tuple[Type[Exception]]] = Exception,
    retry_condition: Callable[[Type[Exception]], bool] = None,
    backoff_time: int = 0
):
    """ Add retry capabilities to the decorated function.

        Call the decorated function up to ``tries`` times, until it succeeds or
        it raises an unexpected exception.
        The decorated function Will only be retried if it raises one of the
        expected ``exceptions`` **and** ``retry_condition`` is fulfilled.
        Any other exception Will be raised immediately without further tries.

        Args:
            tries: The decorated function will be called at most this amount of
                times.
            exceptions: The expected exceptions to trigger the retry.
            retry_condition: Function to call with the caught exception to verify
                if the retry process should continue.
                If it returns ``False``, the caught exception will be raised.
            backoff_time: Seconds to wait before the next try..

        Example:
            Try to get the status of a server through a request to one of its
            REST API endpoints. Retry up to five times if Forbidden 403::

                import requests

                from urllib.parse import urljoin
                from requests.exceptions import HTTPError


                def http_code_is_forbidden(e):
                    \"\"\" The status code in the response is 403 \"\"\"
                    return 403 == e.response.status_code


                @retry(tries=5, exceptions=HTTPError, retry_condition=http_code_is_forbidden)
                def get_server_status(server, headers):
                    response = requests.get(urljoin(server, "api/status"), headers=headers)
                    response.raise_for_status()
                    return response.json()

        The decorated function can have two parts divided by one ``yield``.
        In that case the expected exceptions will only be caught in the second part::

            import requests


            @retry(tries=3, exceptions=(AssertionError, IndexError))
            def get_client_book(book_name):
                response = requests.get("https://localhost:8080/api/client/99/books")
                response.raise_for_status()
                data = response.json()

                yield

                last = data[-1]  # This might raise IndexError
                assert book_name == last["name"]  # This might raise AssertionError
                return last


            # Setting a book for a client
            response = requests.post("https://localhost/client/99/books", json={"name": "1984"})
            response.raise_for_status()

            # The book should be the last enrty of the books endpoint
            book = get_client_book("1984")
    """
    def decorator(function):

        @wraps(function)
        def helper(*args, **kwargs):
            yield
            return function(*args, **kwargs)

        f = function if isgeneratorfunction(function) else helper

        @wraps(function)
        def wrapper(*args, **kwargs):
            t = tries
            while t > 0:
                gen = f(*args, **kwargs)
                next(gen)
                try:
                    next(gen)
                except StopIteration as e:
                    return e.value
                except exceptions as e:
                    if retry_condition is None or retry_condition(e):
                        if t == 1:
                            raise
                        t = t - 1
                        sleep(backoff_time)
                    else:
                        raise
        return wrapper
    return decorator


def globalize(function: Callable) -> Callable:
    """
        Make ``function`` globally available in the module it was defined so it
        can be serialized. Useful when calling local functions with
        :mod:`multiprocessing`.

        Args:
            function: Function to decorate
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    wrapper.__name__ = wrapper.__qualname__ = uuid.uuid4().hex
    setattr(sys.modules[function.__module__], wrapper.__name__, wrapper)
    return wrapper

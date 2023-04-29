import datetime as dt
import functools
import logging
import time


def for_all_methods(excluded, decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr not in excluded:
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def timer(func, logger):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.time()
        value = func(*args, **kwargs)
        end_time = time.time()
        run_time = round(start_time, end_time)
        logger.debug("Finished in {}".format(run_time), extra={"name_override": func.__name__})
        return value

    return wrapper_timer


def debuglog(logger=None):
    # type: (object) -> object
    """Print the executing status of the decorated function
    @rtype: object
    """

    def log_inner(func):
        @functools.wraps(func)
        def wrapper_log(*args, **kwargs):
            log = None
            try:
                if logger is None:
                    for kw in kwargs.values():
                        if isinstance(kw, logging.Logger):
                            log = kw
                        elif isinstance(kw, object) and hasattr(kw, "logger"):
                            log = kw.logger
                    if log is None:
                        for arg in args:
                            if isinstance(arg, logging.Logger):
                                log = arg
                            elif isinstance(arg, object) and hasattr(arg, "logger"):
                                log = arg.logger
                else:
                    log = logger
            except Exception as exc:
                print(exc)
            start_time = time.time()
            log.debug("Executing... ", extra={"name_override": func.__name__})
            value = func(*args, **kwargs)
            if value:
                log.debug("Finishing...", extra={"name_override": func.__name__})
            else:
                log.debug("Finished.", extra={"name_override": func.__name__})
            tt = round(time.time() - start_time, 2)
            total_time = "Elapsed time: {}".format(dt.timedelta(seconds=tt)).split(".")[0]
            log.debug(total_time, extra={"name_override": func.__name__})
            return value

        return wrapper_log

    return log_inner


def retry_requests(retry=3, sleep_time=0.5, logger=None):
    def retry_inner(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            log = None
            try:
                stream = False
                if logger is None:
                    for kw in kwargs.values():
                        if isinstance(kw, logging.Logger):
                            log = kw
                        elif isinstance(kw, object) and hasattr(kw, "logger"):
                            log = kw.logger
                    for arg in args:
                        if isinstance(arg, logging.Logger):
                            log = arg
                        elif isinstance(arg, object) and hasattr(arg, "logger"):
                            log = arg.logger
                        elif isinstance(arg, dict):
                            if "stream" in arg:
                                stream = arg.get("stream")
                else:
                    log = logger
            except Exception as exc:
                print(exc)
            count = 0
            while count < retry:
                response = func(*args, **kwargs)
                if response[0].ok:
                    return response
                count += 1
                if count < retry:
                    if log:
                        log.debug(
                            "Retry: {}: Retrying in {} sec..".format(count, sleep_time),
                            extra={"name_override": func.__name__},
                        )
                    else:
                        print("{} Retrying in {} sec..".format(str(response), sleep_time))
                    time.sleep(sleep_time)
            if not stream:
                if log:
                    log.debug(msg=response[0].text)
                else:
                    print(response[0].text)
            return response

        return wrapper_retry

    return retry_inner

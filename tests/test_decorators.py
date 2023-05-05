import time

import requests

from ..utils.decorators import debuglog, retry_requests
from ..utils.loggering import LoggerGeneric


# @pytest.mark.skip
def test_retry_request_decorator_function_logger_from_function_400(global_config):
    logger, config_file, session, client, url = global_config

    def to_decorate(logger=None):
        response = requests.Response()
        response.status_code = 400
        return response

    initial = time.time()
    result = retry_requests(retry=3, sleep_time=0.5)(to_decorate)(logger)
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 400
    assert timer >= 1


# @pytest.mark.skip
def test_retry_request_decorator_function_logger_from_parameter_401(global_config):
    logger, config_file, session, client, url = global_config

    def to_decorate(logger=None):
        response = requests.Response()
        response.status_code = 401
        return response

    initial = time.time()
    result = result = retry_requests(retry=3, sleep_time=0.5, logger=logger)(to_decorate)()
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 401
    assert timer >= 1


# @pytest.mark.skip
def test_retry_request_decorator_class_logger_from_class_402(global_config):
    logger, config_file, session, client, url = global_config

    class Deco:
        def __init__(self, logger):
            self.logger = logger

        @retry_requests(retry=3, sleep_time=0.5)
        def to_decorate(self):
            response = requests.Response()
            response.status_code = 402
            return response

    initial = time.time()
    deco = Deco(logger=logger)
    result = deco.to_decorate()
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 402
    assert timer >= 1


# @pytest.mark.skip
def test_log_decorator_function_logger_from_function_403(global_config):
    logger, config_file, session, client, url = global_config

    def to_decorate(logger=None):
        response = requests.Response()
        response.status_code = 403
        return response

    initial = time.time()
    result = debuglog()(to_decorate)(logger)
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 403


# @pytest.mark.skip
def test_log_decorator_function_logger_from_parameter_404(global_config):
    logger, config_file, session, client, url = global_config

    def to_decorate(logger=None):
        response = requests.Response()
        response.status_code = 404
        return response

    initial = time.time()
    result = result = debuglog(logger=logger)(to_decorate)()
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 404


# @pytest.mark.skip
def test_log_decorator_class_logger_from_class_405():
    BASIC_FORMAT = "%(name)s:%(levelname)s:%(message)s"
    loggerps = LoggerGeneric(
        name="TESTS", formatter=BASIC_FORMAT, log_level="DEBUG", file_name="test_debug.log"
    )
    loggertest = loggerps.get_logger()

    class Deco:
        def __init__(self, logger=None):
            self.logger = logger

        @debuglog()
        def to_decorate(self):
            response = requests.Response()
            response.status_code = 405
            return response

    initial = time.time()
    deco = Deco(logger=loggertest)
    result = deco.to_decorate()
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 405


# @pytest.mark.skip
def test_log_decorator_class_logger_from_parameter_406(global_config):
    logger, config_file, session, client, url = global_config

    class Deco:
        def __init__(self, logger=None):
            self.logger = logger

        @debuglog()
        def to_decorate(self):
            response = requests.Response()
            response.status_code = 406
            return response

    initial = time.time()
    deco = Deco(logger=logger)
    result = deco.to_decorate()
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 406


# @pytest.mark.skip
def test_log_decorator_class_logger_from_parameter_407(global_config):
    logger, config_file, session, client, url = global_config

    @debuglog()
    def to_decorate(
        retries=5, backoff_factor=2, status_forcelist=(500, 502, 503, 504), logger=None
    ):
        response = requests.Response()
        response.status_code = 407
        return response

    def caller():
        return to_decorate(logger)

    initial = time.time()
    # deco = Deco(logger=logger)
    result = caller()
    final = time.time()
    timer = int(final - initial)
    assert result.status_code == 407

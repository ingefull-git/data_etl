import requests
from base import RequestRetryGeneric
from decorators import debuglog, for_all_methods, retry_requests
from requests.adapters import HTTPAdapter, Retry


@debuglog()
def session_retry(retries=5, backoff_factor=2, status_forcelist=(500, 502, 503, 504), logger=None):
    """
    Creates a Session instance

    :param retries: The number of times to retry the request, defaults to 5 (optional)
    :param backoff_factor: The backoff factor to apply between attempts after the second try (most errors are resolved
    immediately by a second try without a delay). urllib3 will sleep for: {backoff factor} * (2 ^ ({number of total retries}
    - 1)) seconds. If the backoff_, defaults to 2 (optional)
    :param status_forcelist: A set of integer HTTP status codes that we should force a retry on
    :param logger: The logger to use. If None, print
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


@for_all_methods(["__init__"], debuglog())
# > T
class RequestRetryPowerSchool(RequestRetryGeneric):
    """
    his class is a subclass of the generic `RequestRetryGeneric` class, and it is used to make requests to the
    PowerSchool API
    """

    @retry_requests(retry=2, sleep_time=1)
    def make_request(self, *args, **kwargs):
        """
        It makes a request to the server.
        """
        return super(RequestRetryPowerSchool, self).make_request(*args, **kwargs)

    def check_response(self, *args, **kwargs):
        """
        It checks the response of the function.
        """
        response = kwargs.get("response")
        request = kwargs.get("request")
        stream = request.get("stream", "")
        try:
            if response.ok:
                if stream:
                    return True
                if "count" in response.content:
                    return True
                elif "access_token" in response.content:
                    return True
                elif "record" in response.content:
                    return True
                elif "message" in response.content:
                    response.status_code = 403
                    return False
                else:
                    response.status_code = 403
                    return False
            else:
                return False
        except Exception as exc:
            print(exc)
            return False

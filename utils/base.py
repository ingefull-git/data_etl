import json
import logging
import time
from abc import ABCMeta, abstractmethod

import requests


class GenericMeta():
    """
    It's a metaclass that allows you to define a class with a generic type
    """
    __metaclass__ = ABCMeta
 

class LoggerGeneric(GenericMeta):
    """
    `LoggerGeneric` is a metaclass that creates a class that logs all attribute accesses to a file

    :param log_level: The level of logging you want to see, defaults to INFO (optional)
    :param formatter: This is the format of the log message
    :param name: The name of the logger
    :param file_name: The name of the file to be used for logging
    """
    def __init__(self, log_level='INFO', formatter=None, name=__name__, file_name=None):
        self.log_level = log_level if log_level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') else 'INFO'
        self.format= formatter
        self.name = name
        self.file = file_name
        self.logger = None


    def get_logger(self, file_level=None):
        """
        This function returns a logger object that can be used to log messages to a file and/or the console

        :param file_level: The level of logging to be written to the log file
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.log_level))
        logger.addHandler(self.stream_handler())
        if self.file and file_level:
            logger.addHandler(self.file_handler(log_level=file_level))
        self.logger = logger
        return logger


    @abstractmethod
    def formatter(self):
        """
        A function that takes in a string and returns a string with the first letter capitalized.
        """
        raise NotImplementedError


    @abstractmethod
    def stream_handler(self):
        """
        A function that is called when a new stream is created.
        """
        raise NotImplementedError


    @abstractmethod
    def file_handler(self, log_level=None):
        """
        A function that takes two arguments, self and log_level.

        :param log_level: The log level to use for the handler
        """
        raise NotImplementedError


    @abstractmethod
    def memory_handler(self, capacity=None, flush_level=None, target=None):
        raise NotImplementedError


    @abstractmethod
    def flush_memory(self, handler=None):
        raise NotImplementedError


class ClientGeneric(GenericMeta):
    """
    It takes a dictionary and returns a class with the dictionary's keys as attributes

    :param config_file: {}
    """
    def __init__(self, config_file):
        self.config_file = config_file
        self.configuration = self.get_file()
        for k, v in self.configuration.items():
            setattr(self, k, v)


    def get(cls, key, default=None):
        """
        `get` returns the value of the key in the dictionary, or the default value if the key is not found

        :param cls: The class that the method is being called on
        :param key: The key to get the value for
        :param default: The default value to return if the key is not found
        """
        if hasattr(cls, key):
            return getattr(cls, key)
        else:
            return default


    def get_file(self):
        """
        It returns the file name of the file that is being read.
        """
        with open(self.config_file, 'r') as f:
            return json.load(f)


    def get_or_create(cls, key, value=None):
        """
        "If the object with the given key exists, return it, otherwise create it."

        The function takes a class, a key, and an optional value. If the value is not given, it is assumed to be the same as
        the key

        :param cls: The class of the object you want to get or create
        :param key: The key to use to look up the object
        :param value: The value to set the key to if it doesn't exist
        """
        if hasattr(cls, key):
            return getattr(cls, key)
        else:
            setattr(cls, key, value)
            return getattr(cls, key), True


    def __str__(cls):
        """
        It returns a string representation of the class.

        :param cls: The class object that is being defined
        """
        return '{} instance with attributes: {}'.format(cls.__class__.__name__, [k for k, v in cls.__dict__.items()])


class RequestRetryGeneric(GenericMeta):
    """
    This class is a wrapper for the requests library that allows for retries and logging
    This class is a generic class that can be used to retry any function that returns a response object
    """
    def __init__(self, session=requests.Session(), method=None, hostname=None, headers=None, retry_params=None, stream=False, timeout=600.0, logger=LoggerGeneric):
        self.method = method
        self.hostname = hostname
        self.headers = headers
        self.logger = logger
        self.session = session
        self.retry_params = retry_params
        self.stream = stream
        self.timeout = timeout


    def make_request(self, *args, **kwargs):
        """
        It makes a request to the server.
        """
        t0 = time.time()
        context = args[0]
        try:
            resp = self.session.request(
                method = context.get('method', self.method),
                url = '{}{}'.format(self.hostname, context.get('url', "")) if 'http' not in context.get('url') else context.get('url'),
                headers = context.get('headers', self.headers),
                params = context.get('params', None),
                json = context.get('payload', None),
                stream = context.get('stream', self.stream),
                timeout = context.get('timeout', self.timeout)
                )
            if self.check_response(response=resp, request=context):
                self.log_response(context=context, response=resp, timer=t0)
            resp.raise_for_status()
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as err:
            self.logger.info('Request exception: {}.'.format(err))
            resp = requests.Response()
            resp._content = bytes({'error': err})
            resp.status_code = 408
        except requests.exceptions.HTTPError as err:
            self.log_exception(exception=err)
            resp._content = bytes({'error': err})
            context.update(self.retry_params)
        except requests.exceptions.RequestException as err:
            self.log_exception(exception=err)
            resp._content = bytes({'error': err})
        return resp, context


    def log_response(self, *args, **kwargs):
        """
        It logs the response of the request
        """
        context = kwargs.get('context', "")
        response = kwargs.get('response')
        timer = kwargs.get('timer')
        self.logger.debug('Request for {} with params {} executed with code {}.'.format('{}'.format(self.hostname + context.get('url', "") if 'http' not in context.get('url') else context.get('url')), context.get('params'), response.status_code))


    def log_exception(self, *args, **kwargs):
        """
        It logs the exception.
        """
        exception_msg = kwargs.get('exception')
        self.logger.debug('Request exception: {}.'.format(exception_msg))

    @abstractmethod
    def check_response(self, *args, **kwargs):
        """
        It checks the response of the function.
        """
        raise NotImplementedError


class QueriesGeneric(GenericMeta):
    """
    This class is a metaclass that allows you to create a class that inherits from `QueriesGeneric` and then use that
    class to create a class that inherits from `Queries` and `QueriesGeneric` and that has a `__dict__` that is a `dict` of
    `Query` objects
    """
    def __init__(self, request=RequestRetryGeneric, entities=None, preadapter=None, postadapter=None, logger=LoggerGeneric):
        self.request = request
        self.entities = entities
        self.preadapter = preadapter
        self.postadapter = postadapter
        self.logger = logger
        self.context = self.get_context_data()


    def get_context_data(self, **kwargs):
        """
        It returns a dictionary of the context data.
        """
        return kwargs


    @abstractmethod
    def prepare_query(self, *args, **kwargs):
        """
        This function takes in a query and returns a query that is ready to be executed
        """
        raise NotImplementedError


    @abstractmethod
    def request_query(self, *args, **kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        raise NotImplementedError

    @abstractmethod
    def check_response_query(self, *args, **kwargs):
        """
        It checks the response of the query.
        """
        raise NotImplementedError


    @abstractmethod
    def process_query(self, *args, **kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        raise NotImplementedError

        
    @abstractmethod
    def make_query(self, *args, **kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        raise NotImplementedError


class AdapterGeneric(GenericMeta):
    """
    It's a metaclass that
    takes a class and returns a new class that has the same name and bases
    as the original class, but with a new method called `__call__` that
    takes a single argument and returns an instance of the original class
    with that argument as its first argument
    """
    def __init__(self, query=QueriesGeneric, client=ClientGeneric, logger=LoggerGeneric):
        self.query= query
        self.logger = logger
        self.client = client
        self.context = self.get_context_data()


    def get_context_data(self, **kwargs):
        """
        It returns a dictionary of the context data.
        """
        return kwargs


class PullGeneric(GenericMeta):
    """
    The PullGeneric class is a generic class that can be used to pull data from a database
    """
    def __init__(self, adapter=AdapterGeneric(), logger=LoggerGeneric):    
        self.adapter = adapter
        self.query = adapter.query
        self.logger = logger or adapter.logger
        self.context = self.get_context_data()


    def get_context_data(self, **kwargs):
        """
        It returns a dictionary of the context data.
        """
        return kwargs
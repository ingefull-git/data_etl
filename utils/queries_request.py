import time
from functools import partial
from itertools import chain, imap

from base import QueriesGeneric
from decorators import debuglog, for_all_methods


@for_all_methods(["__init__"], debuglog())
class QueriesPowerSchool(QueriesGeneric):
    """
    This class is a subclass of the generic class, and it overrides the `get_context_data` and `prepare_query` methods
    """

    def prepare_query(self, *args, **kwargs):
        """
        This function takes in a query and returns a query that is ready to be executed
        """
        context = kwargs.get("context", "")
        prepare = map(partial(self.preadapter, context=context), self.entities)
        return chain.from_iterable(prepare)

    def check_response_query(self, *args, **kwargs):
        """
        It checks the response of the query.
        """
        response, request = kwargs.get("response")
        return True if response.ok else False

    def request_query(self, *args, **kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        prepare = kwargs.get("prepare")
        responses = imap(self.request.make_request, prepare)
        for response in responses:
            if self.check_response_query(response=response):
                result = self.process_query(response=response)
            else:
                result = response[0].text
        return result

    def process_query(self, *args, **kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        response = kwargs.get("response")
        process = self.postadapter(response=response)
        return process

    def make_query(self, *args, **kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        t0 = time.time()
        prepare = self.prepare_query(context=kwargs)
        result = self.request_query(prepare=prepare)
        return result

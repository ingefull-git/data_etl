import json

import requests


class MockFactory:
    """
    It is a class that is used to mock the requests.get() function.
    """
    def __init__(self, stream=False, **kwargs):
        self.response = requests.Response()
        self.counter = 0
        self.stream = stream
        self.status = kwargs["status"]

    def increment(self):
        """
        It increments the value of the attribute `self.value` by 1
        """
        self.counter += 1
    
    def side_effects(self,*args,**kwargs):
        """
        A function that takes in a variable number of arguments and keyword arguments.
        """
        self.increment()
        self.response.raw = self.response.content
        for count,tup in enumerate(self.status,start=1):
            if count == self.counter:
                if isinstance(tup[0],int):
                    status = tup[0]
                else:
                    exception_code = tup[0]
                    raise exception_code("This is an exception: {}".format(str(exception_code)))
                content = tup[1]
                self.response.status_code = status
                content = json.dumps(content)
                self.response._content = bytes(content)
        if self.stream:
            self.response.raise_for_status()
            return self.response.status_code
        else:
            return self.response
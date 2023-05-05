from encodings import utf_8
import json
import requests

class MockFactory:
    def __init__(self, stream=False, **kwargs):
        self.response = requests.Response()
        self.counter = 0
        self.stream = stream
        self.status = kwargs["status"]
        


        

    def increment(self):
        self.counter += 1
    
    def side_effects(self,*args,**kwargs):
        self.increment()
        self.response.raw = self.response.content

        for count,tup in enumerate(self.status,start=1):
            if count == self.counter:
                if isinstance(tup[0],int):
                    status = tup[0]
                #elif isinstance(tup[0],requests.exceptions.ReadTimeout):
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
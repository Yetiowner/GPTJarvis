from typing import Union, Optional

class API():
    def __init__(self, link: str, querynames: list = [], querydescriptors: dict = {}, datatransform: Optional[function] = None):
        self.link = link
        self.querynames = querynames
        self.querydescriptors = querydescriptors
        self.datatransform = datatransform
    
    def showApiLink(self, number):
        showstr = f"""API {number}:
        {self.link.format(*self.querynames)}, where """
        return showstr

class ChatBot():
    def __init__(self, apis: list = []):
        self.apis = apis
    
    def query(self, text):
        pass

def loadApiKeyFromFile(file):
    global apikey
    with open(file, "r") as f:
        apikey = f.read()
        
apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish
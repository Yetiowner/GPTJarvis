from typing import Union, Optional, Callable

class API():
    def __init__(self, link: str, querynames: list = [], querydescriptors: dict = {}, queryform: dict = {}, datatransform: Optional[Callable] = None):
        self.link = link
        self.querynames = querynames
        self.querydescriptors = querydescriptors
        self.queryform = queryform
        self.datatransform = datatransform

        for form in self.queryform:
            if type(self.queryform[form]) == type:
                self.queryform[form] = self.queryform[form].__name__

    
    def showApiLink(self, number):
        queriesinfo = ", and ".join([f"{{{self.querynames[index]}}} is replaced with {self.querydescriptors[self.querynames[index]] if self.querynames[index] in self.querydescriptors.keys() else 'the query'} I give you{' and is of the form ' + (self.queryform[self.querynames[index]]) if self.querynames[index] in self.queryform.keys() else ''}" for index in range(len(self.querynames))])
        showstr = f"""API {number}:
        {self.link.format(*["{" + i + "}" for i in self.querynames])}, where {queriesinfo}"""
        return showstr

class ChatBot():
    def __init__(self, apis: list[API] = []):
        self.apis = apis
    
    def query(self, text):
        pass

    def generateSetupText(self):
        text = "I will give you a series of API link formats, and whenever I ask you a question relating to a specific subject, reply with the api format filled in the the query I will give you. Pick the API most suited to the question type. If the question is suitable for none of the APIs, don't reply with a link, instead reply with your own knowledge base. Do not say whether an API link is suitable for the question, just reply with your own knowledge.\n\n"
        for index, api in enumerate(self.apis):
            text += api.showApiLink(index+1)+"\n\n"
        
        return text




def loadApiKeyFromFile(file):
    global apikey
    with open(file, "r") as f:
        apikey = f.read()
        
apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish
APIexample = API("https://stackoverflow.com/questions/{}/{}", ["questionnum", "questionname"], {"questionnum": "The number of the question", "questionname": "The name of the question"}, {"questionnum": int, "questionname": str})
chatbot = ChatBot([APIexample])
print(chatbot.generateSetupText())
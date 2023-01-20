from typing import Union, Optional, Callable, List
import types
import openai
import requests
import extracttxt
import re

class API():
    def __init__(self, link: str, querynames: list = [], querydescriptors: dict = {}, queryform: dict = {}, datacleaning: Optional[Callable] = extracttxt.scrapeText):
        self.link = link
        self.querynames = querynames
        self.querydescriptors = querydescriptors
        self.queryform = queryform
        self.datacleaning = datacleaning
        self.number = 0

        for form in self.queryform:
            if type(self.queryform[form]) == type:
                self.queryform[form] = self.queryform[form].__name__

    
    def showApiLink(self):
        queriesinfo = ", and ".join([f"{{{self.querynames[index]}}} is replaced with {self.querydescriptors[self.querynames[index]] if self.querynames[index] in self.querydescriptors.keys() else 'the query'} I give you{' and is of the form ' + (self.queryform[self.querynames[index]]) if self.querynames[index] in self.queryform.keys() else ''}" for index in range(len(self.querynames))])
        showstr = f"""API {self.number}:
        {self.link.format(*["{" + i + "}" for i in self.querynames])}, where {queriesinfo}"""
        return showstr
    
    def __repr__(self):
        return f"API {self.number}: {self.link}"

class ChatBot():
    def __init__(self, apis: List[API] = []):
        self.apis = apis
    
    def query(self, text):
        textToQuery = self.generateSetupText() + text
        openai.api_key = apikey
        
        response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=textToQuery,
        temperature=0.2,
        max_tokens=1024,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )

        response = response["choices"][0]["text"].lstrip()
        link = re.findall('https?://[^\s]+', response)[0]

        #print(link)

        apinumber = self.getApiNumberFromString(response[response.index(link)+len(link):])
        api = self.getAPIFromNumber(apinumber)
        
        try:
            data = self.getDataFromLink(link, api)
        except Exception as e:
            print(apinumber)
            print(response)
            print(link)
            raise e
        
        textToAnalyse = self.generateAnalysisText(data) + "\n\n" + text

        newresponse = openai.Completion.create(
        engine="text-davinci-003",
        prompt=textToAnalyse,
        temperature=0.5,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )

        newresponse = newresponse["choices"][0]["text"].lstrip()
        return newresponse

    
    def getDataFromLink(self, link, api: API):
        content = requests.get(link).content
        if type(api.datacleaning) == types.FunctionType:
            content = api.datacleaning(content)
        
        return content


    def getAPIFromNumber(self, number):
        for api in self.apis:
            if api.number == number:
                return api

    def getApiNumberFromString(self, string: str):
        out = ""
        for i in string:
            if i == ")":
                break
            elif i.isnumeric():
                out += i
        return int(out)

    def generateAnalysisText(self, data):
        return data

    def generateSetupText(self):
        text = "I will give you a series of API link formats, and whenever \
I ask you a question relating to a specific subject, reply with \
the api format filled in the the query I will give you. Pick the \
API most suited to the question type. If the question is suitable \
for none of the APIs, don't reply with a link, instead reply with \
your own knowledge base. Do not say whether an API link is suitable \
for the question, just reply with your own knowledge. If you do use an \
API, underneath the link please say the number of the API you used \
in brackets. The first thing you say should be the link, and only the link \
and api name\n\n"
        for index, api in enumerate(self.apis):
            api.number = index + 1
            text += api.showApiLink()+"\n\n"
        
        return text




def loadApiKeyFromFile(file):
    global apikey
    with open(file, "r") as f:
        apikey = f.read()
        
apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish
APIStackOverFlow = API("https://stackoverflow.com/questions/{}/{}", ["questionnum", "questionname"], {"questionnum": "The number of the question", "questionname": "The name of the question"}, {"questionnum": int, "questionname": str})
APIBrilliant = API("https://brilliant.org/wiki/{}", ["subject"])
APIQuora = API("https://www.quora.com/search?q={}", ["user"])
APIWikipedia = API("https://en.wikipedia.org/wiki/{}", ["searchterm"])
chatbot = ChatBot([APIStackOverFlow, APIBrilliant, APIQuora, APIWikipedia])
print(chatbot.query("Quote what is said about Tony the Pony on question 1732348 on SO? Start from 'You can't parse [X]...', and translate it into french."))
#print(chatbot.query("What is backpropogation? Get answers from billiant."))
#print(chatbot.query("Give me the etymology of water using wikipedia"))
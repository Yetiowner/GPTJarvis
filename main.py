import os
from typing import Union, Optional, Callable, List
import types
import openai
import requests
import extracttxt
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
from bs4 import BeautifulSoup
from openai.embeddings_utils import cosine_similarity
import pandas as pd
import numpy as np
import json
from test import explode, build
import inspect

with open("usage.log", "a") as file:
    file.write("--------------------\n")


options = FirefoxOptions()
options.add_argument("--headless")
options.preferences["permissions.default.geo"] = 1
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
browser = webdriver.Firefox(options=options)

with open("keys.json", "r") as file:
    APIKEYS = json.load(file)

MODEL = "text-davinci-003"
JARVIS = "\nYou are Jarvis from Iron Man, so answer like him. Call me Sir. If I ask a question I should know the answer to, \
be slightly sarcastic in your response."

class API():
    def __init__(self, link: str, querynames: list = [], querydescriptors: dict = {}, queryform: dict = {}, description: Optional[str] = None, datacleaning: Optional[Callable] = extracttxt.scrapeText, accessDelay = 0):
        self.link = link
        self.querynames = querynames
        self.querydescriptors = querydescriptors
        self.queryform = queryform
        self.description = description
        self.datacleaning = datacleaning
        self.number = 0
        self.accessDelay = accessDelay

        for form in self.queryform:
            if type(self.queryform[form]) == type:
                self.queryform[form] = self.queryform[form].__name__

    
    def showApiLink(self):
        queriesinfo = ", and ".join([f"{{{self.querynames[index]}}} is replaced with {self.querydescriptors[self.querynames[index]] if self.querynames[index] in self.querydescriptors.keys() else 'the query'} I give you{' and is of the form ' + (self.queryform[self.querynames[index]]) if self.querynames[index] in self.queryform.keys() else ''}" for index in range(len(self.querynames))])
        if self.description != None:
            queriesinfo += f". Description: {self.description}"
        showstr = f"""{self.link.format(*["{" + i + "}" for i in self.querynames])}, where {queriesinfo}"""
        return showstr
    
    def __repr__(self):
        return f"API {self.number}: {self.link}"

class Function():
    def __init__(self, function, args=[], kwargs={}, typeannots={}, description=None):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.typeannots = typeannots
        self.description = description
        self.number = 0
    
    def showFunction(self):
        return f"{self.function.__name__}({', '.join(self.args)}){' Where ' + str(self.typeannots) if self.typeannots else ''}{' Description: ' + self.description if self.description else ''}"
    
    def __repr__(self):
        return f"Func {self.number}: {self.function.__name__}"

class ChatBot():
    def __init__(self, apis: List[API] = [], functions: List[Function] = []):
        self.apis = apis
        self.functions = functions
        for index, api in enumerate(self.apis):
            api.number = index + 1
        for index, function in enumerate(self.functions):
            function.number = index + 1
        self.info = self.genInfoText()
    
    def genInfoText(self):
        out = ""
        with open("aditionalInfo.txt", "r") as file:
            out += file.read() + "\n"
        #out += self.getDataFromLink("https://where-am-i.org/", APILocation, "Where am I?") + "\n"
        out += self.getDataFromLink("https://api.ipify.org/?format=json", APIIPFinder, "What is my IP address?")
        return out
    
    def query(self, text):
        print("----------------------------")
        openai.api_key = apikey
        try:
            embeddedquery = self.loadAPIQueryEmbedding()
        except:
            self.makeAPIQueryEmbedding()
            embeddedquery = self.loadAPIQueryEmbedding()

        try:
            embeddedfunction = self.loadFunctionQueryEmbedding()
        except:
            self.makeFunctionQueryEmbedding()
            embeddedfunction = self.loadFunctionQueryEmbedding()

        textToQuery, apinumber, funcnumber = self.generateSetupText(embeddedquery, embeddedfunction, text)
        print(textToQuery)

        #print(textToQuery)

        #print(textToQuery)
        
        response = openai.Completion.create(
        engine=MODEL,
        prompt=textToQuery,
        temperature=0.2,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )
        logUsage(response)


        response = response["choices"][0]["text"].lstrip()
        choice = response[0]
        restofresponse = response[1:].lstrip()


        if choice == "A":
            link = re.findall('https?://[^\s]+', response)[0]

            print(link)

            api = self.getAPIFromNumber(apinumber)
            
            try:
                data = self.getDataFromLink(link, api, text)
            except Exception as e:
                print(apinumber)
                print(response)
                print(link)
                raise e
            
            
            textToAnalyse = self.generateAnalysisText(data) + "\n\n" + text
            
            print(textToAnalyse)

            newresponse = openai.Completion.create(
            engine=MODEL,
            prompt=textToAnalyse,
            temperature=0.5,
            max_tokens=1024,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.6
            )
            logUsage(newresponse)

            #print(newresponse)

            response = newresponse["choices"][0]["text"].lstrip()

        elif choice == "F":
            chosenfunction = self.getFuncFromNumber(funcnumber)
            chosenfunctiontorun = restofresponse
            funcglobals = inspect.getmodule(chosenfunction.function).__dict__
            exec(chosenfunctiontorun, funcglobals)

        elif choice == "N":
            print(self.info + "\n" + text + "\n" + JARVIS)
            response = openai.Completion.create(
            engine=MODEL,
            prompt=self.info + "\n" + JARVIS + "\n" + text,
            temperature=1,
            max_tokens=1024,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
            )
            logUsage(response)
            response = response["choices"][0]["text"].lstrip()
        
        print("----------------------------")
        return response
    
    def loadAPIQueryEmbedding(self):
        df = pd.read_csv('embedded_questions.csv')
        df["embedding"] = df.embedding.apply(eval)
        df["embedding"] = df.embedding.apply(np.array)
        return df
    
    def makeAPIQueryEmbedding(self):
        apitexts = [i.showApiLink() for i in self.apis]
        df = pd.DataFrame(apitexts, columns=["items"])
        df["embedding"] = df.apply(lambda x: get_embedding_batch(x.tolist()))
        df.to_csv('embedded_questions.csv', index=False)
    


    def loadFunctionQueryEmbedding(self):
        df = pd.read_csv('embedded_functions.csv')
        df["embedding"] = df.embedding.apply(eval)
        df["embedding"] = df.embedding.apply(np.array)
        return df
    
    def makeFunctionQueryEmbedding(self):
        functiontexts = [i.showFunction() for i in self.functions]
        df = pd.DataFrame(functiontexts, columns=["items"])
        df["embedding"] = df.apply(lambda x: get_embedding_batch(x.tolist()))
        df.to_csv('embedded_functions.csv', index=False)

    def generateSetupText(self, df, df1, prompt):
        embedding = get_embedding(prompt, model='text-embedding-ada-002')
        df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, embedding))
        res = df.sort_values('similarities', ascending=False).head(1)
        newres = res.values.flatten().tolist()
        apinum = res.index[0]+1
        api = newres[0]
        print(newres[-1])

        embedding = get_embedding(prompt, model='text-embedding-ada-002')
        df1['similarities'] = df1.embedding.apply(lambda x: cosine_similarity(x, embedding))
        res = df1.sort_values('similarities', ascending=False).head(1)
        newres = res.values.flatten().tolist()
        funcnum = res.index[0]+1
        func = newres[0]
        print(newres[-1])


        text = f"Here is an API: {api}.\n\nHere is a function: {func}\n\nHere is some information: {self.info}\n\nHere is a request: {prompt}\n\n\
If the request is better suited to the function, reply with an F followed by the function filled in with the request (The function is in python) on the next line. However, if the API \
is better suited to the query, reply with an A, followed by the API filled in on the next line. Choose only one of these.\n"
        return text, apinum, funcnum


    def getMostUsefulParagraph(self, paragraphlist, valuepairs, prompt):
        n = 3
        """
        for paragraph in paragraphlist:
            print(paragraph[:min(len(paragraph), 500)])
            print("-------------------------")"""
        
        paragraphlist = [i for i in paragraphlist if i != ""]
        df = pd.DataFrame(paragraphlist, columns=["items"])
        df["embedding"] = df.apply(lambda x: get_embedding_batch(x.tolist()))
        embedding = get_embedding(prompt, model='text-embedding-ada-002')
        df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, embedding))
        res = df.sort_values('similarities', ascending=False).head(n).iloc[:, 0].tolist()

        ress = []
        for chosenres in res:
            for i in valuepairs:
                if i[0] == chosenres:
                    chosenres += "\n" + i[1]
                    break
                if i[1] == chosenres:
                    chosenres = i[0] + "\n" + chosenres
            ress.append(chosenres)

        return "\n\n\n".join(ress)
        
    
    def getDataFromLink(self, link, api: API, prompt):
        browser.get(link)
        time.sleep(api.accessDelay)
        content = browser.page_source
        if type(api.datacleaning) == types.FunctionType:
            content = api.datacleaning(content)
        
        if type(content) == list:
            with open("out.txt", "w", encoding="utf-8") as file:
                file.write("\n---------------\n".join(content[0]))
            content, valuepairs = content
            content = self.getMostUsefulParagraph(content, valuepairs, prompt)
            print(content)

        
        return content


    def getAPIFromNumber(self, number):
        for api in self.apis:
            if api.number == number:
                return api


    def getFuncFromNumber(self, number):
        for func in self.functions:
            if func.number == number:
                return func

    def getApiNumberFromString(self, string: str):
        out = ""
        for i in string:
            if i == ")":
                break
            elif i.isnumeric():
                out += i
        return int(out)

    def generateAnalysisText(self, data):
        return "Information:\n" + self.info + "\n" + data + "\n\nAnswer the following question using the information \
I just gave you, not from your own knowledge base." + JARVIS


def get_embedding(text: str, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=[text], model=model)
    logUsage(response)
    return response["data"][0]["embedding"]

def get_embedding_batch(texts: list, model="text-embedding-ada-002"):
    texts = [i for i in texts if i != ""]
    responses = openai.Embedding.create(input=texts, model=model)
    logUsage(responses)
    
    return [responses["data"][i]["embedding"] for i in range(len(texts))]

def remove_special(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def logUsage(openairesponse):
    with open("usage.log", "a") as file:
        try:
            file.write(f"{openairesponse['model']}: {openairesponse['usage']['total_tokens']}\n")
        except:
            print(openairesponse)
            raise ValueError

def loadApiKeyFromFile(file):
    global apikey
    with open(file, "r") as f:
        apikey = f.read()

def getTextFromHTMLClassesAndIDs(text, classes=[], ids=[], splitchildren = [], maxofeachsection = 10):
    soup = BeautifulSoup(text, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()

    found = []
    for id in ids:
        foundsoup = soup.find_all(attrs={"id": id})
        found += foundsoup
    for classs in classes:
        foundsoup = soup.find_all(attrs={"class": classs})
        found += foundsoup
    
    splittext = []
    valuepairs = []
    
    newfound = []
    for founditem in [soup]:
        foundparents = []
        for parent in splitchildren:
            #print(founditem.findChildren(attrs={parent[0]: parent[1]}, recursive=True))
            for foundparent in founditem.findChildren(attrs={parent[0]: parent[1]}, recursive=True):
                foundparents.append(foundparent)
        for parent in foundparents:
            children = parent.findChildren(recursive=False)
            for child in children:
                newfound.append(child)

                """text = child.get_text(strip=True, separator=" ")
            
                if not(text.strip()):
                    continue

                splittext.append(text)
                text1 = "\n".join([f"{i[0]}:{i[1]}" for i in child.attrs.items()])
                splittext.append(text1)
                valuepairs.append([text1, text])
                child.extract()"""
    
    for id in ids:
        foundsoup = soup.find_all(attrs={"id": id})
        newfound += foundsoup
    for classs in classes:
        foundsoup = soup.find_all(attrs={"class": classs})
        newfound += foundsoup
        
    alltext = []
    accum = 0
    for founditem in newfound:
        text = founditem.get_text(strip=True, separator=" ")
        if not(text.strip()):
            continue
        
        
        accum += len(text)
        if accum > 20000:
            continue
        alltext.append(text)
        text1 = "\n".join([f"{i[0]}:{i[1]}" for i in founditem.attrs.items()])
        alltext.append(text1)
        valuepairs.append([text1, text])
        

    return alltext, valuepairs

def wolframDataClean(data):
    return "\n".join(re.findall('alt="(.*?)"', data))

def whereamiDataClean(data):
    return "Address: " + re.findall('<div id="address" class="datavalue">(.*?)</div>', data)[0] + "\nLat: " + re.findall('<div id="latitude" class="datavalue">(.*?)</div>', data)[0] + "\nLon: " + re.findall('<div id="longitude" class="datavalue">(.*?)</div>', data)[0]

def stackoverflowDataClean(data):
    textlist, valuepairs = getTextFromHTMLClassesAndIDs(data, classes=["d-flex fw-wrap pb8 mb16 bb bc-black-075"], ids=["question-header", "question", "answers"], splitchildren=[["id", "answers"]])
    return [textlist, valuepairs]

def googleDataClean(data):
    textlist, valuepairs = getTextFromHTMLClassesAndIDs(data, classes=["ULSxyf"], ids=["appbar"], splitchildren=[["jsname", "N760b"]])
    return [textlist, valuepairs]

def wikiDataClean(data):
    textlist, valuepairs = getTextFromHTMLClassesAndIDs(data, splitchildren=[["class", "mw-parser-output"]])
    return [textlist, valuepairs]

def weatherDataClean(data):
    textlist, valuepairs = getTextFromHTMLClassesAndIDs(data, splitchildren=[["id", "forecastContent"]])
    return [textlist, valuepairs]

def jsonDataClean(data):
    soup = BeautifulSoup(data, features="html.parser")
    parsed = json.loads(soup.text)
    text = str(parsed)
    text = text.replace("'", "")
    return text
    


        
apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish

APIStackOverFlow = API("https://stackoverflow.com/questions/{}", ["questionnum"], {"questionnum": "The number of the question"}, {"questionnum": int}, datacleaning=stackoverflowDataClean)
APIWikipedia = API("https://en.wikipedia.org/wiki/{}", ["searchterm"], datacleaning=wikiDataClean)
#APIGoogle = API("https://www.google.com/search?q={}", ["searchterm"], description="Use this for things including statistics", datacleaning=googleDataClean)
APIDateTime = API("https://www.timeapi.io/api/Time/current/zone?timeZone={}", ["timezone"], queryform={"timezone": "IANA time zone name"}, datacleaning=jsonDataClean)
APIMaths = API("https://www.wolframalpha.com/input?i={}", ["mathsquestion"], queryform={"mathsquestion": "Pure maths expression, using the %2B format"}, accessDelay=7, datacleaning=wolframDataClean)
APIWeather = API("http://api.weatherapi.com/v1/current.json?key=" + APIKEYS["WeatherAPI"] + "&q={}&aqi=no", ["location"], queryform={"location": "Latitude, Longitude or IP address or post code or city name"}, datacleaning=jsonDataClean)
APIExchangeRate = API("https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}", ["firstcurrency", "secondcurrency"], datacleaning=jsonDataClean)
APIIPFinder = API("https://api.ipify.org/?format=json", datacleaning=jsonDataClean, description="Gets the IP address of the user")
APILocation = API("https://where-am-i.org/", description = "Use this to get the current location of the user.", datacleaning=whereamiDataClean, accessDelay=2)
FunctionExplode = Function(explode, args=["suit"], typeannots = {"suit": "int"}, description = "Use this function to initate self destruct on the suit given, and make it explode. @Param suit: integer number of the suit.")
FunctionBuild = Function(build, args=["suit"], typeannots = {"suit": "int"}, description = "Use this function to initate the creation of the suit given. @Param suit: integer number of the suit.")
chatbot = ChatBot([APIStackOverFlow, APIWikipedia, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation], [FunctionExplode, FunctionBuild])

#print(chatbot.query("Quote what is said about Tony the Pony on question 1732348 on SO? Start from 'You can't parse [X]...', and translate it into french. Only say the first 5 words."))
#print(chatbot.query("How many answers are on stack overflow question 75221583?"))
#print(chatbot.query("What is the latest post from Rick Roals on quora? Quote him in full, and give me the link to the post."))
#print(chatbot.query("Give me the etymology of water using the wikipedia article for water."))
#print(chatbot.query("Is it the evening right now?"))
#print(chatbot.query("What is x if (e^(x^2))/x=5+x?"))
#print(chatbot.query("What is d/dx if f(x) = (e^(x^2))/x?"))
#print(chatbot.query("What is en passant?"))
#print(chatbot.query("What is the weather today? I live at 30, 30."))
#print(chatbot.query("Tell me a story."))
#print(chatbot.query("How many dogecoin is a dollar worth right now?"))
#print(chatbot.query("What is my IP address?"))
#print(chatbot.query("Where am I?")) # TODO fix
#print(chatbot.query("How many people live in the US right now according to google?"))
#print(chatbot.query("How many people have covid right now? Use google."))
#print(chatbot.query("Translate the entire rick roll lyrics into french"))
#print(chatbot.query("How does the queen move? Check from wikipedia"))
# Information test
#print(chatbot.query("What is my name?"))
#print(chatbot.query("What is your name? Also, what is my name?"))
# Programming test
print(chatbot.query("Jarvis, do me a favour and build mark 42"))
print(chatbot.query("Jarvis, do me a favour and blow mark 42"))
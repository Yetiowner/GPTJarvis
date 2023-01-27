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

with open("usage.log", "a") as file:
    file.write("--------------------\n")

try:
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)

except:
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    browser = webdriver.Firefox(options=options)

"""browser.get("https://stackoverflow.com/questions/36768068/get-meta-tag-content-property-with-beautifulsoup-and-python")
text = browser.page_source
soup = BeautifulSoup(text, features="html.parser")
for script in soup(["script", "style"]):
    script.extract()
print(soup.attrs)
quit()"""
MODEL = "text-davinci-003"

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
        if self.description:
            queriesinfo += f". Description: {self.description}"
        showstr = f"""API {self.number}:
        {self.link.format(*["{" + i + "}" for i in self.querynames])}, where {queriesinfo}"""
        return showstr
    
    def __repr__(self):
        return f"API {self.number}: {self.link}"

class ChatBot():
    def __init__(self, apis: List[API] = []):
        self.apis = apis
    
    def query(self, text):
        print("----------------------------")
        textToQuery = self.generateSetupText() + text
        #print(textToQuery)
        openai.api_key = apikey

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
        #print(response)


        try:
            link = re.findall('https?://[^\s]+', response)[0]
        except IndexError:
            response = openai.Completion.create(
            engine=MODEL,
            prompt=text,
            temperature=1,
            max_tokens=1024,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
            )
            logUsage(response)
            response = response["choices"][0]["text"].lstrip()
            return response

        print(link)

        apinumber = self.getApiNumberFromString(response[response.index(link)+len(link):])
        api = self.getAPIFromNumber(apinumber)
        
        try:
            data = self.getDataFromLink(link, api, text)
        except Exception as e:
            print(apinumber)
            print(response)
            print(link)
            raise e
        
        
        
        
        textToAnalyse = self.generateAnalysisText(data) + "\n\n" + text
        
        #print(textToAnalyse)

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

        newresponse = newresponse["choices"][0]["text"].lstrip()
        print("----------------------------")
        return newresponse

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

    def getApiNumberFromString(self, string: str):
        out = ""
        for i in string:
            if i == ")":
                break
            elif i.isnumeric():
                out += i
        return int(out)

    def generateAnalysisText(self, data):
        return "Information:\n\n" + data + "\n\nAnswer the following question using the information \
I just gave you, not from your own knowledge base. Answer like you are Jarvis from Iron Man. Occasionally \
include pleasantly sarcastic comments."

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
        if accum > 15000:
            continue
        alltext.append(text)
        text1 = "\n".join([f"{i[0]}:{i[1]}" for i in founditem.attrs.items()])
        alltext.append(text1)
        valuepairs.append([text1, text])
        

    return alltext, valuepairs

def wolframDataClean(data):
    return "\n".join(re.findall('alt="(.*?)"', data))

def whereamiDataClean(data):
    return re.findall('<div class="aiAXrc">(.*?)</div>', data)[0] + "\n" + re.findall('<span class="fMYBhe">(.*?)</span>', data)[0]

def stackoverflowDataClean(data):
    textlist, valuepairs = getTextFromHTMLClassesAndIDs(data, classes=["d-flex fw-wrap pb8 mb16 bb bc-black-075"], ids=["question-header", "question", "answers"], splitchildren=[["id", "answers"]])
    return [textlist, valuepairs]

def googleDataClean(data):
    textlist, valuepairs = getTextFromHTMLClassesAndIDs(data, classes=["ULSxyf"], ids=["appbar"], splitchildren=[["jsname", "N760b"]])
    return [textlist, valuepairs]

def wikiDataClean(data):
    textlist, valuepairs = getTextFromHTMLClassesAndIDs(data, splitchildren=[["class", "mw-parser-output"]])
    #print([type(valuepairs) for i in textlist])
    return [textlist, valuepairs]
        
apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish
APIStackOverFlow = API("https://stackoverflow.com/questions/{}", ["questionnum"], {"questionnum": "The number of the question"}, {"questionnum": int}, datacleaning=stackoverflowDataClean)
APIBrilliant = API("https://brilliant.org/wiki/{}", ["subject"])
APIQuora = API("https://www.quora.com/search?q={}", ["query"])
APIWikipedia = API("https://en.wikipedia.org/wiki/{}", ["searchterm"], datacleaning=wikiDataClean)
APIGoogle = API("https://www.google.com/search?q={}", ["searchterm"], description="Use this for things including statistics", datacleaning=googleDataClean)
APIDateTime = API("https://www.timeapi.io/api/Time/current/zone?timeZone={}", ["timezone"], queryform={"timezone": "IANA time zone name"}, datacleaning=None)
APIMaths = API("https://www.wolframalpha.com/input?i={}", ["mathsquestion"], queryform={"mathsquestion": "Pure maths expression, using the %2B format"}, accessDelay=7, datacleaning=wolframDataClean)
APIWeather = API("https://www.metoffice.gov.uk/weather/forecast/u1214b469#?date={}", ["date"], queryform={"date": "yyyy-mm-dd"})
APIExchangeRate = API("https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}", ["firstcurrency", "secondcurrency"], datacleaning=None)
APIIPFinder = API("https://api.ipify.org/?format=json", datacleaning=None)
APILocation = API("https://www.google.com/search?q=Where+am+i", description = "Use this to get the current location of the user.", datacleaning=whereamiDataClean)
chatbot = ChatBot([APIStackOverFlow, APIBrilliant, APIQuora, APIWikipedia, APIGoogle, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation])
#print(chatbot.query("Quote what is said about Tony the Pony on question 1732348 on SO? Start from 'You can't parse [X]...', and translate it into french. Only say the first 5 words."))
#print(chatbot.query("How many answers are on stack overflow question 75221583?"))
#print(chatbot.query("What is backpropogation? Get answers from billiant."))
#print(chatbot.query("What is the latest post from Rick Roals on quora? Quote him in full, and give me the link to the post."))
print(chatbot.query("Give me the etymology of water using the wikipedia article for water."))
#print(chatbot.query("Is it the evening right now? I am in England."))
#print(chatbot.query("What is x if (e^(x^2))/x=5+x?"))
#print(chatbot.query("What is d/dx if f(x) = (e^(x^2))/x?"))
#print(chatbot.query("What is en passant?"))
#print(chatbot.query("What is the weather today?"))
#print(chatbot.query("Tell me a story."))
#print(chatbot.query("How many dogecoin is a dollar worth right now?"))
#print(chatbot.query("What is my IP address?"))
#print(chatbot.query("Where am I?")) # TODO fix
#print(chatbot.query("How many people live in the US right now according to google?"))
#print(chatbot.query("How many people have covid right now? Use google."))
#print(chatbot.query("Translate the entire rick roll lyrics into french"))
#print(chatbot.query("How does the queen move?"))
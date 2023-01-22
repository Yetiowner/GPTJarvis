from typing import Union, Optional, Callable, List
import types
import openai
import requests
import extracttxt
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(options=chrome_options)

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

        response = response["choices"][0]["text"].lstrip()
        #print(response)


        try:
            link = re.findall('https?://[^\s]+', response)[0]
        except IndexError:
            response = openai.Completion.create(
            engine=MODEL,
            prompt=text,
            temperature=1,
            max_tokens=512,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
            )
            response = response["choices"][0]["text"].lstrip()
            return response

        print(link)

        apinumber = self.getApiNumberFromString(response[response.index(link)+len(link):])
        api = self.getAPIFromNumber(apinumber)
        
        try:
            data = self.getDataFromLink(link, api)
        except Exception as e:
            print(apinumber)
            print(response)
            print(link)
            raise e
        
        #print(data)
        
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

        #print(newresponse)

        newresponse = newresponse["choices"][0]["text"].lstrip()
        print("----------------------------")
        return newresponse

    
    def getDataFromLink(self, link, api: API):
        browser.get(link)
        time.sleep(api.accessDelay)
        content = browser.page_source
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
        return "Information:\n\n" + data + "\n\nAnswer the following question using the information \
I just gave you, not from your own knowledge base."

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

def getTextFromHTMLClassesAndIDs(text, classes=[], ids=[], maxlen=8000):
    soup = BeautifulSoup(text, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()

    found = []
    for id in ids:
        found.append(soup.find(attrs={"id": id}))
    for classs in classes:
        found.append(soup.find(attrs={"class": classs}))
    
    alltext = []
    for founditem in found:
        text = founditem.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        alltext.append(text)
    text = "\n".join(alltext)
    text = text[:min(maxlen if maxlen != -1 else len(text), len(text)-1)]
    return text

def wolframDataClean(data):
    return "\n".join(re.findall('alt="(.*?)"', data))

def whereamiDataClean(data):
    return re.findall('<div class="aiAXrc">(.*?)</div>', data)[0] + "\n" + re.findall('<span class="fMYBhe">(.*?)</span>', data)[0]

def stackoverflowDataClean(data):
    text = getTextFromHTMLClassesAndIDs(data, classes=["d-flex fw-wrap pb8 mb16 bb bc-black-075"], ids=["question-header", "mainbar"])
    return text
        
apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish
APIStackOverFlow = API("https://stackoverflow.com/questions/{}", ["questionnum"], {"questionnum": "The number of the question"}, {"questionnum": int}, datacleaning=stackoverflowDataClean)
APIBrilliant = API("https://brilliant.org/wiki/{}", ["subject"])
APIQuora = API("https://www.quora.com/search?q={}", ["query"])
APIWikipedia = API("https://en.wikipedia.org/wiki/{}", ["searchterm"])
APIGoogle = API("https://www.google.com/search?q={}", ["searchterm"])
APIDateTime = API("https://www.timeapi.io/api/Time/current/zone?timeZone={}", ["timezone"], queryform={"timezone": "IANA time zone name"})
APIMaths = API("https://www.wolframalpha.com/input?i={}", ["mathsquestion"], queryform={"mathsquestion": "Pure maths expression, using the %2B format"}, accessDelay=7, datacleaning=wolframDataClean)
APIWeather = API("https://www.metoffice.gov.uk/weather/forecast/u1214b469#?date={}", ["date"], queryform={"date": "yyyy-mm-dd"})
APIExchangeRate = API("https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}", ["firstcurrency", "secondcurrency"], datacleaning=None)
APIIPFinder = API("https://api.ipify.org/?format=json", datacleaning=None)
APILocation = API("https://www.google.com/search?q=Where+am+i", description = "Use this to get the current location of the user.", datacleaning=whereamiDataClean)
chatbot = ChatBot([APIStackOverFlow, APIBrilliant, APIQuora, APIWikipedia, APIGoogle, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation])
#print(chatbot.query("Quote what is said about Tony the Pony on question 1732348 on SO? Start from 'You can't parse [X]...', and translate it into french."))
#print(chatbot.query("What is backpropogation? Get answers from billiant."))
#print(chatbot.query("What is the latest post from Rick Roals on quora? Quote him in full, and give me the link to the post."))
#print(chatbot.query("Give me the etymology of water using wikipedia"))
#print(chatbot.query("Is it the evening right now? I am in England."))
#print(chatbot.query("What is x if (e^(x^2))/x=5?"))
print(chatbot.query("What is d/dx if f(x) = (e^(x^2))/x?"))
#print(chatbot.query("What is en passant?"))
#print(chatbot.query("What is the weather today?"))
#print(chatbot.query("Tell me a story."))
#print(chatbot.query("How many dogecoin is a dollar worth right now?"))
#print(chatbot.query("What is my IP address?"))
#print(chatbot.query("Where am I?"))
#print(chatbot.query("How many people live in the US right now according to google?"))
#print(chatbot.query("Translate the entire rick roll lyrics into french"))
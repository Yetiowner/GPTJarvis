import time
from typing import Union, Optional, Callable, List
import types
import openai
import GPTJarvis.src.extracttxt as extracttxt
import re
import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
from GPTJarvis.src.utils import loadPrompt
import GPTJarvis.src.personalities as personalities

"""C_describe(): describe a variable as a string
C_say(): output a string
C_interpret(): asks question about output and returns the answer in the method requested
C_choose(): Returns the index of an item in a list based on a query"""

MODEL = "gpt-3.5-turbo"
PERMANENTINFO = loadPrompt("PermanentInfo.txt", mode = "text")
FILEPATH = None

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
    def __init__(self, function, doc, priority=False):
        self.truefunction = function
        self.function = function.__name__
        self.doc = doc
        self.number = 0
        self.priority = priority
        self.mode = None
    
    def showFunction(self):
        return f"{self.mode}_{self.doc}"
    
    def __repr__(self):
        return f"Func {self.number}: {self.doc}"
    
    def showSimplifiedFunction(self):
        return f"{self.mode}_{self.doc}"


class ChatBot():
    def __init__(self, functions: List[Function] = [], readables: List[Function] = [], info = None, sampleCount = 3, minSimilarity = 0.6, personality = personalities.JARVIS, maxhistorylength = 3, temperature = 0.5):
        self.functions = functions
        self.readables = readables
        for index, function in enumerate(self.functions):
            function.number = index + 1
            function.mode = "F"
        for index, readable in enumerate(self.readables):
            readable.number = index + 1
            readable.mode = "R"
        print(info)
        self.originalinfo = PERMANENTINFO + "\n\n\n" + info
        self.info = self.genInfoText() # Information including previous accessor/func calls
        self.tempinfo = ""
        self.requesthistory = []
        self.temphistory = ""
        self.q_and_a_history = ""
        self.maxhistorylength = maxhistorylength
        self.sampleCount = sampleCount
        self.minSimilarity = minSimilarity
        self.personality = personality
        self.temperature = temperature
        openai.api_key = apikey
        with open(FILEPATH+"usage.log", "a") as file:
            file.write("--------------------\n")


        readableReloadRequired = self.getEmbeddingReloadRequired(self.readables, "reads")
        runnableReloadRequired = self.getEmbeddingReloadRequired(self.functions, "functions")

        if not readableReloadRequired:
            self.embeddedread = self.loadReadableQueryEmbedding()
        else:
            self.makeReadableQueryEmbedding()
            self.embeddedread = self.loadReadableQueryEmbedding()

        if not runnableReloadRequired:
            self.embeddedfunction = self.loadFunctionQueryEmbedding()
        else:
            self.makeFunctionQueryEmbedding()
            self.embeddedfunction = self.loadFunctionQueryEmbedding()
        
    
    def getEmbeddingReloadRequired(self, accessibles, name):
        realreadables = [i.showFunction() for i in accessibles]
        try:
            df = pd.read_csv(FILEPATH+f'embedded_{name}.csv')
        except FileNotFoundError:
            return True
        realreadablesfromdf = df["items"].values.tolist()
        noReadableReloadRequired = (realreadables != realreadablesfromdf)
        return noReadableReloadRequired

    def genInfoText(self):
        out = ""
        if self.originalinfo:
            out += self.originalinfo + "\n\n"
        #out += self.getDataFromLink("https://where-am-i.org/", APILocation, "Where am I?") + "\n"
        #out += self.getDataFromLink("https://api.ipify.org/?format=json", APIIPFinder, "What is my IP address?")
        return out
    
    def query(self, text):
        print("----------------------------")

        textToQuery, readnumbers, funcnumbers = self.generateSetupText(self.embeddedread, self.embeddedfunction, text)
        self.display(textToQuery)

        #print(textToQuery)

        #print(textToQuery)
        print(1)
        response = openai.ChatCompletion.create(
        model=MODEL,
        messages=textToQuery,
        temperature=self.temperature,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        timeout = 5
        )
        print(2)
        logUsage(response)


        superresponse = response["choices"][0]["message"]["content"].lstrip().rstrip()
        return superresponse

        responses = []

        for response in superresponse:
            print(response)
            if len(response) == 0:
                continue
            choice = response[0]
            if response[1] != " ":
                choice = None
            restofresponse = response[1:].lstrip()


            if choice == "R":
                readnumber = -1
                for readablenumber in readnumbers:
                    chosenreadable = self.getReadFromNumber(readablenumber)
                    if chosenreadable.function == restofresponse.split("(")[0]:
                        readnumber = readablenumber
                chosenread = self.getReadFromNumber(readnumber)
                if chosenread == None:
                    chosenread = Function(None)
                chosenreadtorun = restofresponse
                response = [chosenread, chosenreadtorun]

            elif choice == "F":
                funcnumber = -1
                for functionnumber in funcnumbers:
                    chosenfunc = self.getFuncFromNumber(functionnumber)
                    if chosenfunc.function == restofresponse.split("(")[0]:
                        funcnumber = functionnumber
                chosenfunction = self.getFuncFromNumber(funcnumber)
                if chosenfunction == None:
                    chosenfunction = Function(None)
                chosenfunctiontorun = restofresponse
                response = [chosenfunction, chosenfunctiontorun]

            elif choice == "N":
                print("=======================")
                response = restofresponse
            
            elif choice == "C":
                pass
            
            else:
                choice = "N"
            
            print("----------------------------")

            responses.append([choice, response])
        
        return responses
    
    def register_addInfo(self, info):
        self.tempinfo += info + "\n"
    
    def addInfo(self):
        self.info += self.tempinfo
        self.info += "\n"
        self.tempinfo = ""
    
    def register_addHistory(self, info):
        self.temphistory += info + "\n"
    
    def addHistory(self):
        self.requesthistory.append(self.temphistory)
        if len(self.requesthistory) > self.maxhistorylength:
            self.commitToLTM(self.requesthistory.pop(0), mode="history")
        self.temphistory = ""
    
    def breakConversation(self):
        self.commitToLTM(self.info, mode="info")
        self.commitToLTM(self.requesthistory, mode="history")
        self.info = self.genInfoText()
        self.requesthistory = []
        self.temphistory = ""
        self.tempinfo = ""
    
    def addQuestion(self, question):
        self.q_and_a_history += "Me: " + question + "\n"
    
    def addAnswer(self, answer):
        self.q_and_a_history += "You: " + answer + "\n\n"
    
    def commitToLTM(self, info, mode=None):
        #TODO
        pass

    def followThroughInformation(self, information, question):
        analysis = self.generateAnalysisText(information, question)
        self.display(analysis)
        response = openai.ChatCompletion.create(
        model=MODEL,
        messages=analysis,
        temperature=self.temperature,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )
        logUsage(response)
        response = response["choices"][0]["message"]["content"].lstrip().rstrip()
        return response
    
    def loadReadableQueryEmbedding(self):
        df = pd.read_csv(FILEPATH+'embedded_reads.csv')
        df["embedding"] = df.embedding.apply(eval)
        df["embedding"] = df.embedding.apply(np.array)
        return df
    
    def makeReadableQueryEmbedding(self):
        realreadables = [i.showFunction() for i in self.readables]
        simplifiedreadables = [i.showSimplifiedFunction() for i in self.readables]
        df = pd.DataFrame(simplifiedreadables, columns=["simplified"])
        df["embedding"] = df.apply(lambda x: get_embedding_batch(x.tolist()))
        df["items"] = realreadables
        df["priority"] = [i.priority for i in self.readables]
        df.to_csv(FILEPATH+'embedded_reads.csv', index=False)
    


    def loadFunctionQueryEmbedding(self):
        df = pd.read_csv(FILEPATH+'embedded_functions.csv')
        df["embedding"] = df.embedding.apply(eval)
        df["embedding"] = df.embedding.apply(np.array)
        return df
    
    def makeFunctionQueryEmbedding(self):
        realfunctions = [i.showFunction() for i in self.functions]
        simplifiedfunctions = [i.showSimplifiedFunction() for i in self.functions]
        df = pd.DataFrame(simplifiedfunctions, columns=["simplified"])
        df["embedding"] = df.apply(lambda x: get_embedding_batch(x.tolist()))
        df["items"] = realfunctions
        df["priority"] = [i.priority for i in self.functions]
        df.to_csv(FILEPATH+'embedded_functions.csv', index=False)

    def generateSetupText(self, df, df1, prompt):
        embedding = get_embedding(prompt, model='text-embedding-ada-002')

        df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, embedding))
        df_priority = df[df['priority'] == True]
        df = df[df['similarities'] >= self.minSimilarity]
        result = df[df["priority"] == False].sort_values('similarities', ascending=False).head(self.sampleCount)
        result = pd.concat([df_priority, result], axis=0)
        readables = []
        readablenums = []
        for index, res in result.iterrows():
            res = res.values
            newres = res
            readablenum = index+1
            readable = newres[-3]
            readables.append(readable)
            readablenums.append(readablenum)
        readables = "\n".join(readables)

        df1['similarities'] = df1.embedding.apply(lambda x: cosine_similarity(x, embedding))
        df1_priority = df1[df1['priority'] == True]
        df1 = df1[df1['similarities'] >= self.minSimilarity]
        result = df1[df1["priority"] == False].sort_values('similarities', ascending=False).head(self.sampleCount)
        result = pd.concat([df1_priority, result], axis=0)
        funcs = []
        funcnums = []
        for index, res in result.iterrows():
            res = res.values
            newres = res
            funcnum = index+1
            func = newres[-3]
            funcs.append(func)
            funcnums.append(funcnum)
        funcs = "\n".join(funcs)

        text = loadPrompt("QueryResult.txt")

        text[0]["content"] = text[0]["content"].format(personality=self.personality.prompt, info=self.info)
        text[-1]["content"] = text[-1]["content"].format(accessors=readables, functions=funcs, q_and_a_history=self.q_and_a_history.rstrip(), prompt=prompt)
        text = self.injectHistory(text)
        return text, readablenums, funcnums
    
    def display(self, prompts):
        for item in prompts:
            if "name" in item:
                label = item["name"]
            else:
                label = item["role"]
            print(label)
            content = item["content"]
            content = "\n".join(["\t" + i for i in content.split("\n")])
            print(content)

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
            with open(FILEPATH+"out.txt", "w", encoding="utf-8") as file:
                file.write("\n---------------\n".join(content[0]))
            content, valuepairs = content
            content = self.getMostUsefulParagraph(content, valuepairs, prompt)
            print(content)

        
        return content


    def getReadFromNumber(self, number):
        for read in self.readables:
            if read.number == number:
                return read


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

    def generateAnalysisText(self, data, question):
        text = loadPrompt("Analysis.txt")
        text[0]["content"] = text[0]["content"].format(personality=self.personality.prompt, info=self.info)
        text[-1]["content"] = text[-1]["content"].format(data=data, q_and_a_history=self.q_and_a_history, query=question)
        text = self.injectHistory(text)
        return text
    
    def injectHistory(self, text: list):
        for historyitem in self.requesthistory:
            thingtoinsert = {"role": "system", "name": "previous_requests", "content": historyitem}
            print(thingtoinsert)
            text.insert(len(text)-1, thingtoinsert)
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
    with open(FILEPATH+"usage.log", "a") as file:
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
    
def init_browser():
    global browser
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.preferences["permissions.default.geo"] = 1
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    browser = webdriver.Firefox(options=options)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))



"""APIStackOverFlow = API("https://stackoverflow.com/questions/{}", ["questionnum"], {"questionnum": "The number of the question"}, {"questionnum": int}, datacleaning=stackoverflowDataClean)
APIWikipedia = API("https://en.wikipedia.org/wiki/{}", ["searchterm"], datacleaning=wikiDataClean)
#APIGoogle = API("https://www.google.com/search?q={}", ["searchterm"], description="Use this for things including statistics", datacleaning=googleDataClean)
APIDateTime = API("https://www.timeapi.io/api/Time/current/zone?timeZone={}", ["timezone"], queryform={"timezone": "IANA time zone name"}, datacleaning=jsonDataClean)
APIMaths = API("https://www.wolframalpha.com/input?i={}", ["mathsquestion"], queryform={"mathsquestion": "Pure maths expression, using the %2B format"}, accessDelay=7, datacleaning=wolframDataClean)
APIWeather = API("http://api.weatherapi.com/v1/current.json?key=" + APIKEYS["WeatherAPI"] + "&q={}&aqi=no", ["location"], queryform={"location": "Latitude, Longitude or IP address or post code or city name"}, datacleaning=jsonDataClean)
APIExchangeRate = API("https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}", ["firstcurrency", "secondcurrency"], datacleaning=jsonDataClean)
APIIPFinder = API("https://api.ipify.org/?format=json", datacleaning=jsonDataClean, description="Gets the IP address of the user")
APILocation = API("https://where-am-i.org/", description = "Use this to get the current location of the user.", datacleaning=whereamiDataClean, accessDelay=2)"""

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
#print(Jarvis.query("Jarvis, build the mark 42"))
#print(Jarvis.query("Jarvis, do me a favour and blow mark 42"))
from typing import *
import inspect
import os
from os import listdir
from os.path import isfile, join
import subprocess
from subprocess import PIPE
import sys
import time
import threading
import types
from contextlib import redirect_stdout
import shutil
import GPTJarvis.src.voicebox as voicebox
import GPTJarvis.src.chatbot as chatbot
import GPTJarvis.src.personalities as personalities
import ctypes

#TODO: add long term memory
#TODO: add perma function wrapper
#TODO: add function chaining
#TODO: add true automation E.g. using @Jarvis.listener

functionlist = []
opqueue = []
apiKey = None
FILEPATH = ".Jarvis/"
UNLIKELYNAMESPACECOLLIDABLE = "ThereIsAFunctionHereASDFASDFASDFASDFASDF"
UNLIKELYNAMESPACECOLLIDABLE1 = "ReturningDataOfFunctionASDFASDFASDFASDFASDF"
chatbot.FILEPATH = FILEPATH
voicebox.FILEPATH = FILEPATH


def runnable(func):
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  wrapper.runnable = True
  wrapper.func = func
  return wrapper

def readable(func):
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  wrapper.readable = True
  wrapper.func = func
  return wrapper

def update():
  global opqueue
  #print(opqueue)
  if opqueue != []:
    op = opqueue.pop()
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    attrs = module.__dict__
    filename = f"{FILEPATH}streamedFileOutput/{os.path.basename(module.__file__)}.txt"

    with open(filename, "a") as file:
      with redirect_stdout(file):
        try:
          result = eval(op, attrs)
          if result == None:
            result = "Success!"
        except Exception as e:
          result = str(e)
    #while True:
    print(UNLIKELYNAMESPACECOLLIDABLE1+str(bytes(str(result), encoding='utf8')))
    sys.stdout.flush()

def loadApiKeyFromFile(openai_key_path):
  with open(openai_key_path, "r") as f:
    apikey = f.read()
  return apikey

def loadInfoFromFile(info_path):
  with open(info_path, "r") as f:
    info = f.read()
  return info

def setKey(key):
  chatbot.apikey = key

def init_main(scope: Union[str, List[str]] = "/", info = None, openai_key = None, sampleCount = 3, memory_retention_time = 900, personality = personalities.JARVIS):
  if type(scope) == str:
    scope = [scope]

  frame = inspect.currentframe().f_back
  filename = inspect.getframeinfo(frame)[0]
  dirname = os.path.dirname(filename)

  allaccessible = []
  for item in scope:
    joinedItemName = os.path.join(dirname, item)
    if os.path.isdir(joinedItemName):
      onlyfiles = [os.path.join(joinedItemName, f) for f in listdir(joinedItemName) if isfile(join(joinedItemName, f)) and os.path.splitext(f)[1] == ".py"]
      if filename in onlyfiles:
        onlyfiles.remove(filename)
      accessablefiles = onlyfiles
    elif os.path.isfile(joinedItemName):
      accessablefiles = [joinedItemName]
    elif os.path.isdir(item):
      onlyfiles = [os.path.join(item, f) for f in listdir(item) if isfile(join(item, f)) and os.path.splitext(f)[1] == ".py"]
      if filename in onlyfiles:
        onlyfiles.remove(filename)
      accessablefiles = onlyfiles
    elif os.path.isfile(item):
      accessablefiles = [item]
    else:
      raise FileNotFoundError
    allaccessible.extend(accessablefiles)

  accessablefiles = allaccessible


  if openai_key:
    chatbot.apikey = openai_key

  try:
    shutil.rmtree(FILEPATH+"streamedFileOutput")
  except FileNotFoundError:
    pass
  os.mkdir(FILEPATH+"streamedFileOutput")

  makeHidden(FILEPATH)
  if not(os.path.isdir(FILEPATH)):
    os.mkdir(FILEPATH)
    makeHidden(FILEPATH)



  processes = []
  for file in accessablefiles:
    processes.append(subprocess.Popen([sys.executable, file, "-JarvisSubprocess"], stdin=PIPE, stdout=PIPE, universal_newlines=True))
  
  #chatbot = ChatBot([APIStackOverFlow, APIWikipedia, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation], functionlist)
  allvariables = []
  functon_process_relationship = []
  for p in processes:
    processvariables = []
    expectedcount = 2
    for i in iter(p.stdout.readline, ""):
      if i:
        if i.startswith(UNLIKELYNAMESPACECOLLIDABLE):
          i = i[len(UNLIKELYNAMESPACECOLLIDABLE):]
          expectedcount -= 1
          evalled = eval(i)
          funced = []
          for evalledfunc in evalled:
            funced.append(chatbot.Function(*evalledfunc))
          for func in funced:
            functon_process_relationship.append([func, p])
          processvariables.append(funced)
          if expectedcount == 0:
            break
    allvariables.append(processvariables)
  

  functions = []
  readables = []
  for modulefuncs in allvariables:
    modulefunctions = modulefuncs[0]
    modulereadables = modulefuncs[1]
    for i in modulefunctions:
      functions.append(i)
    for i in modulereadables:
      readables.append(i)
  
  chosenchatbot = chatbot.ChatBot(functions, readables, info, sampleCount = sampleCount, personality = personality)


  startStreamingOutput()

  runProcessMainloop(chosenchatbot, functon_process_relationship, processes, memory_retention_time, personality)
  
def makeHidden(path):
  FILE_ATTRIBUTE_HIDDEN = 0x02
  ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

def startStreamingOutput():
  thread = threading.Thread(target=streamOutput)
  thread.start()

def streamOutput():
  lastfilename = None
  mypath = FILEPATH+"streamedFileOutput"
  linereached = {}
  while True:
    onlyfiles = [FILEPATH+"streamedFileOutput" + "/" + f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in onlyfiles:
      try:
        with open(file, "r+") as openedfile:
          readlines = openedfile.readlines()
          if file not in linereached:
            linereached[file] = 0
          for index in range(linereached[file], len(readlines)):
            if file != lastfilename:
              filenametodisplay = os.path.splitext(os.path.basename(file))[0]
              print(f"{filenametodisplay}: ")
            lastfilename = file
            linereached[file] += 1
            line = readlines[index].strip()
            print(line)
      except PermissionError:
        pass

def awaitQueryFinish():
  pass

def runProcessMainloop(chosenchatbot: chatbot.ChatBot, functon_process_relationship, processes, memory_retention_time, personality):
  """createQuery("detonate the mark 32", chosenchatbot, functon_process_relationship, processes)
  createQuery("build the mark 32", chosenchatbot, functon_process_relationship, processes)"""
  #ans = createQuery("what is the temperature of suit 6?", chosenchatbot, functon_process_relationship, processes)
  #voicebox.say(ans)
  #chosenchatbot.breakConversation()
  while True:
    startWaitingTime = time.time()
    qText = input("Enter a query: ")
    timeTaken = time.time()-startWaitingTime
    if timeTaken > memory_retention_time:
      print("Breaking conversation.")
      chosenchatbot.breakConversation()
    ans1 = createQuery(qText, chosenchatbot, functon_process_relationship, processes)
    voicebox.say(ans1, personality=personality)
  """print("\n\n")
  ans1_2 = createQuery("Is this suitable for ice cream?", chosenchatbot, functon_process_relationship, processes)
  voicebox.say(ans1_2)
  print("\n\n")
  ans1_3 = createQuery("What was my last question?", chosenchatbot, functon_process_relationship, processes)
  voicebox.say(ans1_3)
  chosenchatbot.breakConversation()"""
  #ans2 = createQuery("who invented the alphabet?", chosenchatbot, functon_process_relationship, processes)
  #voicebox.say(ans2)
  #createQuery("Set the weather to the opposite of sunny", chosenchatbot, functon_process_relationship, processes)
  
  
def createQuery(string, chosenchatbot: chatbot.ChatBot, functon_process_relationship, processes):
  chosentype, result = chosenchatbot.query(string)
  print(result)
  chosenchatbot.register_addHistory(f"My query: {string}")
  if chosentype == "N":
    chosenchatbot.register_addHistory(f"Your response: N {result}")
    chosenchatbot.addHistory()
    return result
  else:
    for function in functon_process_relationship:
      if function[0] == result[0]:
        chosenprocess = function[1]
    
    thingtorun = result[1]
    if "\n" in thingtorun:
      thingtorun = thingtorun.split("\n")[0]

    if thingtorun.split("(")[0] != result[0].function:
      result = chosenchatbot.followThroughInformation("", string)
      chosenchatbot.register_addHistory(f"Your response: {result}")
      chosenchatbot.addHistory()
      return result

    chosenprocess.stdin.write(thingtorun+"\n")
    chosenprocess.stdin.flush()
    validoutput = False
    while not(validoutput):
      output = chosenprocess.stdout.readline()
      if output.startswith(UNLIKELYNAMESPACECOLLIDABLE1):
        output = list(eval(output[len(UNLIKELYNAMESPACECOLLIDABLE1):]))
        output = bytes(output).decode("utf-8")
        output = output.strip()
        validoutput = True
    #chosenchatbot.register_addHistory(f"Me: {string}\n{chosentype} {thingtorun}")
    if result[0].mode == "R":
      explainedOutput = f"Your response: {result[0].mode} {thingtorun} \n\nResult: {output if len(output) < 100 else 'Truncated as too long'}"
      explainedOutputFull = f"Your response: {result[0].mode} {thingtorun} \n\nResult: {output}"

      chosenchatbot.register_addInfo(explainedOutput)
      chosenchatbot.addInfo()

      chosenchatbot.register_addHistory(explainedOutput)
      textResult = chosenchatbot.followThroughInformation(explainedOutputFull + f" Where {result[0].showFunction()}", string)
      chosenchatbot.register_addHistory(f"You: {textResult}")
      chosenchatbot.addHistory()
      #chosenchatbot.register_addInfo(f"Your response: {textResult}")
      #chosenchatbot.addInfo()
      return textResult
    #chosenchatbot.addHistory()
    if result[0].mode == "F":
      explainedOutput = f"Your response: {result[0].mode} {thingtorun} \n\nResult: {output if len(output) < 100 else 'Truncated as too long'}"
      explainedOutputFull = f"Your response: {result[0].mode} {thingtorun} \n\nResult: {output}"
      chosenchatbot.register_addInfo(explainedOutput)
      chosenchatbot.addInfo()

      chosenchatbot.register_addHistory(explainedOutput)
      textResult = chosenchatbot.followThroughInformation(explainedOutputFull + f" Where {result[0].showFunction()}", string)
      chosenchatbot.register_addHistory(f"You: {textResult}")
      chosenchatbot.addHistory()
      return textResult
    #print(chosenprocess)
    #print(thingtorun)


def listenForRunCommand():
  global opqueue
  while True:
    try:
      x = input()
      opqueue.append(x)
    except EOFError as e:
      pass

def init():
  #x = input() # wait for confirmation
  frame = inspect.stack()[1]
  module = inspect.getmodule(frame[0])
  if "-JarvisSubprocess" not in sys.argv:
    return
  diagnostics = []
  functions = [getattr(module, a) for a in dir(module) if isinstance(getattr(module, a), types.FunctionType)]
  diagnostics.append(functions)
  readables = []
  runnables = []
  for item in functions:
    if getattr(item, "runnable", False):
      runnables.append(item)
    if getattr(item, "readable", False):
      readables.append(item)


  displayFunctions(runnables)
  displayFunctions(readables)
  
  thread = threading.Thread(target=listenForRunCommand)
  thread.start()

def displayFunctions(functions):
  out = []
  for function in functions:
    func = function.func
    out.append([func.__name__, inspect.getfullargspec(func).args, {}, {i: j.__name__ for i, j in get_type_hints(func).items()}, func.__doc__])
  print(UNLIKELYNAMESPACECOLLIDABLE + str(out))
  sys.stdout.flush()
  
  
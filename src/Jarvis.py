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
import ctypes

#TODO: multiple options for func per request
#TODO: add long term memory
#TODO: add forgetfullness
#TODO: add personalities

functionlist = []
opqueue = []
apiKey = None
FILEPATH = ".Jarvis/"
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
    print(result)
    sys.stdout.flush()

def loadApiKeyFromFile(openai_key_path):
  chatbot.loadApiKeyFromFile(openai_key_path)

def setKey(key):
  chatbot.apikey = key

def init_main(scope: Union[str, List[str]] = "folder", info = None, openai_key = None):

  if type(scope) == str:
    scope = [scope]

  allaccessible = []
  for item in scope:
    if item == "folder":
      frame = inspect.stack()[1]
      module = inspect.getmodule(frame[0])
      filename = module.__file__
      dirname = os.path.dirname(filename)
      onlyfiles = [dirname + ("\\" if "\\" in filename else "/") + f for f in listdir(dirname) if isfile(join(dirname, f)) and os.path.splitext(f)[1] == ".py"]
      onlyfiles.remove(filename)
      accessablefiles = onlyfiles
    else:
      accessablefiles = item
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
    processes.append(subprocess.Popen([sys.executable, file], stdin=PIPE, stdout=PIPE, universal_newlines=True))
  
  #chatbot = ChatBot([APIStackOverFlow, APIWikipedia, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation], functionlist)
  allvariables = []
  functon_process_relationship = []
  for p in processes:
    processvariables = []
    expectedcount = 2
    for i in iter(p.stdout.readline, ""):
      if i:
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
  
  chosenchatbot = chatbot.ChatBot(functions, readables, info)

  startStreamingOutput()

  runProcessMainloop(chosenchatbot, functon_process_relationship, processes)
  
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

def runProcessMainloop(chosenchatbot, functon_process_relationship, processes):
  """createQuery("detonate the mark 32", chosenchatbot, functon_process_relationship, processes)
  createQuery("build the mark 32", chosenchatbot, functon_process_relationship, processes)"""
  #ans = createQuery("what is the temperature of suit 6?", chosenchatbot, functon_process_relationship, processes)
  #voicebox.say(ans)
  #chosenchatbot.breakConversation()
  while True:
    ans1 = createQuery(input("Enter a query: "), chosenchatbot, functon_process_relationship, processes)
    voicebox.say(ans1)
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
  chosenchatbot.register_addInfo(f"My query: {string}")
  if chosentype == "N":
    chosenchatbot.register_addInfo(f"Your response: {result}")
    chosenchatbot.addInfo()
    return result
  else:
    for function in functon_process_relationship:
      if function[0] == result[0]:
        chosenprocess = function[1]
    
    thingtorun = result[1]

    if thingtorun.split("(")[0] != result[0].function:
      result = chosenchatbot.followThroughInformation("", string)
      chosenchatbot.register_addInfo(f"Your response: {result}")
      chosenchatbot.addInfo()
      return result

    chosenprocess.stdin.write(thingtorun+"\n")
    chosenprocess.stdin.flush()
    output = chosenprocess.stdout.readline().strip()
    chosenchatbot.register_addHistory(f"Me: {string}\nYou: {chosentype} {thingtorun}")
    chosenchatbot.addHistory()
    if result[0].mode == "R":
      explainedOutput = f"Result of {thingtorun}: \n{output}"
      chosenchatbot.register_addInfo(explainedOutput)
      textResult = chosenchatbot.followThroughInformation(explainedOutput, string)
      chosenchatbot.register_addInfo(f"Your response: {textResult}")
      chosenchatbot.addInfo()
      return textResult
    if result[0].mode == "F":
      explainedOutput = f"Result of running {thingtorun}: \n{output}"
      chosenchatbot.register_addInfo(explainedOutput)
      textResult = chosenchatbot.followThroughInformation(explainedOutput, string)
      chosenchatbot.register_addInfo(f"Your response: {textResult}")
      chosenchatbot.addInfo()
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
  print(out)
  sys.stdout.flush()
  
  
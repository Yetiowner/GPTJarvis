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
import GPTJarvis.src.config as config
import GPTJarvis.src.codechecker as codechecker
import GPTJarvis.src.customfunctions as customfunctions
import GPTJarvis.src.utils as utils
import GPTJarvis.src.findError as findError
import ctypes
import functools
import importlib.util
import sys
from enum import Enum
import keyboard
import traceback

#TODO: add long term memory
#TODO: add true automation E.g. using @Jarvis.listener

functionlist = []
opqueue = []
requestQueue = []
apiKey = None

allreadables = []
allrunnables = []

FILEPATH = ".Jarvis/"
UNLIKELYNAMESPACECOLLIDABLE = "ThereIsAFunctionHereASDFASDFASDFASDFASDF"
UNLIKELYNAMESPACECOLLIDABLE1 = "ReturningDataOfFunctionASDFASDFASDFASDFASDF"
chatbot.FILEPATH = FILEPATH
voicebox.FILEPATH = FILEPATH

class JarvisBecameEvilError(Exception):
  """Raised when Jarvis attempts to run dangerous code.
"Oopsie Daisy" """
  def __init__(self, message):
    self.message = message
    super().__init__(self.message)

class App:
  def __init__(self, chosenchatbot, function_module_relationship, memory_retention_time, personality, inbuiltbackgroundlistener, outputfunc, outputasync):
    self.chosenchatbot = chosenchatbot
    self.function_module_relationship = function_module_relationship
    self.memory_retention_time = memory_retention_time
    self.personality = personality
    self.inbuiltbackgroundlistener = inbuiltbackgroundlistener
    self.outputfunc = outputfunc
    self.outputasync = outputasync

class InputMode(Enum):
  VOICE = "v"
  TEXT_BOX = "t"
  NONE = None

class RunningMode(Enum):
  SYNC = "sync"
  ASYNC = "async"

class JarvisApp:
  def __init__(self, appinfo = None, includePersonalInfo = True, openai_key = None, sampleCount = 20, minSimilarity = 0.5, memory_retention_time = 900, personality = personalities.JARVIS, maxhistorylength = 10, temperature = 0.5, inbuiltbackgroundlistener = InputMode.VOICE, outputfunc = voicebox.say, outputasync = True, speechHotkey = "alt+j", maxretries = 4):
    
    self.appinfo = appinfo
    self.includePersonalInfo = includePersonalInfo
    self.openai_key = openai_key
    info = self.genInfo()

    self.configFilePaths()
    self.configAPIkey()
    
    voicebox.HOTKEY = speechHotkey

    functions, readables = self.getFunctions()

    self.chosenchatbot = chatbot.ChatBot(functions = functions, readables = readables, info = info, sampleCount = sampleCount, minSimilarity = minSimilarity, personality = personality, maxhistorylength = maxhistorylength, temperature = temperature)
    self.memory_retention_time = memory_retention_time
    self.personality = personality
    self.inbuiltbackgroundlistener = inbuiltbackgroundlistener
    self.outputfunc = outputfunc
    self.outputasync = outputasync
    self.runningmode = RunningMode.SYNC
    self.maxretries = maxretries
  
  def startInbuiltVoiceListener(self, hotkey = "alt+j"):
    try:
      keyboard.clear_all_hotkeys()
    except AttributeError:
      pass
    self.initiateVoiceListener()
    keyboard.add_hotkey(hotkey, lambda: self.startRecording())
    keyboard.on_release_key(hotkey.split("+")[-1], lambda event: self.stopRecording())
  
  def startInbuiltTextboxListener(self):
    voicebox.startTextboxListener()

  def initiateVoiceListener(self):
    voicebox.initiateVoiceListener()

  def startRecording(self):
    if not voicebox.listening:
      voicebox.startRecording()

  def stopRecording(self):
    if voicebox.listening:
      voicebox.stopRecording()
  
  def getFunctions(self):
    self.function_module_relationship = []
    allvariables = []
    modulevariables = []

    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame)

    runnables = allrunnables
    readables = allreadables
    
    for functype in [runnables, readables]:
      out = []
      for function in functype:
        func = function.func
        if getattr(function, "priority", False):
          priority = True
        else:
          priority = False
        out.append([func, getFullDoc(func), priority])

      funced = []
      for func in out:
        funced.append(chatbot.Function(*func))
      for func in funced:
        self.function_module_relationship.append([func, module])
      modulevariables.append(funced)
    
    allvariables.append(modulevariables)
    
    functions = []
    readables = []
    for modulefuncs in allvariables:
      modulefunctions = modulefuncs[0]
      modulereadables = modulefuncs[1]
      for i in modulefunctions:
        functions.append(i)
      for i in modulereadables:
        readables.append(i)
    
    return functions, readables

  def configAPIkey(self):
    if self.openai_key:
      chatbot.apikey = self.openai_key
    else:
      apikey = config.loadApiKey()
      if not(apikey):
        raise KeyError("You need to configure an API key to use this app!")
      chatbot.apikey = apikey

  def configFilePaths(self):
    if not(os.path.isdir(FILEPATH)):
      os.mkdir(FILEPATH)
    
    try:
      shutil.rmtree(FILEPATH+"streamedFileOutput")
    except FileNotFoundError:
      pass
    os.mkdir(FILEPATH+"streamedFileOutput")

    makeHidden(FILEPATH)
    if not(os.path.isdir(FILEPATH)):
      os.mkdir(FILEPATH)
      makeHidden(FILEPATH)

  def genInfo(self):
    allinfo = []
    if self.includePersonalInfo and config.loadPersonalInfo() != None:
      allinfo.append("Personal info:\n" + str(config.loadPersonalInfo()))
    if self.appinfo != None:
      allinfo.append("App info:\n" + self.appinfo)
    if allinfo == []:
      allinfo = ["None"]
    info = "\n".join(allinfo)
    return info

  def update(self):
    self.startWaitingTime = time.time()
    self.runProcess()
  
  def runProcess(self):
    qText = checkRequestQueue()
    if qText == None:
      return
    timeTaken = time.time()-self.startWaitingTime
    self.startWaitingTime = time.time()
    if timeTaken > self.memory_retention_time:
      print("Breaking conversation.")
      self.chosenchatbot.breakConversation()

    self.personalityimplemented = False
    try:
        sig = inspect.signature(self.outputfunc)
        if "personality" in sig.parameters:
            self.personalityimplemented = True
    except ValueError:
        pass
    
    self.createQuery(qText)

    #voicebox.say(ans1, mode = outputfunc, personality = personality)
  
  def createQuery(self, string):
    thingtorun = self.chosenchatbot.query(string)
    print(thingtorun)
    failed = True
    attempts = 0
    lastSuccessfulRequestIndex = len(self.chosenchatbot.q_and_a_history)
    failedAtAnyPoint = False
    while attempts <= self.maxretries and failed:
      try:
        self.sendAndReceive(thingtorun, self.runningmode, self.chosenchatbot)
        failed = False
      except Exception as e:
        if isinstance(e, JarvisBecameEvilError):
          raise
        error = findError.calcException(e, thingtorun)
        linefailed = error[0]
        tb_str = error[1]
        linefailederror = error[2]
        failed = True
        failedAtAnyPoint = True
      self.chosenchatbot.addQuestion(string)
      self.chosenchatbot.addAnswer(thingtorun)
      if failed:
        answer = self.chosenchatbot.q_and_a_history[-1]
        answer = answer.split("\n")
        answer[linefailed-1] += f" # <----- THIS RAISES AN ERROR! FIX THIS! {linefailederror}"
        answer = "\n".join(answer)
        self.chosenchatbot.q_and_a_history[-1] = answer
        self.chosenchatbot.addQuestion(utils.loadPrompt("failure.txt", mode = "text").format(error=tb_str))
        if linefailederror.startswith("SyntaxError"):
          self.chosenchatbot.addQuestion(utils.loadPrompt("SyntaxFailure.txt", mode = "text"))
        thingtorun = self.chosenchatbot.query(string)
        print(thingtorun)
      attempts += 1
    if failedAtAnyPoint:
      del self.chosenchatbot.q_and_a_history[lastSuccessfulRequestIndex+1:-1]

  def C_say(self, string, variablestoadd = []):
    return customfunctions.C_say(string, self.outputasync, self.personalityimplemented, self.outputfunc, self.personality, variablestoadd)

  def C_choose(self, list_or_dict, prompt, list_description, multiple = False):
    return customfunctions.C_choose(list_or_dict, prompt, list_description, multiple)

  def runCode(self, thingtorun, chatbot: chatbot.ChatBot):
    readables = chatbot.readables
    functions = chatbot.functions

    globalsforrunning = {"C_say": self.C_say, "C_choose": self.C_choose}

    for funcset, functype in [(readables, "R"), (functions, "F")]:
      for func in funcset:
        globalsforrunning[functype + "_" + func.function] = func.truefunction
    
    detector = codechecker.DangerousCodeDetector()
    safe = detector.check(thingtorun)
    if not(safe[0]):
      raise JarvisBecameEvilError(f"{safe[1]} in code '{thingtorun}'")
    
    exec(thingtorun, globalsforrunning)
  
  def sendAndReceive(self, thingtorun, runningmode, chatbot):
    if runningmode == RunningMode.SYNC:
      result = self.runCode(thingtorun, chatbot)
    
    return result

def priority(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  wrapper.priority = True
  wrapper.func = func

  return wrapper

def runnable(func):
  global allrunnables

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  wrapper.runnable = True
  wrapper.func = func
  allrunnables.append(wrapper)
  return wrapper

def readable(func):
  global allreadables

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  wrapper.readable = True
  wrapper.func = func
  allreadables.append(wrapper)
  return wrapper

def addReadables(*funcs):
  for func in funcs:
    readable(func)

def addRunnables(*funcs):
  for func in funcs:
    runnable(func)

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
          result = "Operation failed: " + str(e)
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

def init_main(scope: Union[str, List[str]] = "/", info = None, openai_key = None, sampleCount = 10, minSimilarity = 0.65, memory_retention_time = 900, personality = personalities.JARVIS, maxhistorylength = 10, temperature = 0.5, inbuiltbackgroundlistener = InputMode.VOICE, outputfunc = voicebox.say, outputasync = True, runningmode = RunningMode.SYNC, speechHotkey = "alt+j"):
  if type(scope) == str:
    scope = [scope]

  if not(os.path.isdir(FILEPATH)):
    os.mkdir(FILEPATH)
  
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

  frame = inspect.currentframe().f_back
  filename = inspect.getframeinfo(frame)[0]
  dirname = os.path.dirname(filename)

  allaccessible = []
  for item in scope:
    item = item.rstrip("/").rstrip("\\").lstrip("/").lstrip("\\")
    joinedItemName = os.path.join(dirname, item)
    if os.path.isdir(joinedItemName):
      onlyfiles = [os.path.join(joinedItemName, f).replace("/", "\\") for f in listdir(joinedItemName) if isfile(join(joinedItemName, f)) and os.path.splitext(f)[1] == ".py"]
      if filename.replace("/", "\\") in onlyfiles:
        onlyfiles.remove(filename.replace("/", "\\"))
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

  if runningmode == RunningMode.ASYNC:
    processes = []
    for file in accessablefiles:
      processes.append(subprocess.Popen([sys.executable, file, "-JarvisSubprocess"], stdin=PIPE, stdout=PIPE, universal_newlines=True))

    allvariables = []
    function_process_relationship = []
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
              function_process_relationship.append([func, p])
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
    
    chosenchatbot = chatbot.ChatBot(functions = functions, readables = readables, info = info, sampleCount = sampleCount, minSimilarity = minSimilarity, personality = personality, maxhistorylength = maxhistorylength, temperature = temperature)


    startStreamingOutput()

    if inbuiltbackgroundlistener == InputMode.TEXT_BOX:
      voicebox.startTextboxListener()
    elif inbuiltbackgroundlistener == InputMode.VOICE:
      startInbuiltVoiceListener(hotkey = speechHotkey)

    #runProcessMainloop(chosenchatbot, function_process_relationship, memory_retention_time, personality, inbuiltbackgroundlistener, outputfunc, outputasync, runningmode=runningmode)
  
  elif runningmode == RunningMode.SYNC:
    function_module_relationship = []
    allvariables = []

    for index, file in enumerate(accessablefiles):
      modulevariables = []
      spec = importlib.util.spec_from_file_location(f"module.name{index}", file)
      module = importlib.util.module_from_spec(spec)
      sys.modules[f"module.name{index}"] = module
      spec.loader.exec_module(module)

      functions = [getattr(module, a) for a in dir(module) if isinstance(getattr(module, a), types.FunctionType)]
      readables = []
      runnables = []
      for item in functions:
        if getattr(item, "runnable", False):
          runnables.append(item)
        if getattr(item, "readable", False):
          readables.append(item)
      
      for functype in [runnables, readables]:
        out = []
        for function in functype:
          func = function.func
          if getattr(function, "priority", False):
            priority = True
          else:
            priority = False
          out.append([func, getFullDoc(func), priority])

        funced = []
        for func in out:
          funced.append(chatbot.Function(*func))
        for func in funced:
          function_module_relationship.append([func, module])
        modulevariables.append(funced)
      
      allvariables.append(modulevariables)
    
    functions = []
    readables = []
    for modulefuncs in allvariables:
      modulefunctions = modulefuncs[0]
      modulereadables = modulefuncs[1]
      for i in modulefunctions:
        functions.append(i)
      for i in modulereadables:
        readables.append(i)
    
    chosenchatbot = chatbot.ChatBot(functions = functions, readables = readables, info = info, sampleCount = sampleCount, minSimilarity = minSimilarity, personality = personality, maxhistorylength = maxhistorylength, temperature = temperature)

    if inbuiltbackgroundlistener == InputMode.TEXT_BOX:
      voicebox.startTextboxListener()
    elif inbuiltbackgroundlistener == InputMode.VOICE:
      startInbuiltVoiceListener(hotkey = speechHotkey)

    #runProcessMainloop(chosenchatbot, function_module_relationship, memory_retention_time, personality, inbuiltbackgroundlistener, outputfunc, outputasync, runningmode=runningmode)

  
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

def submitRequest(request: str):
  global requestQueue
  requestQueue.append(request)

def checkRequestQueue():
  global requestQueue
  if requestQueue == []:
    return None
  else:
    return requestQueue.pop(0)

def runnableHiddenDecorator(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  return wrapper

def readableHiddenDecorator(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  return wrapper

def listenForRunCommand():
  global opqueue
  while True:
    try:
      x = input()
      opqueue.append(x)
    except EOFError as e:
      pass

def init():
  runnables = allrunnables
  readables = allreadables


  displayFunctions(runnables)
  displayFunctions(readables)
  
  thread = threading.Thread(target=listenForRunCommand)
  thread.start()

def getFullDoc(my_function):
  try:
    function_signature = inspect.signature(my_function)
    function_definition = f"{my_function.__name__}{function_signature}"
    docstring_with_definition = f"{function_definition}\n{my_function.__doc__ if my_function.__doc__ else ''}"
    return docstring_with_definition
  except:
    return my_function.__doc__

def displayFunctions(functions):
  out = []
  for function in functions:
    func = function.func
    if getattr(function, "priority", False):
      priority = True
    else:
      priority = False
    out.append([func, getFullDoc(func), priority])
  print(UNLIKELYNAMESPACECOLLIDABLE + str(out))
  sys.stdout.flush()
  
  
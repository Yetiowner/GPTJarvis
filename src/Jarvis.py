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
import functools
import importlib.util
import sys
from enum import Enum

#TODO: add long term memory
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

class VoiceMode(Enum):
  TEXT2TEXT = "T2T"
  SPEECH2SPEECH = "S2S"
  TEXT2SPEECH = "T2S"
  SPEECH2TEXT = "S2T"

class SyncMode(Enum):
  SYNC = "s"
  ASYNC = "a"

def priority(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  wrapper.priority = True
  wrapper.func = func

  return wrapper

def runnable(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
  
  wrapper.runnable = True
  wrapper.func = func
  return wrapper

def readable(func):
  @functools.wraps(func)
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

def init_main(scope: Union[str, List[str]] = "/", info = None, openai_key = None, sampleCount = 3, minSimilarity = 0.65, memory_retention_time = 900, personality = personalities.JARVIS, maxhistorylength = 3, temperature = 0.5, mode = VoiceMode.SPEECH2SPEECH, syncmode = SyncMode.SYNC, speechHotkey = "alt+j"):
  if type(scope) == str:
    scope = [scope]

  if not(os.path.isdir(FILEPATH)):
    os.mkdir(FILEPATH)

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
  
  voicebox.HOTKEY = speechHotkey

  if syncmode == SyncMode.ASYNC:
    processes = []
    for file in accessablefiles:
      processes.append(subprocess.Popen([sys.executable, file, "-JarvisSubprocess"], stdin=PIPE, stdout=PIPE, universal_newlines=True))

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
    
    chosenchatbot = chatbot.ChatBot(functions = functions, readables = readables, info = info, sampleCount = sampleCount, minSimilarity = minSimilarity, personality = personality, maxhistorylength = maxhistorylength, temperature = temperature)


    startStreamingOutput()

    runProcessMainloop(chosenchatbot, functon_process_relationship, memory_retention_time, personality, mode, syncmode=syncmode)
  
  else:
    functon_module_relationship = []
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
          out.append([func.__name__, inspect.getfullargspec(func).args, {}, {i: j.__name__ for i, j in get_type_hints(func).items()}, func.__doc__, priority])

        funced = []
        for func in out:
          funced.append(chatbot.Function(*func))
        for func in funced:
          functon_module_relationship.append([func, module])
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

    runProcessMainloop(chosenchatbot, functon_module_relationship, memory_retention_time, personality, mode, syncmode=syncmode)
    


  
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

def runProcessMainloop(chosenchatbot: chatbot.ChatBot, functon_process_relationship, memory_retention_time, personality, mode: VoiceMode, syncmode=SyncMode.SYNC):
  mode = mode.value
  inmode = mode[0]
  outmode = mode[2]
  print("Ready")
  while True:
    startWaitingTime = time.time()
    qText = voicebox.listen(mode = inmode)
    timeTaken = time.time()-startWaitingTime
    if timeTaken > memory_retention_time:
      print("Breaking conversation.")
      chosenchatbot.breakConversation()
    ans1 = createQuery(qText, chosenchatbot, functon_process_relationship, syncmode)
    voicebox.say(ans1, mode = outmode, personality = personality)
  
  
def createQuery(string, chosenchatbot: chatbot.ChatBot, functon_process_relationship, syncmode):
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

    output = sendAndReceiveFromFunction(chosenprocess, thingtorun, syncmode)

    if result[0].mode == "R":
      explainedOutput = f"Your response: {result[0].mode} {thingtorun} \n\nResult: {output if len(output) < 100 else 'Truncated as too long'}"
      explainedOutputFull = f"Your response: {result[0].mode} {thingtorun} \n\nResult: {output}"

      chosenchatbot.register_addInfo(explainedOutput)
      chosenchatbot.addInfo()

      chosenchatbot.register_addHistory(explainedOutput)
      textResult = chosenchatbot.followThroughInformation(explainedOutputFull + f" Where {result[0].showFunction()}", string)
      chosenchatbot.register_addHistory(f"You: {textResult}")
      chosenchatbot.addHistory()
      return textResult

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


def sendAndReceiveFromFunction(chosenprocess, thingtorun, syncmode):
  if syncmode == SyncMode.ASYNC:
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
  else:
    try:
      localscopy = locals()
      result = eval(f"chosenprocess.{thingtorun}", localscopy)
      if result == None:
        result = "Success!"
    except Exception as e:
      result = str(e)
    output = result
  return output

def listenForRunCommand():
  global opqueue
  while True:
    try:
      x = input()
      opqueue.append(x)
    except EOFError as e:
      pass

def init():
  frame = inspect.stack()[1]
  module = inspect.getmodule(frame[0])
  if "-JarvisSubprocess" not in sys.argv:
    #return
    pass
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
    if getattr(function, "priority", False):
      priority = True
    else:
      priority = False
    out.append([func.__name__, inspect.getfullargspec(func).args, {}, {i: j.__name__ for i, j in get_type_hints(func).items()}, func.__doc__, priority])
  print(UNLIKELYNAMESPACECOLLIDABLE + str(out))
  sys.stdout.flush()
  
  
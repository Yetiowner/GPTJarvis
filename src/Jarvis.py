from typing import get_type_hints
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


functionlist = []
opqueue = []


def runnable(func):
  def wrapper(*args, **kwargs):
    func(*args, **kwargs)
  
  wrapper.runnable = True
  wrapper.func = func
  return wrapper

def readable(func):
  def wrapper(*args, **kwargs):
    func(*args, **kwargs)
  
  wrapper.readable = True
  wrapper.func = func
  return wrapper

def update():
  global opqueue
  if opqueue != []:
    op = opqueue.pop()
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    attrs = module.__dict__
    filename = f"streamedFileOutput/{os.path.basename(module.__file__)}.txt"

    with open(filename, "a") as file:
      with redirect_stdout(file):
        exec(op, attrs)
  

def init_main(scope="folder"):
  from GPTJarvis.src import chatbot
  
  chatbot.loadApiKeyFromFile("secret.txt") # TODO delete when publish

  shutil.rmtree("streamedFileOutput")
  os.mkdir("streamedFileOutput")

  #init_browser()
  if scope == "folder":
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    filename = module.__file__
    dirname = os.path.dirname(filename)
    onlyfiles = [dirname + ("\\" if "\\" in filename else "/") + f for f in listdir(dirname) if isfile(join(dirname, f)) and os.path.splitext(f)[1] == ".py"]
    onlyfiles.remove(filename)
    accessablefiles = onlyfiles
  else:
    accessablefiles = scope
  print(accessablefiles)
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
        funced = [chatbot.Function(*evalledfunc) for evalledfunc in evalled]
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
  
  chosenchatbot = chatbot.ChatBot(functions, readables)
  chatbot.init_browser()

  startStreamingOutput()

  runProcessMainloop(chosenchatbot, functon_process_relationship, processes)
  

def startStreamingOutput():
  thread = threading.Thread(target=streamOutput)
  thread.start()

def streamOutput():
  lastfilename = None
  mypath = "streamedFileOutput"
  linereached = {}
  while True:
    onlyfiles = ["streamedFileOutput" + "/" + f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in onlyfiles:
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

def runProcessMainloop(chosenchatbot, functon_process_relationship, processes):
  createQuery("detonate the mark 32", chosenchatbot, functon_process_relationship, processes)
  #createQuery("build the mark 32", chosenchatbot, functon_process_relationship, processes)
  createQuery("what is the weather?", chosenchatbot, functon_process_relationship, processes)
  
  
def createQuery(string, chosenchatbot, functon_process_relationship, processes):
  result = chosenchatbot.query(string)
  for function in functon_process_relationship:
    if function[0] == result[0]:
      chosenprocess = function[1]
  
  thingtorun = result[1]

  chosenprocess.stdin.write(thingtorun)
  #print(chosenprocess)
  #print(thingtorun)

def listenForRunCommand():
  global opqueue
  while True:
    try:
      x = input()
      opqueue.append(x)
    except EOFError:
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
  
  
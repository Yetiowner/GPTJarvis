from GPTJarvis.src.chatbot import *
from typing import get_type_hints
import inspect
import os
from os import listdir
from os.path import isfile, join
import subprocess
from subprocess import PIPE
import sys
import time

apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish

functionlist = []


def runnable(func):
  def wrapper(*args, **kwargs):
    func(*args, **kwargs)
  
  wrapper.runnable = True
  return wrapper

def readable(func):
  def wrapper(*args, **kwargs):
    func(*args, **kwargs)
  
  wrapper.readable = True
  return wrapper

def update():
  pass
  

def init_main(scope="folder"):
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
    processes.append(subprocess.Popen([sys.executable, file], stdin=PIPE, stdout=PIPE))
  
  #chatbot = ChatBot([APIStackOverFlow, APIWikipedia, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation], functionlist)
  print("asdf")
  print("asdf1")
  for p in processes:
    print("asdf2")
    p.stdin.write(b"f")
    runnables = p.stdout.readline()
    #readables = p.stdout.readline()
    print(runnables)
    print(readables)

def init():
  x = input() # wait for confirmation
  with open("filetext.txt", "w") as file:
    file.write("got this far")
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
  with open("filetext.txt", "w") as file:
    file.write(str(x))
  print(runnables)
  print(readables)


  
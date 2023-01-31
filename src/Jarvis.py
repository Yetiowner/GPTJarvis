from GPTJarvis.src.chatbot import *
from typing import get_type_hints
import inspect
import os
from os import listdir
from os.path import isfile, join
import subprocess
import sys

apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish

functionlist = []

def runnable(func):
  pass

def update():
  frame = inspect.stack()[1]
  module = inspect.getmodule(frame[0])
  

def init(scope="folder"):
  print("asaaaaa")
  if scope == "folder":
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    filename = module.__file__
    dirname = os.path.dirname(filename)
    onlyfiles = [dirname + "/" + f for f in listdir(dirname) if isfile(join(dirname, f))]
    print(filename)
    print(onlyfiles)
    onlyfiles.remove(filename)
    accessablefiles = onlyfiles
  else:
    accessablefiles = scope
  for file in accessablefiles:
    subprocess.Popen([sys.executable, file])
  chatbot = ChatBot([APIStackOverFlow, APIWikipedia, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation], functionlist)


  
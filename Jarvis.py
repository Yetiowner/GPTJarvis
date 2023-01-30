from chatbot import *
from typing import get_type_hints

apikey = None
loadApiKeyFromFile("secret.txt") # TODO delete when publish

functionlist = []

def runnable(func):
  def wrapper(*args, **kwargs):
    global functionlist
    print("asdf")
    functionlist.append(Function(func, args, kwargs, get_type_hints(func), func.__doc__))
  return wrapper

def query(prompt):
  return chatbot.query(prompt)

def init():
  global chatbot
  print(functionlist)
  
  chatbot = ChatBot([APIStackOverFlow, APIWikipedia, APIDateTime, APIMaths, APIWeather, APIExchangeRate, APIIPFinder, APILocation], functionlist)

  
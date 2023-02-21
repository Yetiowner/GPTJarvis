import time
from GPTJarvis import Jarvis
import wolframalpha
import json
import json


with open("keys.json", "r") as file:
    app_id = json.load(file)["WolframAlpha"]
client = wolframalpha.Client(app_id)


@Jarvis.runnable
def sayHelloWorld():
  """Prints out hello world"""
  print("Hello world!")

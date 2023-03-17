import json

class Personality():
  def __init__(self, prompt, jsontext) -> None:
    self.prompt = prompt
    self.voice = jsontext["voice"]
    self.pitch = jsontext["pitch"]
    self.speed = jsontext["speed"]

def loadPersonality(name):
  with open(f"src/personalities_list/{name}/Prompt.txt") as file:
    prompt = file.read()
  with open(f"src/personalities_list/{name}/voice.json") as file:
    jsontext = json.load(file)
  
  return Personality(prompt, jsontext)

JARVIS = loadPersonality("Jarvis")
FRIDAY = loadPersonality("Friday")
NONE = loadPersonality("None")
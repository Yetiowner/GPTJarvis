class Personality():
  def __init__(self, prompt) -> None:
    self.prompt = prompt
    #print(self.prompt)

def loadPersonality(name):
  with open(f"src/personalities_list/{name}/Prompt.txt") as file:
    prompt = file.read()
  return Personality(prompt)

JARVIS = loadPersonality("Jarvis")
FRIDAY = loadPersonality("Friday")
ULTRON = loadPersonality("Ultron")
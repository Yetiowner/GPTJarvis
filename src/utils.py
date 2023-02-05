def loadPrompt(promptname):
  with open(f"prompts/{promptname}", "r") as file:
    return file.read()
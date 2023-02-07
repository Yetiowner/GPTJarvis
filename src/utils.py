import pathlib

def loadPrompt(promptname):
  resolvedpath = str(pathlib.Path().parent.absolute().parent.absolute())
  if "/" in resolvedpath:
    joiner = "/"
  else:
    joiner = "\\"
  with open(f"{resolvedpath}{joiner}prompts{joiner}{promptname}", "r") as file:
    return file.read()
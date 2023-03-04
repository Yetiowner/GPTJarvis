import pathlib

def loadPrompt(promptname, mode = "list"):
  resolvedpath = str(pathlib.Path().parent.absolute())#.parent.absolute())
  if "/" in resolvedpath:
    joiner = "/"
  else:
    joiner = "\\"
  with open(f"{resolvedpath}{joiner}prompts{joiner}{promptname}", "r") as file:
    textinfo = file.read()
  if mode == "text":
    return textinfo
  text = textinfo.split("---------------------------")
  text.pop(0)
  newtext = []
  for textitem in text:
    tags = textitem.split("\n")[0]
    rest = "\n".join(textitem.split("\n")[1:])
    tags = tags.split(",")
    dictobj = {}
    dictobj["role"] = tags[0]
    if len(tags) > 1:
      dictobj["name"] = tags[1]
    dictobj["content"] = rest
    newtext.append(dictobj)
  return newtext
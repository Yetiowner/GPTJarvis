from GPTJarvis.src.utils import loadPrompt
import openai
import threading
import copy
import ast

"""If you need to say something, use the C_say(string, variablestoadd = []) function. The string is said, and if it contains a curly bracket it should be formatted using the variablestoadd argument which should be filled in with variables in order
If you have values in a form that cannot be used in a calculation, and need to extract information from it, e.g. an integer from a string, or a boolean from a string, use the function C_interpret(question, arguments, description, returns), where question is the thing query to interpret, e.g. "is the sentiment positive or negative", arguments is a list of inputs that need to be interpretted, description describes the arguments, and returns describes the data-type to return.
If you have values in a form that won't be easy to C_say, then use C_describe(data, method), which returns a string describing the datatype, in the form described by method, e.g. "Describe the items one by one"
If you have a list or dictionary of values and want to find the closest one to your choice, use C_choose(list_or_dict, prompt), which returns the index or key that closest mathes the prompt from the list. The list should not be shortened before hand, so don't try to filter it before this step. This step is the only filtering step needed. The prompt should be a description of the object in the list to find. E.g. "Object which has a 3 in it". Use this if you are searching for something, do NOT try and apply a filter to the list before hand."""

MODEL = "gpt-3.5-turbo"

describePrompt = loadPrompt("describe.txt")
sayPrompt = loadPrompt("say.txt")
#interpretPrompt = loadPrompt("interpret.txt")
choosePrompt = loadPrompt("choose.txt")

def list2dict(listobj):
  if type(listobj) == dict:
    return listobj
  out = {}
  for index, i in enumerate(listobj):
    out[index] = i
  return out

def getResponse(prompt):
  print(threading.enumerate())
  print(1)
  response = openai.ChatCompletion.create(
  model=MODEL,
  messages=prompt,
  temperature=0.5,
  max_tokens=512,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
  )
  print(2)
  response = response["choices"][0]["message"]["content"].lstrip().rstrip()
  return response

def C_describe(dataToDescribe, method):
  prompt = copy.deepcopy(describePrompt)
  prompt[-1]["content"] = prompt[-1]["content"].format(dataToDescribe=dataToDescribe, method=method)
  response = getResponse(prompt)
  return response

def C_say(string, outputasync, personalityimplemented, outputfunc, personality, variablestoadd = []):
  if variablestoadd == []:
    outtext = string
  else:
    formattedstring = string.format(*variablestoadd)
    """prompt = copy.deepcopy(sayPrompt)
    prompt[-1]["content"] = prompt[-1]["content"].format(string=formattedstring)
    response = getResponse(prompt)
    outtext = response"""
    outtext = formattedstring


  if outputasync:
    if personalityimplemented:
      thread = threading.Thread(target=outputfunc, args=(outtext,), kwargs={"personality": personality})
      thread.start()
    else:
      thread = threading.Thread(target=outputfunc, args=(outtext,))
      thread.start()
  else:
    if personalityimplemented:
      outputfunc(outtext, personality = personality)
    else:
      outputfunc(outtext)
  print(string, variablestoadd)

def C_interpret(question, arguments, description, returns):
  pass

def C_choose(list_or_dict, chooseprompt, list_description):
  list_or_dict = list2dict(list_or_dict)
  print(list_or_dict)
  prompt = copy.deepcopy(choosePrompt)
  prompt[-1]["content"] = prompt[-1]["content"].format(list_or_dict=list_or_dict, prompt=chooseprompt, list_description=list_description)
  response = getResponse(prompt)
  print(response, "foo")
  response = ast.literal_eval(response)
  return response
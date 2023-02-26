import os
import json

configfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Personal info")
if not(os.path.isdir(configfolder)):
    os.mkdir(configfolder)

configfile = os.path.join(configfolder, "personal_info.json")
if not(os.path.isfile(configfile)):
    with open(configfile, 'w') as file:
        file.write("{}")

def loadApiKeyFromFile(openai_key_path):
    with open(openai_key_path, "r") as f:
        apikey = f.read()
    setKey(apikey)

def loadInfoFromFile(info_path):
    with open(info_path, "r") as f:
        info = f.read()
    setPersonalInfo(info)

def setKey(key):
    with open(configfile, "r") as file:
        jsonobj = json.load(file)
    jsonobj['OPENAI_KEY'] = key
    with open(configfile, "w") as file:
        json.dump(jsonobj, file)

def setPersonalInfo(info):
    with open(configfile, "r") as file:
        jsonobj = json.load(file)
    jsonobj['JARVIS_PERSONAL_INFO'] = info
    with open(configfile, "w") as file:
        json.dump(jsonobj, file)

def loadPersonalInfo():
    with open(configfile, "r") as file:
        jsonobj = json.load(file)
    try:
        return jsonobj['JARVIS_PERSONAL_INFO']
    except KeyError:
        return None

def loadApiKey():
    with open(configfile, "r") as file:
        jsonobj = json.load(file)
    try:
        return jsonobj['OPENAI_KEY']
    except KeyError:
        return None
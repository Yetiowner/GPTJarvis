import time
from GPTJarvis import Jarvis
from datetime import datetime
import wolframalpha
import json
import os
from openmeteo_py import Hourly,Daily,Options,OWmanager
import pathlib
import jellyfish
import glob
from serpapi import GoogleSearch
import json
from contextlib import redirect_stdout
import tkinter as tk


with open("keys.json", "r") as file:
    app_id = json.load(file)["WolframAlpha"]
client = wolframalpha.Client(app_id)

@Jarvis.readable
def doMaths(mathsExpr):
    """Function that takes in a maths expression of type string and returns the solution of the maths problem."""
    res = client.query(mathsExpr)
    answer = "\n".join([i.text for i in res.results])
    return answer

@Jarvis.runnable
def explodeSuit(suit_number: int):
    """Detonates suit. @param suit_number: int representing suit number, or "mark" number. Synonyms: Destroy suit, blow suit, deactivate suit."""
    print(f"{suit_number} goes boom!")

@Jarvis.runnable
def buildSuit(suit_number: int):
    """Creates and builds suit. @param suit_number: int representing suit number, or "mark" number. Synonyms: Start up suit, create suit"""
    print(f"Created suit number {suit_number}!")

@Jarvis.readable
def getTemperatureOfSuit(suit_number: int):
    """Returns the temperature at the given suit. @param suit_number: int representing suit number, or "mark" number. Returns suit temperature in celsius"""
    return 3*suit_number

@Jarvis.readable
def getTimeAndDate():
    """Returns the current time and date as a string"""
    now = datetime.now()
    return now.strftime("%m/%d/%Y, %H:%M:%S %A")

def foo(a):
    """Bar"""
    return "baz"

@Jarvis.runnable
def sayHelloWorld():
  """Prints out hello world"""
  print("Hello world!")

@Jarvis.readable
def getWeather(latitude, longitude):
    """Returns the current weather as a string. Synonyms: temperature"""

    daily = Daily()
    options = Options(latitude, longitude, current_weather=True)

    mgr = OWmanager(options,
        None,
        daily.all())


    # Download data
    meteo = mgr.get_data()

    code = meteo["daily"]["weathercode"][0]
    temp = (meteo["daily"]["temperature_2m_max"][0]+meteo["daily"]["temperature_2m_min"][0])/2
    unitfortemp = meteo["daily_units"]["temperature_2m_max"]
    codes = {0: "Clear sky", 1: "Mainly clear", 2: "Partially cloudy", 3: "Overcast", 45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain", 71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with light hail", 99: "Thunderstorm with heavy hail"}
    return f"Condition: {codes[code]}, Temperature {temp:.1f}{unitfortemp}"


@Jarvis.runnable
def startProgram(program_name):
    """Starts up the app of choice. Synonyms: Run, start"""
    path = pathlib.Path.home() / 'Desktop'
    path1 = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    results = find_files(program_name, path)
    results1 = find_files(program_name, path1)
    newresults = results
    for result in results1:
        newresults.append(result)
    

    sortedresults = sorted(newresults, key = lambda x: x[1])
    sortedresults = sortedresults[-1]
    thresh = 0.8
    if sortedresults[1] < thresh:
        raise FileNotFoundError
    
    os.startfile(sortedresults[0])
    

def find_files(filename, search_path):
    types = ['*.lnk', '*.url'] # the tuple of file types
    results = []
    for files in types:
        results.extend(y for x in os.walk(search_path) for y in glob.glob(os.path.join(x[0], files)))

    results = [[f, jellyfish.jaro_distance(os.path.splitext(os.path.basename(f))[0], filename)] for f in results]
    return results

@Jarvis.priority
@Jarvis.readable
def googleSearch(string: str):
    """Searches the string on google, and returns the first result as a string. Use this if you want to look up information on the internet, or if I ask you for information that can be looked up."""
    with open("keys.json", "r") as file:
        keys = json.load(file)
    params = {
      "api_key": keys["Google"],
      "engine": "google",
      "q": string,
      "hl": "en",
    }
    search = GoogleSearch(params)
    
    with redirect_stdout(None):
        results = search.get_dict()
    return "\n".join([results['organic_results'][i]['snippet'] for i in range(3)])

@Jarvis.readable
def getHeightOfUserInCentimetres():
  """Returns user's height in centimetres"""
  global heightvar
  global root
  global val
  #Note: input() does not work with Jarvis

  root=tk.Tk()
  heightvar=tk.StringVar()
  label = tk.Label(root, text="Enter your height in centimetres:")
  label.pack(padx=10, pady=10)
  entry = tk.Entry(root, textvariable=heightvar)
  entry.pack(padx=10, pady=10)
  submitbutton = tk.Button(root, command=submit, text="Submit")
  submitbutton.pack(padx=10, pady=10)

  val = None

  while val == None:
    root.update()

  return val

def submit():
  global val

  val = heightvar.get()
    
  root.destroy()

Jarvis.init()
while True:
  Jarvis.update()
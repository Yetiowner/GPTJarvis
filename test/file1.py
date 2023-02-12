import time
import GPTJarvis.src.Jarvis as Jarvis
from datetime import datetime

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
    return now.strftime("%m/%d/%Y, %H:%M:%S")

def foo(a):
    """Bar"""
    return "baz"

Jarvis.init()
while True:
    Jarvis.update()

import time
import GPTJarvis.src.Jarvis as Jarvis

@Jarvis.runnable
def explodeSuit(suit_number: int):
    """Detonates suit. @param suit_number: int representing suit number"""
    print(f"{suit_number} goes boom!")

@Jarvis.runnable
def buildSuit(suit_number: int):
    """Creates and builds suit. @param suit_number: int representing suit number"""
    print(f"Created suit number {suit_number}!")

@Jarvis.readable
def getTemperatureOfSuit(suit_number: int):
    """Returns the temperature at the given suit. @param suit_number: int representing suit number. Returns suit temperature in celsius"""
    return 3*suit_number

def foo(a):
    """Bar"""
    return "baz"

Jarvis.init()
while True:
    Jarvis.update()

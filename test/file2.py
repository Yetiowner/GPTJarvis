import time
import GPTJarvis.src.Jarvis as Jarvis


@Jarvis.runnable
def setWeather(weather):
    """Sets the current weather. @param weather: string describing weather"""
    print(f"Weather set to {weather}")


@Jarvis.readable
def getWeather():
    """Returns the current weather"""
    return "sunny"

def foo(a):
    """Bar"""
    return "baz"

Jarvis.init()
while True:
    Jarvis.update()

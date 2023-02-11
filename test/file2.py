import time
import GPTJarvis.src.Jarvis as Jarvis

globalweather = "sunny"

@Jarvis.runnable
def setWeather(weather):
    """Sets the current weather. @param weather: string describing weather"""
    global globalweather
    globalweather = weather
    print(f"Weather set to {weather}")


@Jarvis.readable
def getWeather():
    """Returns the current weather as a string"""
    return globalweather

def foo(a):
    """Bar"""
    return "baz"

Jarvis.init()
while True:
    Jarvis.update()

from GPTJarvis import Jarvis

@Jarvis.runnable
def sayHelloWorld():
  """Prints out hello world"""
  print("Hello world!")

Jarvis.init()
while True:
  Jarvis.update()
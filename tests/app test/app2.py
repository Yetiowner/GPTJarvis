import math
from GPTJarvis import Jarvis, personalities

Jarvis.addReadables(math.sin, math.cos, math.tan, math.sqrt, math.log, math.sinh, math.tanh, math.cosh, math.asin, math.acos, math.atan, math.acosh, math.asinh, math.atanh, math.degrees, math.radians)

app = Jarvis.init_app(
  appinfo = "This app does maths.",
  personality = personalities.JARVIS, 
  openai_key = None,
  temperature = 0.6,
  minSimilarity = 0.65,
  backgroundlistener = Jarvis.InputMode.TEXT_BOX
)

while True:
  Jarvis.update_app(app)
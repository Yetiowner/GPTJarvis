from GPTJarvis import Jarvis, personalities
Jarvis.init_main(
  scope = ["/", "../test2/file3.py", "../test3"],
  info = Jarvis.loadInfoFromFile("aditionalInfo.txt"), 
  personality = personalities.FRIDAY, 
  openai_key = Jarvis.loadApiKeyFromFile("secret.txt"),
  temperature = 0.6,
  minSimilarity = 0.65,
  backgroundlistener = Jarvis.InputMode.TEXT_BOX,
  outputfunc=print,
  outputasync=False,
)

# Start up discord then minecraft, then get if the temperature of suit 6 is greater than the temperature of suit 7. If suit 7 is hotter, start firefox, otherwise if suit 6 is hotter, start chrome.
# Is the weather in Ohio warmer than the weather in Libya?
# Start firefox then repeat after me: "Foo Bar Baz"
# Build, get the temperature of and then destroy suits 1 to 10, including each number in between
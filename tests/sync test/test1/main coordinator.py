from GPTJarvis import Jarvis, personalities
Jarvis.init_main(
  scope = ["/", "../test2/file3.py", "../test3"],
  info = Jarvis.loadInfoFromFile("aditionalInfo.txt"), 
  personality = personalities.JARVIS, 
  openai_key = Jarvis.loadApiKeyFromFile("secret.txt"),
  temperature = 0.6,
  minSimilarity = 0.65,
  backgroundlistener = Jarvis.InputMode.TEXT_BOX
)
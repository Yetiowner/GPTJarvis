import time
timex = time.time()
from GPTJarvis import Jarvis, personalities
print(time.time()-timex)

Jarvis.init_main(
  scope = "folder",
  info = Jarvis.loadInfoFromFile("aditionalInfo.txt"), 
  personality = personalities.JARVIS, 
  openai_key = Jarvis.loadApiKeyFromFile("secret.txt")
)
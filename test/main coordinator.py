import GPTJarvis.src.Jarvis as Jarvis
import GPTJarvis.src.personalities as personalities
Jarvis.loadApiKeyFromFile("secret.txt")
with open("aditionalInfo.txt", "r") as file:
  info = file.read()
Jarvis.init_main(scope = "folder", info = info, personality = personalities.FRIDAY)
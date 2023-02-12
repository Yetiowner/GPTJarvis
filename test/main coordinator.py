from GPTJarvis.src import Jarvis
Jarvis.loadApiKeyFromFile("secret.txt")
with open("aditionalInfo.txt", "r") as file:
  info = file.read()
Jarvis.init_main(scope = "folder", info = info)
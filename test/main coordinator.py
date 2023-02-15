import GPTJarvis.src.Jarvis as Jarvis
import GPTJarvis.src.personalities as personalities
Jarvis.init_main(
  scope = "folder",
  info = Jarvis.loadInfoFromFile("aditionalInfo.txt"), 
  personality = personalities.JARVIS, 
  openai_key = Jarvis.loadApiKeyFromFile("secret.txt")
)
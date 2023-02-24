from GPTJarvis import Jarvis, personalities
Jarvis.init_main(
  scope = "/",
  info = Jarvis.loadInfoFromFile("aditionalInfo.txt"), 
  personality = personalities.JARVIS, 
  openai_key = Jarvis.loadApiKeyFromFile("secret.txt"),
  temperature = 0.6,
  minSimilarity = 0.65,
  mode = Jarvis.VoiceMode.SPEECH2SPEECH,
  syncmode = Jarvis.SyncMode.ASYNC
)
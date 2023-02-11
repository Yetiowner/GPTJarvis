from urllib.parse import quote
import requests
from playsound import playsound # pip install playsound==1.2.2
import io
import os
import speech_recognition as sr

TEXT = "text"
VOICE = "voice"
MODE = VOICE
def say(text, mode=MODE):
  if mode == TEXT:
    print(text)
  elif mode == VOICE:
    url = f"https://api.streamelements.com/kappa/v2/speech?voice=Brian&text={quote(text)}" # thx to https://github.com/styler for API
    data = requests.get(url).content
    os.remove('voiceclip.mp3')
    with open('voiceclip.mp3', 'wb') as f:
      f.write(data)
    playsound('voiceclip.mp3')

"""recog = sr.Recognizer()
with sr.Microphone() as source2:
  recog.adjust_for_ambient_noise(source2, duration=2)
  print("ready")
  audio2 = recog.listen(source2)
  print("ready1")
  text = recog.recognize_google(audio2, show_all=False, language="en-GB")
  print(text)"""
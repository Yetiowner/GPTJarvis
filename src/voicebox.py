from urllib.parse import quote
import requests
from playsound import playsound # pip install playsound==1.2.2
import io

TEXT = "text"
VOICE = "voice"
def say(text, mode=VOICE):
  if mode == TEXT:
    print(text)
  elif mode == VOICE:
    url = f"https://api.streamelements.com/kappa/v2/speech?voice=Brian&text={quote(text)}" # thx to https://github.com/styler for API
    data = requests.get(url).content
    with open('voiceclip.mp3', 'wb') as f:
      f.write(data)
    playsound('voiceclip.mp3')
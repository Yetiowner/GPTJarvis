from urllib.parse import quote
import requests
from playsound import playsound # pip install playsound==1.2.2
import io
import os
import speech_recognition as sr
import time

TEXT = "text"
VOICE = "voice"
MODE = VOICE
FILEPATH = None

def say(text, mode=MODE):
  if mode == TEXT:
    print(text)
  elif mode == VOICE:
    url = f"https://api.streamelements.com/kappa/v2/speech?voice=Brian&text={quote(text)}" # thx to https://github.com/styler for API
    data = requests.get(url).content
    try:
      os.remove(FILEPATH+'voiceclip.mp3')
    except FileNotFoundError:
      pass
    with open(FILEPATH+'voiceclip.mp3', 'wb') as f:
      f.write(data)
    playsound(FILEPATH+'voiceclip.mp3')

"""recog = sr.Recognizer()
with sr.Microphone() as source2:
  recog.adjust_for_ambient_noise(source2, duration=0.5)
  #recog.pause_threshold = 0.4
  #recog.phrase_threshold = 0.1
  #recog.non_speaking_duration = 0.1
  print("ready")
  audio2 = recog.listen(source2)
  print("ready1")
  text = recog.recognize_google(audio2, show_all=False, language="en-GB")
  print(text)"""

"""from TTS.api import TTS

# List available TTS models and choose the first one
print(TTS.list_models())
model_name = TTS.list_models()[0]
# Init TTS
tts = TTS(model_name)
# Run TTS
# Text to speech with a numpy output
#wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])
# Text to speech to a file
print(tts.speakers)
print(tts.languages)
tts.tts_to_file(text="Hello world! I am a text to speech model and this is a test.", speaker=tts.speakers[5], language=tts.languages[0], file_path="output.wav")
say("Hello world! I am a text to speech model and this is a test.")"""
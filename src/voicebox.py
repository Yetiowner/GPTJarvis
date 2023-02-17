from urllib.parse import quote
import requests
import os
import time
import GPTJarvis.src.personalities as personalities
from pydub import AudioSegment # Install ffmpeg exes and add to path
import soundfile as sf
import pyrubberband as pyrb # https://breakfastquay.com/rubberband/index.html Install CLU and add to path
import subprocess
from pydub.playback import play


TEXT = "text"
VOICE = "voice"
MODE = VOICE
FILEPATH = ".Jarvis/"

def say(text, mode=MODE, personality=personalities.JARVIS):
  pass
  if mode == TEXT:
    print(text)
  elif mode == VOICE:
    url = f"https://api.streamelements.com/kappa/v2/speech?voice={personality.voice}&text={quote(text)}" # thx to https://github.com/styler for API
    data = requests.get(url).content
    try:
      os.remove(FILEPATH+'voiceclip.mp3')
    except FileNotFoundError:
      pass
    with open(FILEPATH+'voiceclip.mp3', 'wb') as f:
      f.write(data)
      
    #print(time.time()-timex)
    subprocess.run(["ffmpeg", "-y", "-i",  f"{FILEPATH}voiceclip.mp3", "-speed", "16", f"{FILEPATH}file.wav", "-hide_banner", "-loglevel", "error"])
    #print(time.time()-timex)
    data, samplerate = sf.read(FILEPATH+"file.wav")
    y_stretch = pyrb.time_stretch(data, samplerate, personality.speed)
    y_shift = pyrb.pitch_shift(y_stretch, samplerate, personality.pitch)
    sf.write(FILEPATH+"outputfile1X5.wav", y_shift, samplerate, format='wav')
    #print(time.time()-timex)
    song = AudioSegment.from_wav(FILEPATH+"outputfile1X5.wav")
    #print(time.time()-timex)
    play(song)
    try:
      os.remove(f"{FILEPATH}outputfile1X5.wav")
    except FileNotFoundError:
      pass
    
    try:
      os.remove(f"{FILEPATH}file.wav")
    except FileNotFoundError:
      pass

    try:
      os.remove(f"{FILEPATH}voiceclip.mp3")
    except FileNotFoundError:
      pass

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

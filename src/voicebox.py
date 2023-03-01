from urllib.parse import quote
import requests
import os
import time
import GPTJarvis.src.personalities as personalities
import GPTJarvis.src.Jarvis as Jarvis
from pydub import AudioSegment # Install ffmpeg exes and add to path
import soundfile as sf
import pyrubberband as pyrb # https://breakfastquay.com/rubberband/index.html Install CLU and add to path
import subprocess
from pydub.playback import play
import speech_recognition as sr
import io
import keyboard
import threading
import tkinter


FILEPATH = ".Jarvis/"
HOTKEY = "alt+j"

def say(text, personality=personalities.JARVIS):
  url = f"https://api.streamelements.com/kappa/v2/speech?voice={personality.voice}&text={quote(text)}" # thx to https://github.com/styler for API
  data = requests.get(url).content
  try:
    os.remove(FILEPATH+'voiceclip.mp3')
  except FileNotFoundError:
    pass
  with open(FILEPATH+'voiceclip.mp3', 'wb') as f:
    f.write(data)
    
  subprocess.run(["ffmpeg", "-y", "-i",  f"{FILEPATH}voiceclip.mp3", "-speed", "16", f"{FILEPATH}file.wav", "-hide_banner", "-loglevel", "error"])
  data, samplerate = sf.read(FILEPATH+"file.wav")
  y_stretch = pyrb.time_stretch(data, samplerate, personality.speed)
  y_shift = pyrb.pitch_shift(y_stretch, samplerate, personality.pitch)
  sf.write(FILEPATH+"outputfile1X5.wav", y_shift, samplerate, format='wav')
  song = AudioSegment.from_wav(FILEPATH+"outputfile1X5.wav")

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

def awaitHotkeyPress():
  global triggered
  triggered = False
  while not triggered:
    time.sleep(0.1)
  triggered = False

def checkHotkeyRelease():
  for part in HOTKEY.split("+"):
    if not keyboard.is_pressed(part):
      return True
  return False

def textboxListener():
  root = tkinter.Tk()
  label = tkinter.Label(root, text="Enter your prompt to Jarvis:")
  label.pack()
  entry = tkinter.Entry(root)
  entry.pack()
  submit = tkinter.Button(root, text="Submit", command = lambda: Jarvis.submitRequest(entry.get()))
  submit.pack()
  root.mainloop()

def startTextboxListener():
  thread = threading.Thread(target=textboxListener)
  thread.start()

def voiceListener():
    global stop
    while True:
      try:
        keyboard.clear_all_hotkeys()
      except AttributeError:
        pass
      keyboard.add_hotkey(HOTKEY, setHotkeyTriggered)
      recog = sr.Recognizer()
      #print(sr.Microphone.list_microphone_names())
      lastHotkeyPoll = time.time()
      with sr.Microphone() as source:
        recog.adjust_for_ambient_noise(source, duration=0.5)

        awaitHotkeyPress()
      
        frames = io.BytesIO()
        stop = False
        while stop == False:
            if time.time()-lastHotkeyPoll > 0.2:
              if checkHotkeyRelease():
                break
              lastHotkeyPoll = time.time()

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0:
              break

            frames.write(buffer)

        frame_data = frames.getvalue()
        frames.close()
        audio2 = sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
        text = recog.recognize_google(audio2, show_all=True, with_confidence=True)#, language="en-GB")
        choices = [text["alternative"][i]["transcript"] for i in range(len(text["alternative"]))]
        truetext = choices[0]

      Jarvis.submitRequest(truetext)

def startVoiceListener():
  thread = threading.Thread(target=voiceListener)
  thread.start()

def setHotkeyTriggered():
  global triggered
  triggered = True

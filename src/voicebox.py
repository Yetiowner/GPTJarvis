from urllib.parse import quote
import requests
import os
import time
import GPTJarvis.src.personalities as personalities
import GPTJarvis.src.Jarvis as Jarvis
import GPTJarvis.src.voicerecorder as voicerecorder
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
import openai
from waiting import wait
import random

FILEPATH = ".Jarvis/"
HOTKEY = "alt+j"
listening = False
recorder = None

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

def startRecording():
  global listening
  listening = True
  recorder.start_recording()

def stopRecording():
  global listening
  listening = False
  recorder.stop_recording()
  with open(f"{FILEPATH}uservoice.mp3", "rb") as f:
    timex = time.time()
    transcript = openai.Audio.transcribe("whisper-1", f, prompt = "Jarvis, could you help me? I have some questions.")
    transcript = transcript["text"]
    print(time.time()-timex)
  print(transcript)

  Jarvis.submitRequest(transcript)

def initiateVoiceListener():
  global recorder
  recorder = voicerecorder.Recorder(filename = f"{FILEPATH}uservoice")
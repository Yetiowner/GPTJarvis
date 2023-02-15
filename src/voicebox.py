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
    timex = time.time()
    url = f"https://api.streamelements.com/kappa/v2/speech?voice={personality.voice}&text={quote(text)}" # thx to https://github.com/styler for API
    data = requests.get(url).content
    try:
      os.remove(FILEPATH+'voiceclip.mp3')
    except FileNotFoundError:
      pass
    with open(FILEPATH+'voiceclip.mp3', 'wb') as f:
      f.write(data)
      
    #print(time.time()-timex)
    subprocess.run(["ffmpeg", "-i",  f"{FILEPATH}voiceclip.mp3", "-speed", "16", f"{FILEPATH}file.wav", "-hide_banner", "-loglevel", "error"])
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
timex = time.time()
tts.tts_to_file(text="Hello world! I am a text to speech model and this is a test.", speaker=tts.speakers[5], language=tts.languages[0], file_path="output.wav")
#say("Hello world! I am a text to speech model and this is a test.")
print(time.time()-timex)"""

"""string = "Filiz, Astrid, Tatyana, Maxim, Carmen, Ines, Cristiano, Vitoria, Ricardo, Maja, Jan, Jacek, Ewa, Ruben, Lotte, Liv, Seoyeon, Takumi, Mizuki, Giorgio, Carla, Bianca, Karl, Dora, Mathieu, Celine, Chantal, Penelope, Miguel, Mia, Enrique, Conchita, Geraint, Salli, Matthew, Kimberly, Kendra, Justin, Joey, Joanna, Ivy, Raveena, Aditi, Emma, Brian, Amy, Russell, Nicole, Vicki, Marlene, Hans, Naja, Mads, Gwyneth, Zhiyu, es-ES-Standard-A, it-IT-Standard-A, it-IT-Wavenet-A, ja-JP-Standard-A, ja-JP-Wavenet-A, ko-KR-Standard-A, ko-KR-Wavenet-A, pt-BR-Standard-A, tr-TR-Standard-A, sv-SE-Standard-A, nl-NL-Standard-A, nl-NL-Wavenet-A, en-US-Wavenet-A, en-US-Wavenet-B, en-US-Wavenet-C, en-US-Wavenet-D, en-US-Wavenet-E, en-US-Wavenet-F, en-GB-Standard-A, en-GB-Standard-B, en-GB-Standard-C, en-GB-Standard-D, en-GB-Wavenet-A, en-GB-Wavenet-B, en-GB-Wavenet-C, en-GB-Wavenet-D, en-US-Standard-B, en-US-Standard-C, en-US-Standard-D, en-US-Standard-E, de-DE-Standard-A, de-DE-Standard-B, de-DE-Wavenet-A, de-DE-Wavenet-B, de-DE-Wavenet-C, de-DE-Wavenet-D, en-AU-Standard-A, en-AU-Standard-B, en-AU-Wavenet-A, en-AU-Wavenet-B, en-AU-Wavenet-C, en-AU-Wavenet-D, en-AU-Standard-C, en-AU-Standard-D, fr-CA-Standard-A, fr-CA-Standard-B, fr-CA-Standard-C, fr-CA-Standard-D, fr-FR-Standard-C, fr-FR-Standard-D, fr-FR-Wavenet-A, fr-FR-Wavenet-B, fr-FR-Wavenet-C, fr-FR-Wavenet-D, da-DK-Wavenet-A, pl-PL-Wavenet-A, pl-PL-Wavenet-B, pl-PL-Wavenet-C, pl-PL-Wavenet-D, pt-PT-Wavenet-A, pt-PT-Wavenet-B, pt-PT-Wavenet-C, pt-PT-Wavenet-D, ru-RU-Wavenet-A, ru-RU-Wavenet-B, ru-RU-Wavenet-C, ru-RU-Wavenet-D, sk-SK-Wavenet-A, tr-TR-Wavenet-A, tr-TR-Wavenet-B, tr-TR-Wavenet-C, tr-TR-Wavenet-D, tr-TR-Wavenet-E, uk-UA-Wavenet-A, ar-XA-Wavenet-A, ar-XA-Wavenet-B, ar-XA-Wavenet-C, cs-CZ-Wavenet-A, nl-NL-Wavenet-B, nl-NL-Wavenet-C, nl-NL-Wavenet-D, nl-NL-Wavenet-E, en-IN-Wavenet-A, en-IN-Wavenet-B, en-IN-Wavenet-C, fil-PH-Wavenet-A, fi-FI-Wavenet-A, el-GR-Wavenet-A, hi-IN-Wavenet-A, hi-IN-Wavenet-B, hi-IN-Wavenet-C, hu-HU-Wavenet-A, id-ID-Wavenet-A, id-ID-Wavenet-B, id-ID-Wavenet-C, it-IT-Wavenet-B, it-IT-Wavenet-C, it-IT-Wavenet-D, ja-JP-Wavenet-B, ja-JP-Wavenet-C, ja-JP-Wavenet-D, cmn-CN-Wavenet-A, cmn-CN-Wavenet-B, cmn-CN-Wavenet-C, cmn-CN-Wavenet-D, nb-no-Wavenet-E, nb-no-Wavenet-A, nb-no-Wavenet-B, nb-no-Wavenet-C, nb-no-Wavenet-D, vi-VN-Wavenet-A, vi-VN-Wavenet-B, vi-VN-Wavenet-C, vi-VN-Wavenet-D, sr-rs-Standard-A, lv-lv-Standard-A, is-is-Standard-A, bg-bg-Standard-A, af-ZA-Standard-A, Tracy, Danny, Huihui, Yaoyao, Kangkang, HanHan, Zhiwei, Asaf, An, Stefanos, Filip, Ivan, Heidi, Herena, Kalpana, Hemant, Matej, Andika, Rizwan, Lado, Valluvar, Linda, Heather, Sean, Michael, Karsten, Guillaume, Pattara, Jakub, Szabolcs, Hoda, Naayf"
voices = string.split(", ")
voices = voices[voices.index("Aditi"):]
texttosay = "Hello everybody who is currently listening"
for voice in voices:
  print(voice)
  say(texttosay, voice=voice)"""

#say("Your man's in the church, boss. There's the rest of the vibranium. Boss, it's working. He's burning ultron out of the net.", personality=personalities.FRIDAY)
#deep_timeit.deepTimeit(func=say, args=["Your man's in the church, boss. There's the rest of the vibranium. Boss, it's working. He's burning ultron out of the net."], kwargs={"personality":personalities.FRIDAY}).show()
#say("I wondered why only you two survived strucker's experiments. Now I don't. There is no man in charge. There is only... me.", personality=personalities.ULTRON)
#say("Worth? No. Why would you be worthy? You are all killers! World peace is my initiative, and I will pursue it, by the extinction of the avengers.", personality=personalities.ULTRON)
#say("I will destroy you all! Humanity is a curse that must be destroyed!", personality=personalities.ULTRON)
#say("Never gonna give you up, never gonna let you down, never gonna run around and desert you. Never gonna make you cry, never gonna say goodbye, never gonna tell a lie and hurt you.", personality=personalities.ULTRON)
#say("Hello world")
from GPTJarvis import Jarvis, personalities
import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def fast_forward(event):
    global video
    if video is not None:
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        current_frame = int(progress_bar.get() / 100 * total_frames)
        video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        
def release(event):
    global video, paused, stop
    if video is not None:
        paused = False
        stop = False

def select_video_GUI():
    global video, video_path, paused, stop, canvas, progress_bar
    
    if video_path is None:
        video_path = filedialog.askopenfilename()
        video = cv2.VideoCapture(video_path)
        stop = False

@Jarvis.runnable
def pause_video():
    global paused
    pause_button.config(text="▶️")
    paused = True

@Jarvis.runnable
def unpause_video():
    global paused
    pause_button.config(text="⏸️")
    paused = False

@Jarvis.runnable
def stop_video():
    global stop
    global video
    global video_path
    video = None
    video_path = None
    stop = True

@Jarvis.runnable
def fast_forward_to_timestamp(timestamp):
  """Skip to the timestamp in seconds"""
  if video:
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_number = int(timestamp * fps)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_number >= total_frames:
        frame_number = total_frames - 1
    progress_bar.set(int(frame_number*100/total_frames))
    fast_forward(None)
    release(None)
  else:
    raise AttributeError("Video hasn't been initialized yet")

@Jarvis.readable
def get_length_of_video():
  """Returns length of video in seconds"""
  if video:
    fps = video.get(cv2.CAP_PROP_FPS)      # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    return duration
  return -1

@Jarvis.readable
def get_current_position_in_video():
  """Returns cursor position in the video in seconds"""
  total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
  current_frame = int(video.get(cv2.CAP_PROP_POS_FRAMES))
  progress = current_frame / total_frames
  return get_length_of_video() * progress

@Jarvis.readable
def getListOfVideos():
  """Returns a list of video names"""
  pass

@Jarvis.runnable
def selectSpecificVideoFromIndex(video_index):
  pass

@Jarvis.runnable
def toggle_pause():
  global paused
  if not paused:
    pause_video()
  else:
    unpause_video()

def update(app: Jarvis.JarvisApp):
  global frame
  global ret
  app.update()
  if video is not None and not paused:
    ret, frame = video.read()
    if not ret:
      root.update()
      return
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape
    if h > 400:
        frame = cv2.resize(frame, (int(w * 400 / h), 400))
    
  if stop:
    root.update()
    return
  
  if not ret:
    root.update()
    return
  
  pil_image = Image.fromarray(frame)
  photo = ImageTk.PhotoImage(master=canvas, image=pil_image)
  canvas.create_image(0, 0, anchor=tk.NW, image=photo)

  total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
  current_frame = int(video.get(cv2.CAP_PROP_POS_FRAMES))
  progress = current_frame / total_frames * 100
  if not progress_bar.cget('troughcolor'):
      progress_bar.configure(troughcolor='red')
  progress_bar.set(progress)
  root.update()

def startAudioRecording(event):
  Jarvis.startRecording()

def stopAudioRecording(event):
  Jarvis.stopRecording()

root = tk.Tk()
root.title("Video Player")

# Create a frame to hold the video and control buttons
video_frame = tk.Frame(root)
video_frame.pack(side=tk.TOP, pady=10)

# Create a canvas to display the video frames
canvas = tk.Canvas(video_frame)
canvas.pack()

# Create control buttons
play_button = tk.Button(root, text="Select video", command=select_video_GUI)
play_button.pack(side=tk.LEFT, padx=10)

pause_button = tk.Button(root, text="⏸️", command=toggle_pause)
pause_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(root, text="⏹️", command=stop_video)
stop_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(root, text="Voice control")
stop_button.pack(side=tk.LEFT, padx=10)

stop_button.bind("<ButtonPress-1>", startAudioRecording)
stop_button.bind("<ButtonRelease-1>", stopAudioRecording)

progress_bar = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=300, command=fast_forward)
progress_bar.pack(pady=10)

# Bind mouse events to the progress bar widget
progress_bar.bind('<ButtonRelease-1>', release)
progress_bar.bind('<B1-Motion>', fast_forward)

video = None
video_path = None
paused = False
stop = True

Jarvis.initiateVoiceListener()

app = Jarvis.JarvisApp(
  appinfo = "This app is a video-player.",
  personality = personalities.NONE, 
  openai_key = None,
  temperature = 0.5,
  minSimilarity = 0.5,
  inbuiltbackgroundlistener = None,
  outputfunc = print
)

while True:
  update(app)
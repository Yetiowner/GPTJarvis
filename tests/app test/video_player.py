from GPTJarvis import Jarvis, personalities
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os

VIDEODIR = r"C:\Users\User\Videos"

def get_videos():
  files = [f for f in os.listdir(VIDEODIR) if os.path.isfile(os.path.join(VIDEODIR, f)) and any([f.endswith(i) for i in [".mp4", ".avi", ".gif", ".mkv"]])]
  data = {}
  for file_name in files:
    viddat = {}

    file_path = os.path.join(VIDEODIR, file_name)

    vidcap = cv2.VideoCapture(file_path)
    success,image = vidcap.read()

    # resize the thumbnail to a reasonable size
    color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    thumbnail = Image.fromarray(color_coverted)
    thumbnail = thumbnail.resize((60, 45) )

    viddat["thumbnail"] = thumbnail
    viddat["videoCapture"] = vidcap
    data[file_name] = viddat
  
  return data

videoData = get_videos()


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

@Jarvis.runnable
def select_video_GUI():
    global window

    folder_path = VIDEODIR
    # create a tkinter window
    window = tk.Tk()
    window.title("Select Video")

    window.config(height=300)

    # create a frame to hold the video thumbnails
    frame = tk.Frame(window)
    frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame, width=300, height=300)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')

    selected = True

    def on_inner_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))
      
    def helperSelectSpecificVideo(name):
        selectSpecificVideo(name)
        selected = False
        window.destroy()

    inner_frame.bind('<Configure>', on_inner_frame_configure)

    cols = 4
    titlelen = 10
    i = -1
    # loop through all the files in the folder_path
    for video in videoData:
        i += 1
        # get the full path of the file
        file_path = os.path.join(folder_path, video)

        # extract the video title from the filename
        video_title = video.split(".")[0]
        if len(video_title) > titlelen:
            video_title = video_title[:titlelen]
            video_title += "..."

        # extract the thumbnail from the video
        thumbnail = videoData[video]["thumbnail"]
        thumbnail = ImageTk.PhotoImage(thumbnail, master = window)

        # create a label to hold the thumbnail and video title
        video_label = tk.Label(inner_frame)
        video_label.image = thumbnail
        video_label.configure(image=thumbnail, text=video_title, compound=tk.TOP)

        # bind the label to a function that will be called when the user clicks on it
        video_label.bind("<Button-1>", lambda event, index=i: helperSelectSpecificVideo(video))

        # add the label to the frame
        video_label.grid(row=i // cols, column=i % cols)

    # run the tkinter event loop
    while selected:
      try:
        window.update()
      except:
        break

def getThumbnail(file_path):
    # use a video processing library to extract a thumbnail from the video
    # here we're using the moviepy library
    vidcap = cv2.VideoCapture(file_path)
    success,image = vidcap.read()

    # resize the thumbnail to a reasonable size
    color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    thumbnail = Image.fromarray(color_coverted)
    thumbnail = thumbnail.resize((60, 45), Image.ANTIALIAS)
    thumbnail = ImageTk.PhotoImage(thumbnail, master = window)

    return thumbnail

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
def set_time_to_timestamp(timestamp):
  """Skip to the timestamp in seconds. Note that the timestamp is relative to the start of the video."""
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
def get_length_of_video(videoName: str):
  """Returns length of the video with the specified name."""
  cap = videoData[videoName]["videoCapture"]
  fps = cap.get(cv2.CAP_PROP_FPS)      # OpenCV v2.x used "CV_CAP_PROP_FPS"
  frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  duration = frame_count/fps
  return duration

@Jarvis.readable
def get_current_position_in_video():
  """Returns cursor position in the video in seconds"""
  total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
  current_frame = int(video.get(cv2.CAP_PROP_POS_FRAMES))
  progress = current_frame / total_frames
  return get_length_of_video(video_name) * progress

@Jarvis.readable
def getListOfVideos():
  """Returns a dictionary of videos. The key of each video is the video name. The value is another dictionary of the style {"thumbnail": PIL image, "videoCapture": cv2 VideoCapture}"""
  return videoData

@Jarvis.readable
def getNameOfVideoCurrentlyPlaying():
  """Returns the string name of the video currently playing as it would appear in getListOfVideos"""
  return os.path.split(video_path)[1]

@Jarvis.runnable
def selectSpecificVideo(name: str):
  """Selects the video with the file name specified. The name should be specific, and can be found in getListOfVideos"""
  global video, video_name, video_path, paused, stop, canvas, progress_bar
  video_path = os.path.join(VIDEODIR, name)
  video_name = name
  video = videoData[name]["videoCapture"]
  stop = False

@Jarvis.runnable
def toggle_pause():
  global paused
  if not paused:
    pause_video()
  else:
    unpause_video()

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
)

while True:
  app.update()
  if video is not None and not paused:
    ret, frame = video.read()
    if not ret:
      root.update()
      continue
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape
    if h > 400:
        frame = cv2.resize(frame, (int(w * 400 / h), 400))
    
  if stop:
    root.update()
    continue
  
  if not ret:
    root.update()
    continue
  
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
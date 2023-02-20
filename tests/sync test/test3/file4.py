from GPTJarvis import Jarvis
import tkinter as tk

@Jarvis.readable
def getHeightOfUserInCentimetres():
  """Returns user's height in centimetres"""
  global heightvar
  global root
  global val
  #Note: input() does not work with Jarvis

  root=tk.Tk()
  heightvar=tk.StringVar()
  label = tk.Label(root, text="Enter your height in centimetres:")
  label.pack(padx=10, pady=10)
  entry = tk.Entry(root, textvariable=heightvar)
  entry.pack(padx=10, pady=10)
  submitbutton = tk.Button(root, command=submit, text="Submit")
  submitbutton.pack(padx=10, pady=10)

  val = None

  while val == None:
    root.update()

  return val

def submit():
  global val

  val = heightvar.get()
    
  root.destroy()

Jarvis.init()
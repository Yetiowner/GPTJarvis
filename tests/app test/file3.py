import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from GPTJarvis import Jarvis, personalities

@Jarvis.runnable
def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt_edit.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    window.title(f"Thecleverprogrammer - {filepath}")

@Jarvis.runnable
def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension="txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = txt_edit.get(1.0, tk.END)
        output_file.write(text)
    window.title(f"Thecleverprogrammer - {filepath}")

window = tk.Tk()
window.title("Thecleverprogrammer")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

txt_edit = tk.Text(window)
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
btn_save = tk.Button(fr_buttons, text="Save As...", command=save_file)
label = tk.Label(fr_buttons, text="Enter what you want me to do: ")
entry = tk.Entry(fr_buttons)
submit = tk.Button(fr_buttons, text="Submit", command=lambda: Jarvis.submitRequest(entry.get()))

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)
label.grid(row=2, column=0, sticky="ew", padx=5, pady=(20, 0))
entry.grid(row=3, column=0, sticky="ew", padx=5)
submit.grid(row=4, column=0, sticky="ew", padx=5)

fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")

app = Jarvis.init_app(
  appinfo = "This app acts as a word processor",
  personality = personalities.JARVIS, 
  openai_key = None,
  temperature = 0.6,
  minSimilarity = 0.65,
  backgroundlistener = Jarvis.InputMode.NONE
)
while True:
  Jarvis.update_app(app)
  window.update()
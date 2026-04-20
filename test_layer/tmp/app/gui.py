import subprocess
import threading
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

# Global process reference
current_process = None

# -------- MAIN WINDOW --------
root = Tk()
root.title("Docksmith Control Panel")
root.geometry("600x450")

# -------- STYLE --------
style = ttk.Style()
style.theme_use('clam')

style.configure(".",
    background="#1e1e1e",
    foreground="white"
)

# -------- TITLE --------
title = Label(root, text="Docksmith Control Panel",
              bg="#1e1e1e", fg="white",
              font=("Arial", 16))
title.pack(pady=10)

# -------- BUTTON FRAME --------
frame = Frame(root, bg="#1e1e1e")
frame.pack(pady=15)

# -------- LOG BOX --------
log_box = ScrolledText(root, height=15,
                       bg="#111111", fg="#00FFAA",
                       insertbackground="white",
                       font=("Courier", 10))
log_box.pack(fill=BOTH, expand=True, padx=10, pady=10)

# -------- LOG FUNCTION --------
def log(msg):
    log_box.insert(END, msg + "\n")
    log_box.see(END)

# -------- BUILD --------
def build_image():
    if getattr(build_image, "running", False):
        log("[ALREADY BUILDING]")
        return

    build_image.running = True

    def task():
        log_box.delete('1.0', END)

        process = subprocess.Popen(
            ["python3", "main.py", "build", "test:latest", "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            log(line.strip())

        log("[BUILD END]")
        build_image.running = False

    threading.Thread(target=task).start()

# -------- RUN --------
def run_container():
    global current_process

    if getattr(run_container, "running", False):
        log("[ALREADY RUNNING]")
        return

    run_container.running = True

    def task():
        global current_process

        log("[RUN START]")

        current_process = subprocess.Popen(
            ["python3", "main.py", "run", "test:latest"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in current_process.stdout:
            log(line.strip())

        log("[RUN END]")
        run_container.running = False
        current_process = None

    threading.Thread(target=task).start()

# -------- STOP --------
def stop_container():
    global current_process

    if current_process and current_process.poll() is None:
        current_process.terminate()
        log("[CONTAINER STOPPED]")
    else:
        log("[NO RUNNING CONTAINER]")

    current_process = None
    run_container.running = False

# -------- BUTTONS --------
ttk.Button(frame, text="Build Image", command=build_image).grid(row=0, column=0, padx=15)
ttk.Button(frame, text="Run Container", command=run_container).grid(row=0, column=1, padx=15)
ttk.Button(frame, text="Stop Container", command=stop_container).grid(row=0, column=2, padx=15)

root.mainloop()

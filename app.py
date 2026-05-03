import tkinter as tk
import cv2
from PIL import Image, ImageTk
from predict import run_pipeline

class HealthApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Health Agent")
        self.root.geometry("900x600")

        self.cap = None

        # Video frame
        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # Buttons
        tk.Button(self.root, text="Start Camera", command=self.start_camera).pack()
        tk.Button(self.root, text="Capture & Analyze", command=self.capture).pack()

        # Output
        self.output = tk.Text(self.root, height=15)
        self.output.pack(fill="both", expand=True)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
        self.root.after(10, self.update_frame)

    def capture(self, part):
        filename = f"{part}.jpg"
        cv2.imwrite(filename, self.frame)
        self.images[part] = filename

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HealthApp()
import tkinter as tk
import cv2
from PIL import Image, ImageTk
from predict import run_pipeline

class HealthApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Health Agent")
        self.root.geometry("900x650")

        self.cap = None

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        tk.Button(self.root, text="Start Camera", command=self.start_camera).pack()
        tk.Button(self.root, text="Capture & Analyze", command=self.capture).pack()

        self.output = tk.Text(self.root, height=20, font=("Consolas", 10))
        self.output.pack(fill="both", expand=True)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

        self.root.after(10, self.update_frame)

    def capture(self):
        cv2.imwrite("captured.jpg", self.frame)

        result = run_pipeline("captured.jpg")

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, result)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HealthApp()
    app.run()
    app.run()

self.images = {"eye": None, "tongue": None, "nail": None}

tk.Button(self.root, text="Capture Eye", command=lambda: self.capture("eye")).pack()
tk.Button(self.root, text="Capture Tongue", command=lambda: self.capture("tongue")).pack()
tk.Button(self.root, text="Capture Nail", command=lambda: self.capture("nail")).pack()
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import threading
import time
import wave
import struct
import ffmpeg
from pvrecorder import PvRecorder
import numpy as np
import cv2
import pyautogui

from log import hash_password

class SyncedRecorderPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")
        self.root.geometry("400x300")
        
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True, fill='both')
        
        self.is_recording = False
        self.audio_data = []
        
        self.start_button = tk.Button(self.frame, text="Start Recording", font=('Helvetica', 16), command=self.start_recording)
        self.start_button.pack(pady=10)
        
        self.stop_button = tk.Button(self.frame, text="Stop Recording", font=('Helvetica', 16), command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)
        
        self.device_label = tk.Label(self.frame, text="", font=('Helvetica', 10))
        self.device_label.pack(pady=10)

        self.root.bind("<B1-Motion>", self.move_window)
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)

        self.x = 0
        self.y = 0

        # Audio recorder setup
        self.audio_device_index = self.find_stereo_mix_device()
        if self.audio_device_index is not None:
            self.recorder = PvRecorder(device_index=self.audio_device_index, frame_length=512)
            device_name = PvRecorder.get_available_devices()[self.audio_device_index]
            self.device_label.config(text=f"Using device: {device_name}")
        else:
            messagebox.showerror("Error", "Stereo Mix device not found. Please enable it in your sound settings.")
            self.root.destroy()

    def find_stereo_mix_device(self):
        devices = PvRecorder.get_available_devices()
        for index, device in enumerate(devices):
            if "stereo mix" in device.lower():
                return index
        return None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def move_window(self, event):
        x = self.root.winfo_pointerx() - self.x
        y = self.root.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.audio_data = []
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.video_thread = threading.Thread(target=self.record_video)
            self.audio_thread.start()
            self.video_thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            messagebox.showinfo("Recording", "Screen and audio recording started.")
        else:
            messagebox.showwarning("Warning", "Recording is already running.")

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.audio_thread.join()
            self.video_thread.join()
            self.save_recording()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def record_audio(self):
        self.recorder.start()
        start_time = time.time()
        while self.is_recording:
            frame = self.recorder.read()
            self.audio_data.extend(frame)
        self.recorder.stop()

    def record_video(self):
        fps = 30.0
        frame_time = 1 / fps
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        screen_size = pyautogui.size()
        out = cv2.VideoWriter('output_video.mp4', fourcc, fps, screen_size)
        
        start_time = time.time()
        while self.is_recording:
            frame_start = time.time()
            
            # Capture the screen
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Write the frame
            out.write(frame)
            
            # Calculate sleep time to maintain constant frame rate
            processing_time = time.time() - frame_start
            sleep_time = max(0, frame_time - processing_time)
            time.sleep(sleep_time)
        
        out.release()

    def save_recording(self):
        # Save audio
        audio_path = 'output_audio.wav'
        with wave.open(audio_path, 'w') as f:
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(self.audio_data), *self.audio_data))

        # Merge audio and video
        input_video = ffmpeg.input('output_video.mp4')
        input_audio = ffmpeg.input(audio_path)
        output_file = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        
        if output_file:
            try:
                ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_file).run(overwrite_output=True)
                messagebox.showinfo("Success", "Recording saved successfully.")
                os.remove("output_video.mp4")
                os.remove(audio_path)
            except FileNotFoundError:
                messagebox.showerror("Error", "ffmpeg not found. Ensure it is installed and added to PATH.")
            except ffmpeg.Error as e:
                messagebox.showerror("Error", f"Failed to save recording: {e}")

def hash_answer(answer):
    # Simple hash function for demonstration purposes
    return str(hash(answer))

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Page")
        self.root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        self.root.configure(bg="#282c34")

        tk.Label(root, text="Language Translator", font=("Arial", 32), bg="#282c34", fg="#61dafb").pack(pady=10)
        tk.Label(root, text="Login", font=("Arial", 24), bg="#282c34", fg="#61dafb").pack(pady=50)
        
        tk.Label(root, text="Username:", font=("Arial", 14), bg="#282c34", fg="white").pack(pady=10)
        self.username_entry = tk.Entry(root, font=("Arial", 14))
        self.username_entry.pack(pady=10, ipadx=50)
        
        tk.Label(root, text="Password:", font=("Arial", 14), bg="#282c34", fg="white").pack(pady=10)
        self.password_entry = tk.Entry(root, show="*", font=("Arial", 14))
        self.password_entry.pack(pady=10, ipadx=50)
        
        tk.Button(root, text="Login", font=("Arial", 14), bg="#61dafb", command=self.login).pack(pady=20)
        tk.Button(root, text="Register", font=("Arial", 14), bg="#61dafb", command=self.register).pack(pady=10)
        tk.Button(root, text="Forgot Password/Change Password", font=("Arial", 14), bg="#61dafb", command=self.open_reset_window).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            try:
                with open(f"users/{username}.txt", "r") as file:
                    lines = file.readlines()
                    stored_password = lines[0].strip()
                    if stored_password == hash_password(password):
                        messagebox.showinfo("Login Success", "Welcome!")
                        self.root.withdraw()
                        self.open_recorder_page()
                    else:
                        messagebox.showerror("Login Failed", "Invalid username or password")
            except FileNotFoundError:
                messagebox.showerror("Login Failed", "User not found")
        else:
            messagebox.showerror("Error", "Both fields are required!")

    def register(self):
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Register")
        reg_window.geometry("400x350")

        tk.Label(reg_window, text="Username:").pack(pady=10)
        reg_username_entry = tk.Entry(reg_window)
        reg_username_entry.pack(pady=5)

        tk.Label(reg_window, text="Password:").pack(pady=10)
        reg_password_entry = tk.Entry(reg_window, show="*")
        reg_password_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Security Question:").pack(pady=10)
        reg_security_question_entry = tk.Entry(reg_window)
        reg_security_question_entry.pack(pady=5)

        tk.Label(reg_window, text="Security Answer:").pack(pady=10)
        reg_security_answer_entry = tk.Entry(reg_window, show="*")
        reg_security_answer_entry.pack(pady=5)

        def save_user():
            username = reg_username_entry.get()
            password = reg_password_entry.get()
            security_question = reg_security_question_entry.get()
            security_answer = reg_security_answer_entry.get()
            
            if username and password and security_question and security_answer:
                if not os.path.exists("users"):
                    os.mkdir("users")
                with open(f"users/{username}.txt", "w") as file:
                    file.write(hash_password(password) + '\n')
                    file.write(security_question + '\n')
                    file.write(hash_answer(security_answer) + '\n')
                messagebox.showinfo("Success", "User registered successfully!")
                reg_window.destroy()
            else:
                messagebox.showerror("Error", "All fields are required!")

        tk.Button(reg_window, text="Register", command=save_user).pack(pady=20)

    def open_reset_window(self):
        reset_window = tk.Toplevel(self.root)
        reset_window.title("Forgot Password/Change Password")
        reset_window.geometry("400x350")

        tk.Label(reset_window, text="Username:").pack(pady=10)
        username_entry = tk.Entry(reset_window)
        username_entry.pack(pady=5)

        tk.Label(reset_window, text="Security Answer:").pack(pady=10)
        security_answer_entry = tk.Entry(reset_window, show="*")
        security_answer_entry.pack(pady=5)

        tk.Label(reset_window, text="New Password:").pack(pady=10)
        new_password_entry = tk.Entry(reset_window, show="*")
        new_password_entry.pack(pady=5)

        def reset_password():
            username = username_entry.get()
            security_answer = security_answer_entry.get()
            new_password = new_password_entry.get()
            
            if username and security_answer and new_password:
                try:
                    with open(f"users/{username}.txt", "r") as file:
                        lines = file.readlines()
                        stored_question = lines[1].strip()
                        stored_answer = lines[2].strip()
                    
                    if hash_answer(security_answer) == stored_answer:
                        with open(f"users/{username}.txt", "w") as file:
                            file.write(hash_password(new_password) + '\n')
                            file.write(stored_question + '\n')
                            file.write(stored_answer + '\n')
                        messagebox.showinfo("Success", "Password updated successfully!")
                        reset_window.destroy()
                    else:
                        messagebox.showerror("Error", "Security answer is incorrect")
                except FileNotFoundError:
                    messagebox.showerror("Error", "User not found")
            else:
                messagebox.showerror("Error", "All fields are required!")

        tk.Button(reset_window, text="Reset Password", command=reset_password).pack(pady=20)

    def open_recorder_page(self):
        recorder_window = tk.Toplevel(self.root)
        SyncedRecorderPage(recorder_window)

if __name__ == "__main__":
    root = tk.Tk()
    login_page = LoginPage(root)
    root.mainloop()

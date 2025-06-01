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
            
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Write the frame
            out.write(frame)
            
            processing_time = time.time() - frame_start
            sleep_time = max(0, frame_time - processing_time)
            time.sleep(sleep_time)
        
        out.release()

    def save_recording(self):
        audio_path = 'output_audio.wav'
        with wave.open(audio_path, 'w') as f:
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(self.audio_data), *self.audio_data))

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
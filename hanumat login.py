import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import hashlib, os, re, pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function for text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Password hashing functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_answer(answer):
    return hashlib.sha256(answer.encode()).hexdigest()

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Page")
        self.root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        self.root.configure(bg="#282c34")

        # Load background image
        self.bg_image = Image.open(r"C:/Users/32han/OneDrive/Pictures/pexels-eberhardgross-1367192.jpg")
        self.bg_image = self.bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create canvas for background
        self.canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenwidth())
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Login Page title
        self.canvas.create_text(root.winfo_screenwidth() // 2, 100, text="Login Page", font=("Arial", 32), fill="white")

        # Username field
        self.canvas.create_text(root.winfo_screenwidth() // 2 - 100, 200, text="Username:", font=("Arial", 14), fill="white")
        self.username_entry = tk.Entry(root, font=("Arial", 14))
        self.canvas.create_window(root.winfo_screenwidth() // 2 + 100, 200, window=self.username_entry)

        # Password field
        self.canvas.create_text(root.winfo_screenwidth() // 2 - 100, 250, text="Password:", font=("Arial", 14), fill="white")
        self.password_entry = tk.Entry(root, show="*", font=("Arial", 14))
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)
        self.canvas.create_window(root.winfo_screenwidth() // 2 + 100, 250, window=self.password_entry)

        # Password strength indicator
        self.strength_label = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#282c34")
        self.canvas.create_window(root.winfo_screenwidth() // 2, 300, window=self.strength_label)
        self.strength_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
        self.canvas.create_window(root.winfo_screenwidth() // 2, 330, window=self.strength_bar)

        # Login button
        login_button = tk.Button(root, text="Login", command=self.login)
        self.canvas.create_window(root.winfo_screenwidth() // 2, 400, window=login_button)

        # Register button
        register_button = tk.Button(root, text="Register", command=self.register)
        self.canvas.create_window(root.winfo_screenwidth() // 2, 450, window=register_button)

        # Forgot Password button
        forgot_button = tk.Button(root, text="Forgot Password", command=self.forgot_password)
        self.canvas.create_window(root.winfo_screenwidth() // 2, 500, window=forgot_button)

    def check_password_strength(self, event=None):
        password = self.password_entry.get()
        strength_score = self.calculate_strength(password)

        # Update strength bar and label
        self.strength_bar["value"] = strength_score
        if strength_score < 30:
            self.strength_label.config(text="Weak", fg="red")
        elif strength_score < 60:
            self.strength_label.config(text="Moderate", fg="orange")
        else:
            self.strength_label.config(text="Strong", fg="green")

    def calculate_strength(self, password):
        """
        This function calculates password strength based on certain criteria:
        - Length of password
        - Use of numbers
        - Use of uppercase and lowercase letters
        - Use of special characters
        """
        score = 0

        # Length of password (basic rule)
        if len(password) >= 8:
            score += 20

        # Numbers in the password
        if re.search(r"\d", password):
            score += 20

        # Special characters in the password
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 20

        # Upper and lowercase letters
        if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
            score += 20

        # Bonus for long password (more than 12 characters)
        if len(password) >= 12:
            score += 20

        return score

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            try:
                with open(f"users/{username}.txt", "r") as file:
                    lines = file.readlines()
                    stored_password = lines[0].strip()
                    if stored_password == hash_password(password):
                        speak("Login successful! Welcome!")
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
        reg_password_entry.bind("<KeyRelease>", lambda event: self.check_password_strength_reg(event, reg_password_entry))
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
                speak("Registration successful! Welcome!")
                reg_window.destroy()
            else:
                messagebox.showerror("Error", "All fields are required!")

        tk.Button(reg_window, text="Register", command=save_user).pack(pady=20)

    def check_password_strength_reg(self, event, password_entry):
        password = password_entry.get()
        strength_score = self.calculate_strength(password)

        # Update password strength label (for the registration page)
        if strength_score < 30:
            password_entry.config(bg="red")
        elif strength_score < 60:
            password_entry.config(bg="orange")
        else:
            password_entry.config(bg="green")

    def forgot_password(self):
        # Forgot Password window
        forgot_window = tk.Toplevel(self.root)
        forgot_window.title("Reset Password")
        forgot_window.geometry("400x350")

        tk.Label(forgot_window, text="Username:").pack(pady=10)
        username_entry = tk.Entry(forgot_window)
        username_entry.pack(pady=5)

        tk.Label(forgot_window, text="Security Question:").pack(pady=10)
        security_question_label = tk.Label(forgot_window, text="")
        security_question_label.pack(pady=5)

        tk.Label(forgot_window, text="Security Answer:").pack(pady=10)
        answer_entry = tk.Entry(forgot_window, show="*")
        answer_entry.pack(pady=5)

        def load_security_question():
            username = username_entry.get()
            try:
                with open(f"users/{username}.txt", "r") as file:
                    lines = file.readlines()
                    security_question = lines[1].strip()
                    security_question_label.config(text=security_question)
            except FileNotFoundError:
                messagebox.showerror("Error", "User not found")

        tk.Button(forgot_window, text="Load Question", command=load_security_question).pack(pady=10)

        def reset_password():
            username = username_entry.get()
            answer = answer_entry.get()
            new_password = new_password_entry.get()

            if username and answer and new_password:
                try:
                    with open(f"users/{username}.txt", "r") as file:
                        lines = file.readlines()
                        stored_answer = lines[2].strip()
                        if stored_answer == hash_answer(answer):
                            # Answer is correct, reset password
                            with open(f"users/{username}.txt", "w") as file:
                                file.write(hash_password(new_password) + '\n')
                                file.write(lines[1])  # Keep the security question
                                file.write(stored_answer + '\n')
                            speak("Password reset successful!")
                            forgot_window.destroy()
                        else:
                            messagebox.showerror("Error", "Incorrect security answer")
                except FileNotFoundError:
                    messagebox.showerror("Error", "User not found")
            else:
                messagebox.showerror("Error", "All fields are required!")

        tk.Label(forgot_window, text="New Password:").pack(pady=10)
        new_password_entry = tk.Entry(forgot_window, show="*")
        new_password_entry.pack(pady=5)

        tk.Button(forgot_window, text="Reset Password", command=reset_password).pack(pady=20)

    def open_recorder_page(self):
        recorder_window = tk.Toplevel(self.root)
        recorder_window.title("Recorder")
        recorder_window.geometry("400x300")
        tk.Label(recorder_window, text="Welcome to the world of AI").pack(pady=10)

# Main application start
if __name__ == "__main__":
    root = tk.Tk()
    login_page = LoginPage(root)
    root.mainloop()

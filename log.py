import tkinter as tk
from tkinter import messagebox
import os
import hashlib
import subprocess

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_answer(answer):
    return hashlib.sha256(answer.encode()).hexdigest()

def register():
    reg_window = tk.Toplevel(root)
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

def login():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        try:
            with open(f"users/{username}.txt", "r") as file:
                lines = file.readlines()
                stored_password = lines[0].strip()
                if stored_password == hash_password(password):
                    messagebox.showinfo("Login Success", "Welcome!")
                    root.withdraw()
                    # Launch the screen recording script
                    subprocess.Popen(["python", "screen_recorder.py"])
                    root.quit()
                else:
                    messagebox.showerror("Login Failed", "Invalid username or password")
        except FileNotFoundError:
            messagebox.showerror("Login Failed", "User not found")
    else:
        messagebox.showerror("Error", "Both fields are required!")

def open_reset_window():
    reset_window = tk.Toplevel(root)
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

root = tk.Tk()
root.title("Login Page")
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.configure(bg="#282c34")
tk.Label(root, text="Language Translator", font=("Arial", 32), bg="#282c34", fg="#61dafb").pack(pady=10)
tk.Label(root, text="Login", font=("Arial", 24), bg="#282c34", fg="#61dafb").pack(pady=50)
tk.Label(root, text="Username:", font=("Arial", 14), bg="#282c34", fg="white").pack(pady=10)
username_entry = tk.Entry(root, font=("Arial", 14))
username_entry.pack(pady=10, ipadx=50)
tk.Label(root, text="Password:", font=("Arial", 14), bg="#282c34", fg="white").pack(pady=10)
password_entry = tk.Entry(root, show="*", font=("Arial", 14))
password_entry.pack(pady=10, ipadx=50)
tk.Button(root, text="Login", font=("Arial", 14), bg="#61dafb", command=login).pack(pady=20)
tk.Button(root, text="Register", font=("Arial", 14), bg="#61dafb", command=register).pack(pady=10)
tk.Button(root, text="Forgot Password/Change Password", font=("Arial", 14), bg="#61dafb", command=open_reset_window).pack(pady=10)
root.mainloop()
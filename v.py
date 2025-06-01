import os
import tkinter as tk
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Directory where model and tokenizer are stored
model_dir = "./gpt2_local"

# Check if model and tokenizer are already downloaded, else download them
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
    print("Downloading model...")
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    # Save locally
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    print("Model downloaded and saved locally.")
else:
    print("Loading model from local storage...")
    model = GPT2LMHeadModel.from_pretrained(model_dir)
    tokenizer = GPT2Tokenizer.from_pretrained(model_dir)
    print("Model loaded from local storage.")

# Define text generation function
def generate_text():
    prompt = user_input.get()
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs['input_ids'], max_length=100)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    output_label.config(text=generated_text)

# Create GUI
root = tk.Tk()
root.title("AI Text Generator (Offline)")

# Create user input field
user_input = tk.Entry(root, width=50)
user_input.pack()

# Create generate button
generate_button = tk.Button(root, text="Generate", command=generate_text)
generate_button.pack()

# Create label to display generated text
output_label = tk.Label(root, text="", wraplength=500)
output_label.pack()

# Start the GUI loop
root.mainloop()

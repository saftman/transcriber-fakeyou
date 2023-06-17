import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import speech_recognition as sr
from tqdm import tqdm

def transcribe_audio_files(folder_path, output_file, language, progress_label):
    r = sr.Recognizer()

    files = os.listdir(folder_path)

    with open(output_file, "w") as f:
        progress = 0
        total_files = len(files)
        progress_label.config(text=f"{progress}% Done {progress} / {total_files}")

        for file in tqdm(files, desc="Transcribing", unit="file"):
            if file.endswith(".wav"):
                file_path = os.path.join(folder_path, file)
                with sr.AudioFile(file_path) as source:
                    audio = r.record(source)
                    try:
                        text = r.recognize_google(audio, language=language)
                        first_word = text.split()[0].capitalize()
                        rest_of_sentence = " ".join(text.split()[1:])
                        if rest_of_sentence.endswith("?"):
                            transcript = f"wavs/{file}| {first_word} {rest_of_sentence}"
                        else:
                            transcript = f"wavs/{file}| {first_word} {rest_of_sentence}."
                        f.write(transcript + "\n")
                    except sr.UnknownValueError:
                        print(f"Unable to transcribe {file_path}")
                    except sr.RequestError as e:
                        print(f"Error occurred while transcribing {file_path}: {e}")

            progress += 1
            progress_percentage = (progress / total_files) * 100
            progress_label.config(text=f"{progress_percentage:.2f}% Done {progress} / {total_files}")
            root.update_idletasks()

def select_folder():
    folder_path = filedialog.askdirectory(title="Select Folder Containing WAV Files", parent=root)
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(tk.END, folder_path)

def select_output_file():
    output_file_path = filedialog.asksaveasfilename(
        title="Select Output File",
        parent=root,
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )
    if output_file_path:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(tk.END, output_file_path)

def start_transcription():
    folder_path = folder_entry.get()
    output_file_path = output_file_entry.get()
    language = language_var.get()

    if not folder_path:
        messagebox.showerror("Error", "No folder selected.")
        return

    if not output_file_path:
        messagebox.showerror("Error", "No output file selected.")
        return

    progress_label.config(text="Transcribing...")
    root.update_idletasks()

    transcribe_audio_files(folder_path, output_file_path, language, progress_label)

    progress_label.config(text="Transcription Complete")
    messagebox.showinfo("Transcription Complete", f"Transcriptions saved to {output_file_path}")

# Create Tkinter root window
root = tk.Tk()
root.title("Audio Transcription")
root.geometry("500x400")
root.configure(bg="lightgray")

# Input Folder Selection
folder_label = tk.Label(root, text="Input Folder (WAVs):", bg="lightgray", font=("Arial", 12))
folder_label.pack(pady=10)
folder_frame = tk.Frame(root, bg="lightgray")
folder_frame.pack()
folder_entry = tk.Entry(folder_frame, width=30, font=("Arial", 10))
folder_entry.pack(side=tk.LEFT, padx=5)
folder_button = tk.Button(folder_frame, text="Browse", command=select_folder, font=("Arial", 10))
folder_button.pack(side=tk.LEFT)

# Output File Selection
output_file_label = tk.Label(root, text="Output File:", bg="lightgray", font=("Arial", 12))
output_file_label.pack(pady=10)
output_frame = tk.Frame(root, bg="lightgray")
output_frame.pack()
output_file_entry = tk.Entry(output_frame, width=30, font=("Arial", 10))
output_file_entry.pack(side=tk.LEFT, padx=5)
output_file_button = tk.Button(output_frame, text="Browse", command=select_output_file, font=("Arial", 10))
output_file_button.pack(side=tk.LEFT)

# Language Selection
language_label = tk.Label(root, text="Language:", bg="lightgray", font=("Arial", 12))
language_label.pack(pady=10)
language_frame = tk.Frame(root, bg="lightgray")
language_frame.pack()
language_var = tk.StringVar(root, "en-us")
language_dropdown = tk.OptionMenu(language_frame, language_var, "en-us", "en-gb", "de", "fr", "es")
language_dropdown.config(font=("Arial", 10))
language_dropdown.pack(padx=10, pady=5)

# Progress Label
progress_label = tk.Label(root, text="", bg="lightgray", font=("Arial", 12))
progress_label.pack(pady=10)

# Start Transcription Button
start_button = tk.Button(root, text="Start Transcription", command=start_transcription, font=("Arial", 12))
start_button.pack(pady=10)

root.mainloop()

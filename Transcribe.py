import sys
import os
import speech_recognition as sr
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QComboBox,
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import threading

def transcribe_file(args):
    file, folder_path, language = args
    r = sr.Recognizer()
    file_path = os.path.join(folder_path, file)
    try:
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language=language)
            first_word = text.split()[0].capitalize()
            rest_of_sentence = " ".join(text.split()[1:])
            if rest_of_sentence.endswith("?"):
                transcript = f"wavs/{file}|{first_word} {rest_of_sentence}"
            else:
                transcript = f"wavs/{file}|{first_word} {rest_of_sentence}."
            return transcript
    except sr.UnknownValueError:
        return f"Unable to transcribe {file_path}"
    except sr.RequestError as e:
        return f"Error occurred while transcribing {file_path}: {e}"

class TranscriptionThread(QThread):
    finished = pyqtSignal()

    def __init__(self, folder_path, output_file, language):
        super().__init__()
        self.folder_path = folder_path
        self.output_file = output_file
        self.language = language

    def run(self):
        files = [(file, self.folder_path, self.language) for file in os.listdir(self.folder_path) if file.endswith(".wav")]

        with Pool(cpu_count()) as pool:
            results = list(tqdm(pool.imap(transcribe_file, files, chunksize=1),
                                total=len(files), desc="Transcribing"))

        with open(self.output_file, "w") as f:
            for result in results:
                f.write(result + "\n")

        self.finished.emit()

class AudioTranscriptionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Audio Transcription')
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon('icon.png'))

        # Dark mode
        self.dark_mode = False
        self.palette_light = self.palette()
        self.palette_dark = QPalette()
        self.palette_dark.setColor(QPalette.Window, QColor(45, 45, 45))
        self.palette_dark.setColor(QPalette.WindowText, Qt.white)
        self.palette_dark.setColor(QPalette.Button, QColor(45, 45, 45))
        self.palette_dark.setColor(QPalette.ButtonText, Qt.white)
        self.palette_dark.setColor(QPalette.Highlight, QColor(100, 100, 100))
        self.setPalette(self.palette_light)

        self.folder_label = QLabel('Input Folder (WAVs):', self)
        self.folder_label.setGeometry(20, 20, 200, 20)

        self.folder_entry = QLineEdit(self)
        self.folder_entry.setGeometry(20, 50, 300, 30)

        self.folder_button = QPushButton('Browse', self)
        self.folder_button.setGeometry(330, 50, 100, 30)
        self.folder_button.clicked.connect(self.select_folder)
        self.folder_button.setStyleSheet('border-radius: 15px;')

        self.output_label = QLabel('Output File:', self)
        self.output_label.setGeometry(20, 100, 200, 20)

        self.output_entry = QLineEdit(self)
        self.output_entry.setGeometry(20, 130, 300, 30)

        self.output_button = QPushButton('Browse', self)
        self.output_button.setGeometry(330, 130, 100, 30)
        self.output_button.clicked.connect(self.select_output_file)
        self.output_button.setStyleSheet('border-radius: 15px;')

        self.language_label = QLabel('Language:', self)
        self.language_label.setGeometry(20, 180, 200, 20)

        self.language_dropdown = QComboBox(self)
        self.language_dropdown.setGeometry(20, 210, 150, 30)
        self.language_dropdown.addItems(["en-us", "en-gb", "de", "fr", "es"])

        self.progress_label = QLabel('', self)
        self.progress_label.setGeometry(20, 260, 300, 20)

        self.transcribe_button = QPushButton('Start Transcription', self)
        self.transcribe_button.setGeometry(20, 300, 200, 40)
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.transcribe_button.setStyleSheet('border-radius: 20px; background-color: #007ACC; color: white;')

        self.dark_mode_button = QPushButton('Dark Mode', self)
        self.dark_mode_button.setGeometry(20, 350, 100, 30)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.dark_mode_button.setStyleSheet('border-radius: 15px; background-color: #303030; color: white;')

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setPalette(self.palette_dark)
        else:
            self.setPalette(self.palette_light)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder Containing WAV Files')
        if folder_path:
            self.folder_entry.setText(folder_path)

    def select_output_file(self):
        output_file_path, _ = QFileDialog.getSaveFileName(self, 'Select Output File', '', 'Text Files (*.txt)')
        if output_file_path:
            self.output_entry.setText(output_file_path)

    def start_transcription(self):
        folder_path = self.folder_entry.text()
        output_file_path = self.output_entry.text()
        language = self.language_dropdown.currentText()

        if not folder_path:
            self.progress_label.setText("Error: No folder selected.")
            return

        if not output_file_path:
            self.progress_label.setText("Error: No output file selected.")
            return

        self.progress_label.setText("Transcribing...")

        # Create and start the transcription thread
        self.transcription_thread = TranscriptionThread(folder_path, output_file_path, language)
        self.transcription_thread.finished.connect(self.transcription_complete)
        self.transcription_thread.start()

    def transcription_complete(self):
        self.progress_label.setText("Transcription Complete")
        os.startfile(self.folder_entry.text())  # Open the folder when done

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AudioTranscriptionApp()
    ex.show()
    sys.exit(app.exec_())

from PyPDF2 import PdfReader
from google.cloud import texttospeech
from google.api_core.exceptions import InvalidArgument
import tkinter as tk
from tkinter import filedialog as fd
import vlc

# Constants for widget padding
XPAD = 5
YPAD = 5

# Path for mp3 file
mp3_path = "/home/kteelee/PycharmProjects/pdf text to speech/output.mp3"


# Create a GUI window where user can select a pdf
class SelectWindow:

    def __init__(self, master):
        self.master = master
        self.filename = ""

        # Welcome message and UI buttons
        self.select_label = tk.Label(self.master, text="Welcome to the Text-to-Speech Convertor.\nSelect the pdf file"
                                                       " you wish to convert.")
        self.select_label.grid(column=0, row=0, padx=XPAD, pady=YPAD)
        self.file_button = tk.Button(self.master, text="Select PDF", command=self.open_file)
        self.file_button.grid(column=0, row=1, padx=XPAD, pady=YPAD)
        self.pdf_label = tk.Label(self.master, text="")
        self.pdf_label.grid(column=0, row=2, padx=XPAD, pady=YPAD)
        self.convert_button = tk.Button(self.master, text="Convert text to speech", command=self.convert_text_to_speech)
        self.convert_button.grid(column=0, row=3, padx=XPAD, pady=YPAD)

    def open_file(self):
        """Asks user to select a file to open"""
        self.filename = fd.askopenfilename(
            title="Select a File",
            initialdir="/home/",
            filetypes=[("PDF", "*.pdf")])
        self.pdf_label.config(text=f"PDF selected:\n{self.filename}", wraplength=460)

    def convert_text_to_speech(self):
        """Sends API request to Google TTS"""
        text = self.get_text_from_pdf(self.filename)
        try:
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(language_code="en-CA",
                                                      ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            with open("output.mp3", "wb") as out:
                out.write(response.audio_content)
            self.open_player()
        except InvalidArgument:
            self.handle_error("length")
        except:
            self.handle_error("general")


    def get_text_from_pdf(self, path):
        """Gets text from pdf"""
        page_texts = []

        reader = PdfReader(path)
        number_of_pages = len(reader.pages)
        for i in range(0, number_of_pages):
            page = reader.pages[i]
            text = page.extract_text()
            text = text.replace("\n", " ")
            page_texts.append(text)

        text = " ".join(page_texts)
        return text

    def open_player(self):
        """Opens window to play mp3 as a new window"""
        self.player_window = tk.Toplevel(self.master)
        self.app = PlayerWindow(self.player_window)

    def handle_error(self, error_type):
        """Opens a window with an error message"""
        self.error_window = tk.Toplevel(self.master)
        self.app = ErrorWindow(self.error_window, error_type)


class PlayerWindow:

    def __init__(self, master):

        # Set up the window
        self.master = master
        self.master.title("Playback text to speech")
        self.master.minsize(width=200, height=200)
        self.master.config(padx=20, pady=20)
        self.media = vlc.MediaPlayer(mp3_path)

        # Create buttons
        self.play_button = tk.Button(self.master, text="Play", command=self.play_mp3)
        self.play_button.grid(column=0, row=0, padx=XPAD, pady=YPAD)
        self.pause_button = tk.Button(self.master, text="Pause", command=self.pause)
        self.pause_button.grid(column=0, row=1, padx=XPAD, pady=YPAD)
        self.stop_button = tk.Button(self.master, text="Stop", command=self.stop)
        self.stop_button.grid(column=0, row=2, padx=XPAD, pady=YPAD)

    def play_mp3(self):
        self.media.play()

    def pause(self):
        self.media.pause()

    def stop(self):
        self.media.stop()


class ErrorWindow:

    def __init__(self, master, error_type):

        # Set up the window
        self.master = master
        self.master.title("Playback text to speech")
        self.master.minsize(width=400, height=200)
        self.master.config(padx=20, pady=20)

        # Label with error message
        self.error_type = error_type
        if self.error_type == "length":
            self.label_text = "Your input is invalid. This error may occur if your text file is too long."
        else:
            self.label_text = "An error has occurred. Please try again later."
        self.error_label = tk.Label(self.master, text=self.label_text)
        self.error_label.grid(row=0, column=0)


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = SelectWindow(root)
    root.title("Convert PDF text to speech")
    root.minsize(width=500, height=500)
    root.config(padx=20, pady=20)
    root.mainloop()

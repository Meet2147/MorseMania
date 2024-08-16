from fastapi import FastAPI, HTTPException, File, UploadFile
from pydub import AudioSegment
from gtts import gTTS
import io
import os
from fastapi.responses import FileResponse

app = FastAPI()

# Directory to save audio files
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ', ': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-',
    '(': '-.--.', ')': '-.--.-', ' ': '/'
}

# Reverse dictionary for Morse to character
CHARACTER_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

@app.post("/to_morse/")
async def to_morse(text: str):
    try:
        morse_code = ' '.join(MORSE_CODE_DICT[char.upper()] for char in text)
        
        # Generate Morse code audio
        morse_audio = AudioSegment.silent(duration=0)
        for symbol in morse_code:
            if symbol == '.':
                morse_audio += AudioSegment.from_file("data/dot.ogg", format="ogg") + AudioSegment.silent(duration=200)
            elif symbol == '-':
                morse_audio += AudioSegment.from_file("data/dash.ogg", format="ogg") + AudioSegment.silent(duration=200)
            elif symbol == ' ':
                morse_audio += AudioSegment.silent(duration=600)  # Space between words

        # Save the generated audio file
        audio_filename = f"{AUDIO_DIR}/morse_code_audio.mp3"
        morse_audio.export(audio_filename, format="mp3")
        
        return {"morse_code": morse_code, "audio_file": f"/audio/{audio_filename}"}
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid character in input")

@app.post("/from_morse/")
async def from_morse(morse_code: str):
    try:
        text = ''.join(CHARACTER_DICT[code] for code in morse_code.split(' '))
        
        # Convert text to speech
        tts = gTTS(text, lang='en')
        audio_filename = f"{AUDIO_DIR}/text_audio.mp3"
        tts.save(audio_filename)
        
        return {"text": text, "audio_file": f"/audio/{audio_filename}"}
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid Morse code input")

# Serve the static audio files
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

# To run the server, use the following command in your terminal
# uvicorn main:app --reload

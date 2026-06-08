import aubio
import numpy as np
import sounddevice as sd
import keyboard
import queue

# --- CONFIGURATION ---
NOTE_TO_KEY_MAP = {
    "E2": "1", "A2": "2", "D3": "3", "G3": "4", "B3": "5", "E4": "6",
}

SAMPLERATE = 44100
WIN_S = 2048
HOP_S = 512

# Thread-safe queue to pass notes from audio thread to main thread
note_queue = queue.Queue()

# Initialize Pitch Detection
pitch_o = aubio.pitch("default", WIN_S, HOP_S, SAMPLERATE)
pitch_o.set_unit("Hz")
pitch_o.set_silence(-40) 

def frequency_to_note(freq):
    if freq < 20: return None
    # Standard formula for MIDI Note Number
    midi = 12 * np.log2(freq / 440.0) + 69
    n = int(round(midi))
    
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return f"{names[n % 12]}{n // 12 - 1}"

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    samples = indata[:, 0].astype(np.float32)
    pitch = pitch_o(samples)[0]
    
    if pitch > 0:
        note = frequency_to_note(pitch)
        if note in NOTE_TO_KEY_MAP:
            note_queue.put(note)

print("Listening... Press Ctrl+C to stop.")

# Open the stream
try:
    with sd.InputStream(channels=1, callback=audio_callback, samplerate=SAMPLERATE, blocksize=HOP_S):
        while True:
            # Process the keyboard presses in the main thread
            try:
                note = note_queue.get(block=False)
                target_key = NOTE_TO_KEY_MAP[note]
                keyboard.press_and_release(target_key)
                print(f"Detected: {note} -> Pressed: {target_key}")
            except queue.Empty:
                continue
except KeyboardInterrupt:
    print("\nStopped.")
import os
import subprocess
import whisper
from datetime import timedelta

def extract_clip(input_file, output_file, start_time, duration=20):
    """Extracts a 20-second clip from the source audio file using FFmpeg."""
    try:
        # FFmpeg command
        command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-ss", str(timedelta(seconds=start_time)),
            "-t", str(duration),
            "-acodec", "copy",
            output_file,
        ]
        subprocess.run(command, check=True)

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        raise

def transcribe_audio(audio_file):
    """Transcribes audio using Whisper AI."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result.get("text", "")

def get_transcription(input_file, timestamp):
    # Resolves issues with homebrew installations not on PATH
    os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin" + os.pathsep + "/usr/local/bin"

    # Temp file for extracted audio
    temp_clip = "temp_clip.mp3"

    try:
        extract_clip(input_file, temp_clip, timestamp)
        transcription = transcribe_audio(temp_clip)
    finally:
        # Delete temp file
        if os.path.exists(temp_clip):
            os.remove(temp_clip)
    
    return transcription

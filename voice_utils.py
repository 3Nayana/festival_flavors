# app/voice_utils.py

import speech_recognition as sr

def transcribe_audio(audio_file_path):
    """
    Transcribes speech from an audio file using Google's Speech Recognition API.

    Args:
        audio_file_path (str): Path to the audio file to transcribe.

    Returns:
        str: Transcribed text, or an error message.
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)

        # Perform speech recognition using Google
        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        return "⚠️ Sorry, could not understand the audio."

    except sr.RequestError as e:
        return f"❌ API request error: {e}"

    except FileNotFoundError:
        return "❗ Audio file not found."

    except Exception as e:
        return f"❗ An unexpected error occurred during transcription: {e}"

from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
import speech_recognition as sr

def transliterate_text(text):
    lines = text.strip().splitlines()
    return "\n".join([transliterate(line.strip(), ITRANS, DEVANAGARI) for line in lines if line.strip()])

def get_speech_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak now.")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "[Could not understand audio]"
    except sr.RequestError:
        return "[Speech service unavailable]"

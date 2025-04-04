##pip install pyaudio
##pip install SpeechRecognition
import speech_recognition as sr

def detectar_voz():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # Ajustar al ruido ambiente de manera más rápida
        recognizer.adjust_for_ambient_noise(source, duration=0.3)

        try:
            # Escuchar con un tiempo de espera más corto
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)

            # Reconocer el texto a partir del audio
            texto = recognizer.recognize_google(audio, language="es-ES")
            return texto  # Devuelve el texto reconocido

        except sr.WaitTimeoutError:
            return "ERROR: No se detectó voz a tiempo."
        except sr.UnknownValueError:
            return "ERROR: No se entendió el audio."
        except sr.RequestError as e:
            return f"ERROR: Error con el servicio: {e}"

if __name__ == "__main__":
    print(detectar_voz())

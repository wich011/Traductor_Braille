import pyttsx3

# Inicializar el motor de texto a voz
engine = pyttsx3.init()

# Establecer la voz directamente
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0')

# Configurar velocidad y volumen
engine.setProperty('rate', 135)   
engine.setProperty('volume', 1.0) 

# Texto a dictar
texto = "Esta es una prueba de dictado con una velocidad extremadamente lenta para verificar la claridad de la pronunciación."

# Ejecutar el dictado
engine.say(texto)
engine.runAndWait()



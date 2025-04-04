// Mapeo de caracteres para Braille Unicode
const brailleMap = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
    'á': '⠷', 'é': '⠮', 'í': '⠌', 'ó': '⠬', 'ú': '⠾', 'ü': '⠳', 'ñ': '⠻',
    '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲', '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦', '9': '⠔',
    '.': '⠄', ',': '⠠', ';': '⠰', ':': '⠱', '?': '⠹', '!': '⠮', '"': '⠐', "'": '⠄', '-': '⠤', ' ': ' '
};

// Mapeo inverso (braille a texto)
const inverseBrailleMap = {};
for (const [key, value] of Object.entries(brailleMap)) {
    inverseBrailleMap[value] = key;
}

// Cambiar entre pestañas
function switchTab(index) {
    const tabs = document.querySelectorAll('.tab');
    const sections = document.querySelectorAll('.section');

    tabs.forEach(tab => tab.classList.remove('active'));
    sections.forEach(section => section.classList.remove('active'));

    tabs[index].classList.add('active');
    sections[index].classList.add('active');
}

// Configuración de elementos DOM
const uploadForm = document.getElementById('uploadForm');
const imageInput = document.getElementById('imageInput');
const captureButton = document.getElementById('captureButton');
const imagePreview = document.getElementById('imagePreview');
const translateButton = document.getElementById('translateButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const spanishOutput = document.getElementById('spanishOutput');
const spanishInput = document.getElementById('spanishInput');
const convertToBrailleButton = document.getElementById('convertToBrailleButton');
const brailleOutput = document.getElementById('brailleOutput');
const translationResult = document.getElementById('translationResult');
const detectarVoz = document.getElementById('detectarVoz');
const estadoTexto = document.getElementById('estadoTexto');
let escuchando = false;


// Inicialización y ocultar resultado
translationResult.style.display = 'none';

// Previsualizar imagen seleccionada
imageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();

        reader.onload = function(e) {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Imagen seleccionada">`;
        };

        reader.readAsDataURL(file);
    }
});

// Capturar imagen desde la cámara
captureButton.addEventListener('click', function() {
    // Crear elementos para la captura
    const videoElement = document.createElement('video');
    const canvasElement = document.createElement('canvas');

    // Configurar video y canvas
    videoElement.style.display = 'block';
    videoElement.style.maxWidth = '100%';
    videoElement.autoplay = true;

    // Reemplazar preview con video
    imagePreview.innerHTML = '';
    imagePreview.appendChild(videoElement);

    // Agregar botón para tomar foto
    const takePhotoButton = document.createElement('button');
    takePhotoButton.textContent = 'Tomar foto';
    takePhotoButton.style.marginTop = '10px';
    imagePreview.appendChild(takePhotoButton);

    // Acceder a la cámara
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement.srcObject = stream;

            // Configurar evento para tomar foto
            takePhotoButton.addEventListener('click', () => {
                // Configurar canvas
                canvasElement.width = videoElement.videoWidth;
                canvasElement.height = videoElement.videoHeight;

                // Dibujar frame del video en canvas
                const ctx = canvasElement.getContext('2d');
                ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

                // Convertir canvas a imagen
                const imageDataUrl = canvasElement.toDataURL('image/png');

                // Detener stream de video
                stream.getTracks().forEach(track => track.stop());

                // Mostrar imagen capturada
                imagePreview.innerHTML = `<img src="${imageDataUrl}" alt="Imagen capturada">`;

                // Crear un objeto File a partir de la imagen para uso posterior
                fetch(imageDataUrl)
                    .then(res => res.blob())
                    .then(blob => {
                        const file = new File([blob], "captured-image.png", { type: "image/png" });

                        // Crear un nuevo FileList (simulado)
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(file);
                        imageInput.files = dataTransfer.files;
                    });
            });
        })
        .catch(error => {
            imagePreview.innerHTML = `<p class="error">Error al acceder a la cámara: ${error.message}</p>`;
        });
});

// Traducir imagen de braille a texto
// ... (resto de tu código)

uploadForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const selectedFile = imageInput.files[0];

    if (!selectedFile) {
        alert('Por favor selecciona una imagen primero.');
        return;
    }

    const formData = new FormData();
    formData.append('image', selectedFile);

    loadingIndicator.classList.add('active');
    translationResult.style.display = 'none';

    fetch('/traducir', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.text()) // Cambiado a response.text()
    .then(data => {
        spanishOutput.textContent = data;
        translationResult.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        spanishOutput.textContent = 'Error al traducir la imagen.';
        translationResult.style.display = 'block';
    })
    .finally(() => {
        loadingIndicator.classList.remove('active');
    });
});


// Convertir texto español a braille
convertToBrailleButton.addEventListener('click', function() {
    const spanishText = spanishInput.value.toLowerCase();

    if (!spanishText) {
        alert('Por favor escribe algo de texto primero');
        return;
    }

    // Convertir a braille
    let brailleText = '';
    for (let i = 0; i < spanishText.length; i++) {
        const char = spanishText[i];
        if (brailleMap[char]) {
            brailleText += brailleMap[char];
        } else {
            // Si no encontramos traducción, mantener el carácter original
            brailleText += char;
        }
    }

    // Mostrar texto en braille
    brailleOutput.innerHTML = `<p>${brailleText}</p>`;
});

const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Función para generar un sonido de beep fuerte
function playBeep() {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    // Configurar la frecuencia del oscilador (sonido de beep)
    oscillator.type = 'sine';  // Tipo de onda: "sine" es un tono suave
    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime);  // Frecuencia de 1000 Hz

    // Configurar el volumen (aumentado para hacerlo más fuerte)
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);  // Volumen al máximo

    // Conectar el oscilador al nodo de ganancia, y luego al destino de salida (los altavoces)
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    // Iniciar el sonido
    oscillator.start();
    // Detener el sonido después de 0.2 segundos
    oscillator.stop(audioContext.currentTime + 0.2);
}

// Asegurémonos de que el audioContext se active en respuesta a la interacción del usuario (necesario en algunos navegadores)
document.body.addEventListener('click', () => {
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
});

// Al hacer clic en el botón, se reproduce el sonido
detectarVoz.addEventListener('click', function() {
    if (!escuchando) {
        iniciarEscucha();
    } else {
        detenerEscucha();
    }
});

function iniciarEscucha() {
    escuchando = true;
    // Cambiar el texto del botón
    detectarVoz.innerHTML = "🎙️ Detener Dictado";
    spanishInput.value = "Cargando...";  // Mostrar texto de espera

    setTimeout(function() {
        playBeep();  // Reproducir el sonido después de 500 ms
        document.getElementById('status').innerText = 'Sonido reproducido.';
    }, 500);  // Retraso de 500 milisegundos (0.5 segundos)

    fetch('/detectar-voz')  // Llamar al servidor backend
        .then(response => response.text())  // Obtener el texto de la respuesta
        .then(data => {
            if (!data || data.trim() === "") {
                spanishInput.value = "No se reconoció voz.";
                brailleOutput.innerHTML = "<p style='color: red;'>No se reconoció ningún sonido.</p>";
            } else {
                spanishInput.value = data.trim();  // Mostrar texto reconocido en español
                brailleOutput.innerHTML = `<p>${textToBraille(data.trim())}</p>`;  // Convertir a Braille
            }
        })
        .catch(error => {
            console.error('Error:', error);
            spanishInput.value = "Error en el procesamiento.";
            brailleOutput.innerHTML = "<p style='color: red;'>Ocurrió un error.</p>";
        });
}

function detenerEscucha() {
    escuchando = false;
    detectarVoz.innerHTML = "🎤 Iniciar Dictado";
    estadoTexto.innerText = ""; // Borra el texto de estado (si lo usas)
}

// Función para convertir el texto en Braille
function textToBraille(text) {
    const brailleMap = {
            'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
            'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
            'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
            'á': '⠷', 'é': '⠮', 'í': '⠌', 'ó': '⠬', 'ú': '⠾', 'ü': '⠳', 'ñ': '⠻',
            '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲', '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦', '9': '⠔',
            '.': '⠄', ',': '⠠', ';': '⠰', ':': '⠱', '?': '⠹', '!': '⠮', '"': '⠐', "'": '⠄', '-': '⠤', ' ': ' '
        };
    return text.split('').map(char => brailleMap[char.toLowerCase()] || char).join('');
}

document.getElementById('readTranslationButton').addEventListener('click', () => {
    const texto = document.getElementById('spanishOutput').innerText;
    if (texto.trim() === "") {
        alert("No hay texto para leer");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = "es-ES"; // Idioma español
    window.speechSynthesis.speak(utterance);
});


document.getElementById('stopReadingButton').addEventListener('click', () => {
    window.speechSynthesis.cancel();
});

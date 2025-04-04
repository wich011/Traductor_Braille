const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const multer = require('multer');
const path = require('path');

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Configuración de Multer para la subida de archivos
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, path.join(__dirname, 'assets')); // Ruta para guardar los archivos
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        const ext = path.extname(file.originalname);
        cb(null, file.fieldname + '-' + uniqueSuffix + ext); // Nombre del archivo
    }
});

const upload = multer({ storage: storage });

app.use(express.static(path.join(__dirname)));

app.post('/traducir', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No se subió ningún archivo.');
    }

    const imagePath = req.file.path;
    console.log("Ruta de la imagen:", imagePath);
    const pythonScriptPath = 'traductor_braille.py';

    exec(`python "${pythonScriptPath}" "${imagePath}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).send(stderr);
        }
        console.log(`stdout: ${stdout}`);
        res.send(stdout);
    });
});

app.get('/detectar-voz', (req, res) => {
    console.log("Iniciando detección de voz...");
    const pythonScriptPath = 'detector_voz.py';

    exec(`python "${pythonScriptPath}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error al ejecutar el script: ${error}`);
            return res.status(500).send("Error al procesar la voz.");
        }

        const salida = stdout.trim();
        console.log(`Resultado del script: ${salida}`);

        if (salida.startsWith("ERROR:")) {
            return res.send("");  // No devolvemos nada si hay error
        }

        res.send(salida);  // Solo texto reconocido
    });
});

app.post('/dictar-texto', (req, res) => {
    const texto = req.body.texto;
    if (!texto) {
        return res.status(400).send('Falta el texto a dictar.');
    }

    const pythonScriptPath = 'dictado_voz.py';
    exec(`python "${pythonScriptPath}" "${texto}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error ejecutando dictado_voz.py: ${error}`);
            return res.status(500).send(stderr);
        }
        console.log(`Dictado de voz completado.`);
        res.send({ mensaje: "Texto dictado exitosamente" });
    });
});


app.listen(port, () => {
    console.log(`Servidor escuchando en http://localhost:${port}`);
});
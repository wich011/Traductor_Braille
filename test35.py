import cv2
import imutils
import numpy as np
from sklearn.cluster import DBSCAN
import random

def main():
    # PASO 1: CARGAR IMAGEN
    image_path = "braille5.jpeg"
    orig = cv2.imread(image_path)
    if orig is None:
        raise ValueError(f"No se pudo cargar la imagen desde {image_path}")
    orig = imutils.resize(orig, height=500)
    #cv2.imshow("1. Imagen Original", orig)
    #cv2.waitKey(0)

    # PASO 2: PREPROCESAMIENTO
    def preprocesar_imagen(img):
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("2.1. Imagen en escala de grises", gray)
        #cv2.waitKey(0)
        
        # Umbral adaptativo
        thresh = cv2.adaptiveThreshold(gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        #cv2.imshow("2.2. Imagen Umbralizada", thresh)
        #cv2.waitKey(0)
        
        # Operación morfológica CLOSE
        kernel = np.ones((3,3), np.uint8)
        morphed_close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        #cv2.imshow("2.3. Imagen después de CLOSE", morphed_close)
        #cv2.waitKey(0)
        
        # Operación morfológica OPEN
        morphed_open = cv2.morphologyEx(morphed_close, cv2.MORPH_OPEN, kernel)
        #cv2.imshow("2.4. Imagen después de OPEN", morphed_open)
        #cv2.waitKey(0)
        
        return morphed_open

    processed = preprocesar_imagen(orig.copy())

    # PASO 3: DETECTAR ÁREA BRAILLE
    def detectar_area_braille(img):
        cnts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Visualizar todos los contornos detectados
        img_contornos = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_contornos, cnts, -1, (0,0,255), 1)
        #cv2.imshow("3.1. Todos los contornos", img_contornos)
        #cv2.waitKey(0)
        
        puntos_braille = []
        for c in cnts:
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            # Filtrar contornos pequeños (conforma a puntos Braille)
            if 5 < area < 50 and abs(w - h) < 10:
                puntos_braille.append(c)
        
        # Visualizar solo los contornos filtrados
        img_filtrado = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_filtrado, puntos_braille, -1, (0,255,0), 2)
        #cv2.imshow("3.2. Contornos filtrados", img_filtrado)
        #cv2.waitKey(0)
        
        if not puntos_braille:
            raise ValueError("No se detectaron puntos Braille.")
        
        # Calcular el bounding box global de los puntos
        puntos_combinados = np.vstack(puntos_braille)
        x, y, w, h = cv2.boundingRect(puntos_combinados)
        return (x, y, w, h)

    try:
        x, y, w, h = detectar_area_braille(processed)
    except ValueError as e:
        print(e)
        return

    # Recortar el área Braille
    def recortar_area_braille(img, x, y, w, h, margen=10):
        # Obtener dimensiones de la imagen
        img_h, img_w = img.shape[:2]

        # Aplicar margen a las coordenadas
        x1 = max(0, x - margen)  # Asegurar que no sea menor que 0
        y1 = max(0, y - margen)  # Asegurar que no sea menor que 0
        x2 = min(img_w, x + w + margen)  # Asegurar que no exceda el ancho de la imagen
        y2 = min(img_h, y + h + margen)  # Asegurar que no exceda el alto de la imagen

        # Recortar la región de interés (ROI)
        roi = img[y1:y2, x1:x2]

        return roi

    cropped = recortar_area_braille(processed, x, y, w, h)
    #cv2.imshow("4. Área recortada", cropped)
    #cv2.waitKey(0)

    # PASO 5: CONVERTIR A TEXTO CON CLUSTERING Y GRID, CON VISUALIZACIONES
    def convertir_a_unicode_y_traducir(img):
        # Detectar contornos en el área recortada
        cnts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        img_contornos_recortados = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_contornos_recortados, cnts, -1, (0,255,0), 1)
        #cv2.imshow("5.1. Contornos en área recortada", img_contornos_recortados)
        #cv2.waitKey(0)
        
        # Filtrar puntos Braille y calcular el centro de cada uno
        puntos_braille = []
        for c in cnts:
            area = cv2.contourArea(c)
            x_c, y_c, w_c, h_c = cv2.boundingRect(c)
            if 5 < area < 50 and abs(w_c - h_c) < 10:
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    puntos_braille.append((cx, cy))
        
        if not puntos_braille:
            print("No se detectaron puntos.")
            return

        # Visualizar los centros de los puntos detectados
        debug_puntos = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        for (cx, cy) in puntos_braille:
            cv2.circle(debug_puntos, (cx, cy), 2, (0,0,255), -1)
        #cv2.imshow("5.2. Centros de puntos detectados", debug_puntos)
        #Scv2.waitKey(0)
        
        puntos = np.array(puntos_braille)
        # Calcular valor eps usando la distancia mediana entre vecinos
        if len(puntos) > 1:
            dists = []
            for i in range(len(puntos)):
                distances = np.linalg.norm(puntos[i] - puntos, axis=1)
                distances = np.sort(distances)[1:2]  # omitir cero
                dists.append(distances[0])
            median_dist = np.median(dists)
        else:
            median_dist = 5
        eps = median_dist * 2.5  

        # Aplicar DBSCAN para agrupar los puntos (cada grupo corresponde a una celda Braille)
        db = DBSCAN(eps=eps, min_samples=1)
        labels = db.fit_predict(puntos)
        
        # Visualizar los clusters detectados
        debug_clusters = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        colors = {}
        for label in np.unique(labels):
            colors[label] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        for (pt, label) in zip(puntos, labels):
            cv2.circle(debug_clusters, tuple(pt), 4, colors[label], -1)
            cv2.putText(debug_clusters, str(label), tuple(pt), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[label], 1)
        cv2.imshow("5.3. Clusters DBSCAN", debug_clusters)
        cv2.waitKey(0)

        # Organizar los puntos en clusters
        cell_clusters = {}
        for label, point in zip(labels, puntos):
            if label not in cell_clusters:
                cell_clusters[label] = []
            cell_clusters[label].append(point)
        
        # Diccionario para mapear patrones a carácter Braille
        braille_a_unicode = {
    # Letras minúsculas
    (1,0,0,0,0,0): '⠁',  # a
    (1,1,0,0,0,0): '⠃',  # b
    (1,0,0,1,0,0): '⠉',  # c
    (1,0,0,1,1,0): '⠙',  # d
    (1,0,0,0,1,0): '⠑',  # e
    (1,1,0,1,0,0): '⠋',  # f
    (1,1,0,1,1,0): '⠛',  # g
    (1,1,0,0,1,0): '⠓',  # h
    (0,1,0,1,0,0): '⠊',  # i
    (0,1,0,1,1,0): '⠚',  # j
    (1,0,1,0,0,0): '⠅',  # k
    (0,0,0,1,0,1): '⠅',  # k
    (1,1,1,0,0,0): '⠇',  # l
    (0,0,0,1,1,1): '⠇',  # l
    (1,0,1,1,0,0): '⠍',  # m
    (1,0,1,1,1,0): '⠝',  # n
    (1,0,1,0,1,0): '⠕',  # o
    (1,1,1,1,0,0): '⠏',  # p
    (1,1,1,1,1,0): '⠟',  # q
    (1,1,1,0,1,0): '⠗',  # r
    (0,1,1,1,0,0): '⠎',  # s
    (0,1,1,1,1,0): '⠞',  # t
    (1,0,1,0,0,1): '⠥',  # u
    (1,1,1,0,0,1): '⠧',  # v
    (0,1,0,1,1,1): '⠺',  # w
    (1,0,1,1,0,1): '⠭',  # x
    (1,0,1,1,1,1): '⠽',  # y
    (1,0,1,0,1,1): '⠵',  # z

    # Letras mayúsculas (precedidas por el indicador de mayúscula ⠠)
    (0,0,0,0,0,1): '⠠',  # Indicador de mayúscula
    # (El carácter real se obtiene combinando ⠠ con la letra minúscula)

    # # Números (precedidos por el indicador numérico ⠼)
    # (0,0,1,1,1,1): '⠼',  # Indicador numérico
    # # Los números se mapean como las letras a-j:
    # (1,0,0,0,0,0): '1',   # 1 (a)
    # (1,1,0,0,0,0): '2',   # 2 (b)
    # (1,0,0,1,0,0): '3',   # 3 (c)
    # (1,0,0,1,1,0): '4',   # 4 (d)
    # (1,0,0,0,1,0): '5',   # 5 (e)
    # (1,1,0,1,0,0): '6',   # 6 (f)
    # (1,1,0,1,1,0): '7',   # 7 (g)
    # (1,1,0,0,1,0): '8',   # 8 (h)
    # (0,1,0,1,0,0): '9',   # 9 (i)
    # (0,1,0,1,1,0): '0',   # 0 (j)
    
    # Signos de puntuación
    (0,0,1,0,1,1): '⠂',  # Coma
    (0,0,1,1,0,0): '⠲',  # Punto
    (0,0,1,0,0,1): '⠦',  # Signo de interrogación de apertura
    (0,0,1,0,1,0): '⠦',  # Signo de interrogación de cierre
    (0,0,1,1,0,1): '⠖',  # Signo de exclamación
    (0,0,1,1,1,0): '⠤',  # Guión
    (0,1,1,0,1,1): '⠶',  # Paréntesis de apertura
    (1,1,0,0,1,1): '⠶',  # Paréntesis de cierre
    (0,1,1,0,0,1): '⠠⠦', # Comillas de apertura
    (0,1,1,0,1,0): '⠴',  # Comillas de cierre

    # Caracteres especiales
    (0,0,0,0,0,0): ' ',   # Espacio
    (0,0,0,0,1,0): '⠀',  # Espacio en Braille (celda vacía)
    (1,1,1,1,1,1): '⠿',  # Carácter de relleno

    # Letras adicionales del español
    (1,0,0,0,0,1): '⠷',  # ñ
    (1,1,0,0,0,1): '⠾',  # ü
    (1,0,0,1,0,1): '⠮',  # á
    (1,0,0,1,1,1): '⠡',  # é
    (1,0,0,0,1,1): '⠣',  # í
    (1,1,0,1,0,1): '⠫',  # ó
    (1,1,0,1,1,1): '⠻',  # ú'

}

        # Calcular tamaño de la cuadrícula
        xdistance = None
        ydistance = None
        for label, points in cell_clusters.items():
            for ax, ay in points:
                for bx, by in points:
                    if ax == bx and ay == by:
                        continue

                    if abs(ay - by) <= 2:
                        calcdist = abs(ax - bx)
                        if xdistance is None or calcdist < xdistance:
                            xdistance = calcdist

                    if abs(ax - bx) <= 2:
                        calcdist = abs(ay - by)
                        if ydistance is None or calcdist < ydistance:
                            ydistance = calcdist

        row_width = None if xdistance is None else xdistance
        row_height = None if ydistance is None else ydistance
        
        cells = []
        debug_cells = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
        # Procesar cada cluster (celda Braille)
        for label, points in cell_clusters.items():
            points = np.array(points)
            x_min = np.min(points[:, 0])
            x_max = np.max(points[:, 0])
            y_min = np.min(points[:, 1])
            y_max = np.max(points[:, 1])
            
            # Visualizar el bounding box del cluster
            cell_box = debug_cells.copy()
            cv2.rectangle(cell_box, (x_min, y_min), (x_max, y_max), (0,255,0), 1)
            #cv2.imshow(f"5.4. Cluster {label} bounding box", cell_box)
            #cv2.waitKey(0)
            
            # rows = 1 if y_min == y_max else 
            x_mid = (x_min + x_max) / 2
            o_row_height = (y_max - y_min) / 3
            
            # Dibujar líneas de división para visualizar la cuadrícula
            cell_debug = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
            cv2.line(cell_debug, (x_min, int(y_min + o_row_height)), (x_max, int(y_min + o_row_height)), (255,0,0), 1)
            cv2.line(cell_debug, (x_min, int(y_min + 2*o_row_height)), (x_max, int(y_min + 2*o_row_height)), (255,0,0), 1)
            cv2.line(cell_debug, (int(x_mid), y_min), (int(x_mid), y_max), (255,0,0), 1)
            #cv2.imshow(f"5.5. Grid del Cluster {label}", cell_debug)
            #cv2.waitKey(0)
            
            # Inicializar la cuadrícula 2x3: filas (top, mid, bottom) y columnas (izquierda, derecha)
            # grid = [[0, 0] for _ in range(3)]
            # for (cx, cy) in points:
            #     col = 0 if cx < x_mid else 1
            #     if cy < y_min + row_height:
            #         row = 0
            #     elif cy < y_min + 2 * row_height:
            #         row = 1
            #     else:
            #         row = 2
            #     grid[row][col] = 1
            grid = [[0, 0] for _ in range(3)]
            for (cx, cy) in points:
                x_offset = (cx - x_min)
                y_offset = (cy - y_min)
                col = 0 if row_width is None else int(x_offset / row_width)
                row = 0 if row_height is None else int(y_offset / row_height)
                print((int(cx) - int(x_min), int(cy) - int(y_min)), (col, row), row_width, row_height)
                grid[row][col] = 1
            
            pattern = ( int(grid[0][0]),  # Punto 1
                        int(grid[1][0]),  # Punto 2
                        int(grid[2][0]),  # Punto 3
                        int(grid[0][1]),  # Punto 4
                        int(grid[1][1]),  # Punto 5
                        int(grid[2][1])   # Punto 6
                        )
            char = braille_a_unicode.get(pattern, '?')
            cell_center = (int((x_min+x_max)/2), int((y_min+y_max)/2))
            cells.append((cell_center, char))
            
            # Mostrar por consola el patrón obtenido para cada cluster
            print(f"Cluster {label}: Pattern {pattern} -> Char {char}")
            
            # Para mejor visualización de la cuadrícula, añade esto:
            cell_vis = cell_debug.copy()
            for pt in points:
                pt_x, pt_y = pt
                col = 0 if pt_x < x_mid else 1
                if pt_y < y_min + row_height:
                    row = 0
                elif pt_y < y_min + 2 * row_height:
                    row = 1
                else:
                    row = 2
                cv2.circle(cell_vis, tuple(pt), 3, (0, 0, 255), -1)
                cv2.putText(cell_vis, f"({row},{col})", (pt_x+5, pt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            #cv2.imshow(f"5.6. Puntos en Grid del Cluster {label}", cell_vis)
            #cv2.waitKey(0)
        # Ordenar las celdas en filas según la coordenada Y del centro y luego por X
        cells = sorted(cells, key=lambda c: c[0][1])
        rows = []
        current_row = []
        row_threshold = eps  # Umbral para determinar el mismo renglón
        last_y = None
        for center, char in cells:
            if last_y is None or abs(center[1] - last_y) < row_threshold:
                current_row.append((center, char))
            else:
                current_row = sorted(current_row, key=lambda c: c[0][0])
                rows.append("".join([c for (_, c) in current_row]))
                current_row = [(center, char)]
            last_y = center[1]
        if current_row:
            current_row = sorted(current_row, key=lambda c: c[0][0])
            rows.append("".join([c for (_, c) in current_row]))
        
        texto_braille = "\n".join(rows)
        print("Texto detectado:")
        print(texto_braille)
        return texto_braille
    

    # traducir de braille a texto
    def traducir_braille_a_texto(braille_text):
        """
        Traduce un string en Unicode Braille a texto normal.

        :param braille_text: String en Unicode Braille.
        :return: String traducido a texto normal.
        """
        # Diccionario de mapeo Braille a texto
        braille_a_texto = {
            '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
            '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
            '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
            '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
            '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y',
            '⠵': 'z',
            '⠷': 'ñ', '⠾': 'ü',  # Letras especiales del español
            '⠮': 'á', '⠡': 'é', '⠣': 'í', '⠫': 'ó', '⠻': 'ú',  # Vocales acentuadas
            '⠼⠁': '1', '⠼⠃': '2', '⠼⠉': '3', '⠼⠙': '4',  # Números
            '⠼⠑': '5', '⠼⠋': '6', '⠼⠛': '7', '⠼⠓': '8',
            '⠼⠊': '9', '⠼⠚': '0',
            '⠂': ',', '⠲': '.', '⠦': '?', '⠖': '!', '⠤': '-',  # Signos de puntuación
            '⠶': '()', '⠠⠦': '"', '⠴': '"',
            '⠀': ' ', ' ': ' ',  # Espacios
        }

        # Indicadores especiales
        indicador_mayuscula = '⠠'
        indicador_numero = '⠼'

        texto_traducido = ""
        i = 0
        n = len(braille_text)

        while i < n:
            # Verificar si es un indicador de mayúscula
            if i + 1 < n and braille_text[i] == indicador_mayuscula:
                siguiente_caracter = braille_text[i + 1]
                if siguiente_caracter in braille_a_texto:
                    texto_traducido += braille_a_texto[siguiente_caracter].upper()
                    i += 2  # Saltar el indicador y el carácter
                    continue

            # Verificar si es un indicador numérico
            if i + 1 < n and braille_text[i] == indicador_numero:
                siguiente_caracter = braille_text[i + 1]
                if siguiente_caracter in braille_a_texto:
                    texto_traducido += braille_a_texto[indicador_numero + siguiente_caracter]
                    i += 2  # Saltar el indicador y el carácter
                    continue

            # Caracteres normales
            if braille_text[i] in braille_a_texto:
                texto_traducido += braille_a_texto[braille_text[i]]
            else:
                texto_traducido += '?'  # Carácter desconocido
            i += 1

        return texto_traducido

    texto_traducido = traducir_braille_a_texto(convertir_a_unicode_y_traducir(cropped))
    print(texto_traducido)

if __name__ == '__main__':
    main()

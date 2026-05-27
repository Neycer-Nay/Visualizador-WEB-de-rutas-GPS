# Sistema de Interpolacion de Trayectorias GPS (Web)

Aplicacion web en Flask para interpolar trayectorias GPS con metodos **lineal** y **de Lagrange**, visualizar la ruta en un mapa interactivo y generar graficas comparativas. Este README es una **guia de estudio** completa y tecnica, pensada para comprender el sistema de principio a fin.

---

## 1. Introduccion general

Este proyecto construye una aplicacion web que permite:

- Subir un archivo CSV con puntos GPS.
- Elegir el metodo de interpolacion (lineal o Lagrange).
- Generar puntos intermedios para una trayectoria suave.
- Visualizar resultados en un mapa interactivo.
- Ver graficas comparativas y estadisticas.
- Descargar el CSV interpolado.

### Tecnologias utilizadas

| Componente | Tecnologia | Uso principal |
| --- | --- | --- |
| Backend | Flask | Servidor web y rutas HTTP |
| Datos | Pandas | Lectura y validacion de CSV |
| Matematica | Numpy | Interpolacion y vectores |
| Graficas | Matplotlib | PNG comparativos |
| Mapas | Folium | HTML interactivo con mapas |
| Frontend | Bootstrap 5 | UI moderna y responsive |

### Objetivos del sistema

1. **Aprender interpolacion numerica** aplicada a GPS.
2. **Comprender el flujo web** (request → procesamiento → respuesta).
3. **Visualizar datos geograficos** en mapas y graficas.
4. **Diseñar una interfaz profesional** usando Bootstrap.

---

## 2. Estructura completa del proyecto

```
gps_interpolador_web/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── uploads/
├── outputs/
├── templates/
│   ├── index.html
│   ├── resultado.html
│   └── layout.html
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── mapas/
│   ├── graficas/
│   └── csv/
├── src/
│   ├── lector_csv.py
│   ├── interpolacion.py
│   ├── mapa.py
│   ├── visualizacion.py
│   └── utilidades.py
└── data/
    └── ruta_gps.csv
```

### Responsabilidad de cada carpeta

- `uploads/`: guarda los CSV subidos por el usuario.
- `outputs/`: carpeta de trabajo local (si se desea usar). No se usa para la UI.
- `templates/`: HTML para las vistas Flask.
- `static/`: archivos estaticos (CSS, mapas, graficas, CSV de ejemplo).
- `src/`: logica del dominio (lectura, interpolacion, mapas, utilidades).
- `data/`: dataset de ejemplo para pruebas.

### Responsabilidad de cada archivo

| Archivo | Responsabilidad |
| --- | --- |
| `app.py` | Orquesta el flujo web, rutas y procesamiento |
| `src/lector_csv.py` | Lectura y validacion del CSV |
| `src/interpolacion.py` | Metodos de interpolacion lineal y Lagrange |
| `src/mapa.py` | Creacion del mapa con Folium |
| `src/visualizacion.py` | Graficas con Matplotlib |
| `src/utilidades.py` | Distancias, tiempos y estadisticas |
| `templates/layout.html` | Plantilla base para todas las paginas |
| `templates/index.html` | Formulario principal |
| `templates/resultado.html` | Vista de resultados |
| `static/css/styles.css` | Estilos visuales personalizados |
| `data/ruta_gps.csv` | Datos GPS reales (Santa Cruz, Bolivia) |

---

## 3. Flujo completo del sistema

```
Usuario → Navegador → Flask → Procesamiento → Resultados → Navegador
```

Paso a paso:

1. El usuario entra a `/`.
2. Flask renderiza `templates/index.html`.
3. El usuario sube un CSV y elige metodo.
4. Flask recibe el archivo con `request.files`.
5. `src/lector_csv.py` valida y limpia los datos.
6. `src/interpolacion.py` genera nuevos puntos.
7. `src/mapa.py` crea el mapa interactivo HTML.
8. `src/visualizacion.py` genera la grafica PNG.
9. `templates/resultado.html` muestra mapa, grafica y estadisticas.

---

## 4. Explicacion detallada de `app.py`

### Importaciones

```python
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
```

- `Flask`: instancia de la app.
- `render_template`: renderiza HTML.
- `request`: accede a archivos y formularios.
- `flash`: mensajes de estado.
- `redirect`: redirecciona si hay errores.
- `send_from_directory`: permite descargar archivos.

### Configuracion

```python
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["STATIC_GRAFICAS"] = "static/graficas"
```

Estos valores definen donde guardar archivos subidos y resultados.

### Ruta principal

```python
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
```

Cuando el usuario entra a `/`, Flask devuelve el formulario principal.

### Ruta de procesamiento

```python
@app.route("/procesar", methods=["POST"])
def procesar():
```

Recibe el CSV, valida formato y llama a los modulos.

### Manejo de formularios

```python
archivo = request.files["archivo"]
metodo = request.form.get("metodo")
num_puntos = request.form.get("num_puntos")
```

### Validaciones

- Archivo obligatorio.
- Extension CSV.
- Tamano maximo 2 MB.
- `num_puntos` entre 100 y 5000.

### Proceso de interpolacion

```python
resultado_lineal = interpolar_ruta(..., metodo="lineal")
resultado_lagrange = interpolar_ruta(..., metodo="lagrange")
```

Se ejecutan ambos metodos para el panel comparativo.

### Generacion de salidas

- `src/mapa.py` → HTML con Folium.
- `src/visualizacion.py` → PNG con Matplotlib.
- CSV interpolado → guardado en `static/csv/`.

---

## 5. Explicacion detallada de `interpolacion.py`

### Interpolacion lineal

Matematicamente, entre dos puntos `(x0, y0)` y `(x1, y1)`:

```
y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
```

En el codigo:

```python
np.interp(x_nuevo, x, y)
```

### Interpolacion de Lagrange

Polinomio unico:

```
P(x) = sum_{i=0}^{n-1} y_i * L_i(x)
L_i(x) = prod_{j!=i} (x - x_j) / (x_i - x_j)
```

### Ventajas y desventajas

- **Lineal**: estable, rapido, poco suave.
- **Lagrange**: suaviza, pero puede oscilar con muchos puntos.

---

## 6. Explicacion detallada de `mapa.py`

Folium crea mapas HTML interactivos.

1. Se define el centro.
2. Se agregan puntos originales.
3. Se dibuja la linea interpolada.
4. Se guarda como HTML.

---

## 7. Explicacion detallada de `visualizacion.py`

Matplotlib genera una grafica PNG:

- Puntos originales en azul.
- Trayectoria interpolada en naranja.
- Leyendas y etiquetas.

---

## 8. Explicacion detallada de `lector_csv.py`

1. Lee el archivo con `pandas.read_csv`.
2. Verifica columnas obligatorias.
3. Convierte tipos (tiempo, latitud, longitud).
4. Valida rangos geograficos.
5. Ordena por tiempo.

---

## 9. Explicacion detallada de `utilidades.py`

- **Haversine**: calcula distancia entre dos coordenadas.
- **convertir_tiempo_a_segundos**: normaliza tiempos.
- **calcular_estadisticas**: distancia total, duracion, velocidades.

---

## 10. Explicacion detallada del Frontend

### layout.html

Plantilla base con navbar, estilos y bloques de contenido.

### index.html

- Formulario de subida.
- Selector de metodo.
- Slider para numero de puntos.

### resultado.html

- Graficas.
- Mapa.
- Estadisticas y tabla comparativa.

---

## 11. Explicacion detallada del CSS

- Gradiente de fondo.
- Tarjetas con sombras.
- Cards con bordes suaves.
- Secciones responsive.

---

## 12. Explicacion matematica completa

### Interpolacion lineal

Para dos puntos:

```
y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
```

### Interpolacion de Lagrange

```
P(x) = sum_{i=0}^{n-1} y_i * L_i(x)
L_i(x) = prod_{j!=i} (x - x_j) / (x_i - x_j)
```

---

## 13. Ejemplos reales

CSV de ejemplo:

```
tiempo,latitud,longitud
2026-05-26 08:00:00,-17.78328,-63.18212
```

---

## 14. Explicacion del mapa GPS

- Latitud: eje vertical.
- Longitud: eje horizontal.
- Folium dibuja la trayectoria sobre OpenStreetMap.

---

## 15. Explicacion de Flask

- Framework micro para web.
- Routing mediante decoradores.
- `render_template` para HTML.
- Archivos estaticos en `/static`.

---

## 16. Ciclo completo web

```
Browser → HTTP POST → Flask → Procesamiento → HTML → Browser
```

---

## 17. Como ejecutar el proyecto

1. Crear entorno virtual.
2. `pip install -r requirements.txt`
3. `python app.py`
4. Abrir `http://127.0.0.1:5001`

---

## 18. Posibles errores y soluciones

- `ModuleNotFoundError`: instalar dependencias.
- Puerto bloqueado: usar 5001.
- CSV invalido: revisar columnas.

---

## 19. Mejoras futuras

- GPS en tiempo real.
- Animaciones.
- Base de datos.
- Autenticacion.
- API externa.

---

## 20. Conclusiones

Este proyecto integra matematicas, programacion y visualizacion geografica para construir una aplicacion web completa. Permite aprender interpolacion, Flask y manejo de datos GPS en un entorno real.

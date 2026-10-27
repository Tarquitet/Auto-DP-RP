# 📦 Auto-DP-RP

Herramienta de automatización en Python para convertir imágenes, archivos de audio y assets de Bedrock en **Resource Packs** y **Data Packs** totalmente funcionales para **Minecraft Java Edition**.

Automatiza la generación de JSON, escalado de assets, traducción de modelos y comandos `/give`.

---

## ⚙️ 1. Requisitos e Instalación

1. Asegúrate de tener **Python 3.9 o superior** instalado.
2. Abre una terminal en la **raíz del proyecto** (donde está `config.json`).
3. Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

_(Esto instala `Pillow` para procesamiento de imágenes y `mutagen` para audio)._

---

## ⚙️ 2. Configuración (`config.json`)

El script lee este archivo automáticamente. No requiere argumentos por línea de comandos. Parámetros clave:

- `"NAMESPACE"`: Namespace de tu proyecto (ej. `"btc"`).
- `"INPUT_FOLDER"`: Carpeta de origen (por defecto: `"pendientes"`).
- `"OUTPUT_FOLDER"`: Carpeta de destino (por defecto: `"output"`).
- `"ACTIVE_VERSION"`: Versión de Minecraft objetivo (ej. `"26.3"`, `"1.21"`). Determina los `pack_format` correctos.

---

## 🚀 3. Flujo de Trabajo (Mini Wiki de Uso)

### Paso 1: Organizar los assets

Coloca tus archivos originales dentro de la carpeta `pendientes/`, respetando estas subcarpetas:

| Carpeta           | Contenido esperado                                                                                                               |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `equipment/`      | Texturas y modelos de armaduras/equipamiento.                                                                                    |
| `items/`          | Objetos personalizados.                                                                                                          |
| `waypoints/`      | Imágenes PNG (el script genera automáticamente resoluciones `16x16`, `10x10` y `6x6`).                                           |
| `paintings/`      | Imágenes para cuadros personalizados.                                                                                            |
| `music/`          | Archivos de audio (.ogg) para discos de música.                                                                                  |
| `importar_zips/`  | Archivos `.zip` con assets para procesar en lote.                                                                                |
| `bedrock_addons/` | Archivos `.mcaddon`, `.mcpack` o `.zip` de Bedrock. El script extrae `.geo.json` y texturas para convertirlas a modelos de Java. |

### Paso 2: Ejecutar el generador

Desde la **raíz del proyecto**, ejecuta:

```bash
python generator/main.py
```

### Paso 3: Obtener el resultado

El script vaciará y regenerará automáticamente las carpetas configuradas en `config.json` (por defecto, `output/BTC Assets` y `output/BTC DP`).

Dentro de la carpeta del Data Pack (`output/.../data/.../functions/`), encontrarás archivos `.mcfunction` con los comandos `/give` ya generados para obtener los items en el juego.

---

## ⚠️ 4. Advertencias Críticas

1. **Sobrescritura total**: En cada ejecución, las carpetas de salida (`output/`) se **vacían y regeneran por completo**. Si tienes archivos personalizados que no deben borrarse, haz una copia de seguridad fuera de esta carpeta antes de ejecutar el script.
2. **Ruta de ejecución**: Siempre ejecuta `python generator/main.py` desde la raíz del proyecto. Si lo ejecutas desde dentro de la carpeta `generator/`, el script fallará al no encontrar `config.json`.

---

## 🛠️ 5. Solución de Problemas

| Problema                                        | Solución                                                                                                            |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'Pillow'` | No instalaste las dependencias. Ejecuta `pip install -r requirements.txt`.                                          |
| `FileNotFoundError: config.json`                | Estás ejecutando el comando desde la carpeta equivocada. Sube un nivel a la raíz del proyecto.                      |
| Los modelos de Bedrock no se convierten         | Asegúrate de que el `.mcaddon` o `.zip` contenga archivos `.geo.json` válidos y texturas en la estructura esperada. |
| Necesitas actualizar los `pack_format`          | Ejecuta `python generator/update_formats.py` para sincronizar las versiones de Minecraft en `config.json`.          |

---

## 📂 Estructura del Proyecto

```text
Auto-DP-RP/
├── config.json              # Configuración principal (namespace, versiones, rutas)
├── requirements.txt         # Dependencias de Python
├── generator/
│   ├── main.py              # Punto de entrada principal (ejecutar este)
│   ├── config.py            # Lógica de carga de configuración
│   ├── update_formats.py    # Script para actualizar formatos de Minecraft
│   ├── utils.py             # Funciones auxiliares
│   └── modules/             # Lógica modular (items, waypoints, bedrock converter, etc.)
├── pendientes/              # 📥 Aquí colocas tus assets de entrada
└── output/                  # 📤 Aquí se genera el Resource Pack y Data Pack final
```

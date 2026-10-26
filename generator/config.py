import json
from pathlib import Path

# Cargar el archivo config.json
with open("config.json", "r", encoding="utf-8") as f:
    _config_data = json.load(f)

NAMESPACE = _config_data.get("NAMESPACE", "builtechraft")
INPUT_FOLDER = Path(_config_data.get("INPUT_FOLDER", "pendientes"))
OUTPUT_FOLDER = Path(_config_data.get("OUTPUT_FOLDER", "output"))

# Leer los nombres de las carpetas de salida
RP_FOLDER_NAME = _config_data.get("RP_FOLDER_NAME", "java_resourcepack")
DP_FOLDER_NAME = _config_data.get("DP_FOLDER_NAME", "java_datapack")

MINECRAFT_VERSIONS = _config_data.get("MINECRAFT_VERSIONS", {})
ACTIVE_VERSION = _config_data.get("ACTIVE_VERSION", "1.21.4")

# Construir las rutas usando las variables
JAVA_RP_PATH = OUTPUT_FOLDER / RP_FOLDER_NAME
JAVA_DP_PATH = OUTPUT_FOLDER / DP_FOLDER_NAME
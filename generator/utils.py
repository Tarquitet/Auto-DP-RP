import json
import shutil
from pathlib import Path

def clean_and_create(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

def inicializar_carpetas(config_data: dict, input_base: Path, output_base: Path):
    """Crea automáticamente las carpetas de entrada y salida basadas en la configuración."""
    subcarpetas = config_data.get("INPUT_SUBFOLDERS", ["equipment"])
    for sub in subcarpetas:
        (input_base / sub).mkdir(parents=True, exist_ok=True)
    output_base.mkdir(parents=True, exist_ok=True)
    print("-> Estructura de directorios inicializada correctamente.")

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.write("\n")

def copy_if_exists(source: Path, destination: Path):
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True
import json
import zipfile
import shutil
from pathlib import Path

def procesar_zips_automaticamente(input_folder_path: Path):
    """
    Escanea la carpeta 'importar_zips' dentro de 'pendientes'.
    Extrae CUALQUIER imagen PNG y la clasifica inteligentemente.
    """
    zips_dir = input_folder_path / "importar_zips"
    salida_equip = input_folder_path / "equipment"
    salida_items = input_folder_path / "items"
    
    if not zips_dir.exists():
        print(f"Omitiendo migración: No existe la carpeta {zips_dir.name}")
        return

    salida_equip.mkdir(parents=True, exist_ok=True)
    salida_items.mkdir(parents=True, exist_ok=True)
    
    print(f"Escaneando zips automáticos en {zips_dir}/...")

    for zip_file in zips_dir.glob("*.zip"):
        print(f" -> Analizando y extrayendo de: {zip_file.name}")
        contador_3d = 0
        contador_2d = 0
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                for archivo in z.infolist():
                    if archivo.is_dir() or not archivo.filename.endswith('.png'):
                        continue
                        
                    ruta_interna = archivo.filename.lower()
                    nombre_base = Path(archivo.filename).stem
                    
                    # Ignorar imágenes de interfaz o cosas irrelevantes
                    if "gui" in ruta_interna or "environment" in ruta_interna:
                        continue

                    # ESTRATEGIA: Si la ruta contiene "entity" o "armor", es textura 3D para la cabeza
                    if "entity" in ruta_interna or "armor" in ruta_interna or "model" in ruta_interna:
                        nuevo_nombre = f"{nombre_base}_head.png"
                        with z.open(archivo) as origen, open(salida_equip / nuevo_nombre, "wb") as destino:
                            shutil.copyfileobj(origen, destino)
                        contador_3d += 1
                        
                    # ESTRATEGIA: Si contiene "item", es el ícono 2D
                    elif "item" in ruta_interna:
                        # Si ya tiene sufijo "_icon", lo respetamos, si no, se lo agregamos
                        if not nombre_base.endswith("_icon"):
                            nuevo_nombre = f"{nombre_base}_head_icon.png"
                        else:
                            nuevo_nombre = f"{nombre_base.replace('_icon', '')}_head_icon.png"
                            
                        with z.open(archivo) as origen, open(salida_equip / nuevo_nombre, "wb") as destino:
                            shutil.copyfileobj(origen, destino)
                        contador_2d += 1
                        
        except zipfile.BadZipFile:
            print(f"    [Error] El archivo {zip_file.name} está corrupto.")
            
        print(f"    Extraídos: {contador_3d} texturas 3D, {contador_2d} íconos 2D.")
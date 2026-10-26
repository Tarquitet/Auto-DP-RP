import json
import urllib.request
from pathlib import Path

def actualizar_formatos_silencioso(config_path="config.json"):
    url = "https://raw.githubusercontent.com/misode/mcmeta/summary/versions/data.json"
    
    print("Conectando a internet para verificar nuevos formatos de Minecraft...")
    try:
        # Petición a la API
        req = urllib.request.Request(url, headers={'User-Agent': 'Auto-DP-RP-Updater/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            nuevos_formatos = {}
            for version in data:
                nombre_version = version.get("id")
                dp_format = version.get("data_pack_version")
                rp_format = version.get("resource_pack_version")
                
                # Guardar solo si tiene formatos válidos
                if nombre_version and dp_format and rp_format:
                    nuevos_formatos[nombre_version] = {
                        "resource_pack_format": rp_format,
                        "data_pack_format": dp_format
                    }
                    
    except Exception as e:
        print(f" [Error de conexión] Se usará la configuración local. ({e})")
        return

    # Leer tu config.json actual
    ruta_config = Path(config_path)
    if ruta_config.exists():
        with open(ruta_config, "r", encoding="utf-8") as f:
            config_actual = json.load(f)
    else:
        print(f" [Error] No se encontró {config_path}")
        return
    
    # 1. ACTUALIZAR SOLO LA LISTA DE VERSIONES (No toca tu ACTIVE_VERSION)
    config_actual["MINECRAFT_VERSIONS"] = nuevos_formatos
    
    # 2. GUARDAR EL JSON
    with open(ruta_config, "w", encoding="utf-8") as f:
        json.dump(config_actual, f, indent=4, ensure_ascii=False)
        
    print("-> Formatos de versiones actualizados en config.json")

if __name__ == "__main__":
    actualizar_formatos_silencioso()
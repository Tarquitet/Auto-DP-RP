import json
import shutil
from pathlib import Path
from PIL import Image

try:
    from generator.utils import write_json
except ModuleNotFoundError:
    from utils import write_json

def process(input_path: Path, rp_path: Path, dp_path: Path, namespace: str):
    print("Processing custom paintings...")
    folder = input_path / "paintings"
    if not folder.exists():
        return
        
    pinturas_survival = []
    commands = [f"# Comandos generados para pinturas en {namespace}", ""]
    
    # Soporta varios formatos de imagen
    for image_path in sorted(folder.glob("*.*")):
        if image_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.webp']:
            continue
            
        parts = image_path.stem.split("_")
        # Regla: nombre_anchoXalto_Autor_survival
        if len(parts) != 4:
            print(f"  [Advertencia] Saltando {image_path.name} (usa: nombre_anchoxalto_Autor_survival.ext)")
            continue
            
        name, size, author, survival = parts
        
        try:
            # Dimensiones en bloques (ej: 2x3)
            width, height = map(int, size.lower().split("x"))
        except ValueError:
            print(f"  [Error] Tamaño inválido en {image_path.name}. Usa el formato 2x3.")
            continue
            
        is_survival = survival.lower() == "si"
        
        # 1. Rutas de Texturas
        tex_painting_dir = rp_path / "assets" / namespace / "textures" / "painting"
        tex_item_dir = rp_path / "assets" / namespace / "textures" / "item"
        tex_painting_dir.mkdir(parents=True, exist_ok=True)
        tex_item_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Procesar Imágenes (Completa y Miniatura)
        with Image.open(image_path) as img:
            img_rgba = img.convert("RGBA")
            # Guardar lienzo completo para la entidad
            img_rgba.save(tex_painting_dir / f"{name}.png", "PNG")
            # Guardar versión 16x16 para el ítem en inventario
            img_rgba.resize((16, 16), Image.Resampling.NEAREST).save(tex_item_dir / f"{name}.png", "PNG")
            
        # 3. Generar Modelo del Ítem
        write_json(
            rp_path / "assets" / namespace / "models" / "item" / f"{name}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"{namespace}:item/{name}"}}
        )
        
        # 4. Generar Data Pack (Painting Variant)
        write_json(
            dp_path / "data" / namespace / "painting_variant" / f"{name}.json",
            {
                "asset_id": f"{namespace}:{name}",
                "width": width,
                "height": height
            }
        )
        
        # 5. Agregar a Survival si corresponde
        if is_survival:
            pinturas_survival.append(f"{namespace}:{name}")
            
        # 6. Generar comando de obtención
        nombre_limpio = name.replace('-', ' ').title()
        commands.extend([
            f"# Cuadro: {nombre_limpio} por {author}",
            f"give @p painting[minecraft:painting_variant=\"{namespace}:{name}\",minecraft:item_model=\"{namespace}:item/{name}\",minecraft:custom_name='{{\"text\":\"{nombre_limpio} - {author}\", \"italic\":false}}'] 1",
            ""
        ])
        print(f"  Pintura: {name} ({width}x{height}) - Survival: {is_survival}")
        
    # Registrar en el Tag 'placeable' (para que el juego las use al poner cuadros)
    if pinturas_survival:
        write_json(
            dp_path / "data" / "minecraft" / "tags" / "painting_variant" / "placeable.json",
            {"values": pinturas_survival}
        )
        
    # Escribir el mcfunction
    if len(commands) > 2:
        command_file = dp_path / "data" / namespace / "function" / "get_paintings.mcfunction"
        command_file.parent.mkdir(parents=True, exist_ok=True)
        command_file.write_text("\n".join(commands), encoding="utf-8")
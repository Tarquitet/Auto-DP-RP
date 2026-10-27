from pathlib import Path
from PIL import Image

try:
    from generator.utils import write_json
except ModuleNotFoundError:
    from utils import write_json

def process(input_path: Path, rp_path: Path, dp_path: Path, namespace: str):
    print("\n🖼️ Procesando pinturas...")
    folder = input_path / "paintings"
    
    if not folder.exists():
        print("  ⚠️ Carpeta 'paintings' no existe. Saltando.")
        return
    
    pinturas_survival = []
    archivos_procesados = 0
    
    for image_path in sorted(folder.glob("*.*")):
        if image_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.webp']:
            continue
        
        parts = image_path.stem.split("_")
        
        # ACEPTA 3 O 4 PARTES
        if len(parts) == 3:
            name, size, author = parts
            is_survival = True
        elif len(parts) == 4:
            name, size, author, survival = parts
            is_survival = survival.lower() == "si"
        else:
            print(f"  ⚠️ Saltando {image_path.name} (usa: nombre_2x3_Autor o nombre_2x3_Autor_si)")
            continue
        
        try:
            width, height = map(int, size.lower().split("x"))
        except ValueError:
            print(f"  ❌ Tamaño inválido en {image_path.name}. Usa 2x3.")
            continue
        
        # Crear carpetas
        tex_painting_dir = rp_path / "assets" / namespace / "textures" / "painting"
        tex_item_dir = rp_path / "assets" / namespace / "textures" / "item"
        tex_painting_dir.mkdir(parents=True, exist_ok=True)
        tex_item_dir.mkdir(parents=True, exist_ok=True)
        
        # Procesar imagen
        with Image.open(image_path) as img:
            img_rgba = img.convert("RGBA")
            img_rgba.save(tex_painting_dir / f"{name}.png", "PNG")
            img_rgba.resize((16, 16), Image.Resampling.NEAREST).save(tex_item_dir / f"{name}.png", "PNG")
        
        # Modelo del ítem (Resource Pack)
        write_json(
            rp_path / "assets" / namespace / "models" / "item" / f"{name}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"{namespace}:item/{name}"}}
        )
        
        # Definición de ítem moderno 1.21.4+ (Resource Pack)
        write_json(
            rp_path / "assets" / namespace / "items" / f"{name}.json",
            {
                "model": {
                    "type": "minecraft:model",
                    "model": f"{namespace}:item/{name}"
                }
            }
        )
        
        # Título formateado
        titulo_limpio = name.replace('-', ' ').replace('_', ' ').title()
        
        # Painting Variant (Data Pack) - FORMATO CORRECTO 1.21+
        write_json(
            dp_path / "data" / namespace / "painting_variant" / f"{name}.json",
            {
                "asset_id": f"{namespace}:{name}",
                "width": width,
                "height": height,
                "title": {
                    "color": "yellow",
                    "text": titulo_limpio
                },
                "author": {
                    "color": "gray",
                    "text": author
                }
            }
        )
        
        if is_survival:
            pinturas_survival.append(f"{namespace}:{name}")
        
        archivos_procesados += 1
        print(f"  ✅ {titulo_limpio} ({width}x{height}) por {author} - Survival: {'SI' if is_survival else 'NO'}")
    
    # Tag placeable
    if pinturas_survival:
        write_json(
            dp_path / "data" / "minecraft" / "tags" / "painting_variant" / "placeable.json",
            {"values": pinturas_survival}
        )
    
    print(f"   Total pinturas procesadas: {archivos_procesados}\n")
from pathlib import Path

try:
    from generator.utils import copy_if_exists, write_json
except ModuleNotFoundError:
    from utils import copy_if_exists, write_json

SLOT_TO_LAYER = {
    "head": "humanoid",
    "chest": "humanoid",
    "feet": "humanoid",
    "legs": "humanoid_leggings",
    "body": "wings",
    "elytra": "wings",
}


def process(input_path: Path, rp_path: Path, namespace: str):
    print("Processing equipment...")
    folder = input_path / "equipment"
    if not folder.exists():
        return

    for image in sorted(folder.glob("*.png")):
        # Ignorar los archivos de ícono en el bucle principal para que no salgan advertencias
        if image.name.endswith("_icon.png"):
            continue

        parts = image.stem.rsplit("_", 1)
        if len(parts) != 2 or parts[1].lower() not in SLOT_TO_LAYER:
            print(f"  warning: skipping {image.name} (use name_slot.png)")
            continue

        name, slot = parts[0], parts[1].lower()
        layer = SLOT_TO_LAYER[slot]
        
        write_json(
            rp_path / "assets" / namespace / "equipment" / f"{name}.json",
            {"layers": {layer: {"texture": f"{namespace}:{name}"}}},
        )
        
        # 1. Copiar la textura 3D para el modelo de la entidad
        copy_if_exists(
            image,
            rp_path / "assets" / namespace / "textures" / "entity" / "equipment" / layer / f"{name}.png",
        )
        
        write_json(
            rp_path / "assets" / namespace / "items" / f"{name}.json",
            {"model": {"type": "minecraft:model", "model": f"{namespace}:item/{name}"}},
        )
        write_json(
            rp_path / "assets" / namespace / "models" / "item" / f"{name}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"{namespace}:item/{name}"}},
        )
        
        # 2. Copiar el ícono para el inventario (busca si existe el archivo _icon)
        icon_image = image.with_name(f"{image.stem}_icon.png")
        if icon_image.exists():
            copy_if_exists(icon_image, rp_path / "assets" / namespace / "textures" / "item" / f"{name}.png")
        else:
            # Si no hay ícono dedicado, usa la imagen normal como respaldo
            copy_if_exists(image, rp_path / "assets" / namespace / "textures" / "item" / f"{name}.png")
            
        print(f"  equipment {name} (slot: {slot} -> {layer})")
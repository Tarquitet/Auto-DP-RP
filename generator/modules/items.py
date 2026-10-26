from pathlib import Path

try:
    from generator.utils import copy_if_exists, write_json
except ModuleNotFoundError:
    from utils import copy_if_exists, write_json


def process(input_path: Path, rp_path: Path, dp_path: Path, namespace: str):
    print("Processing custom items...")
    folder = input_path / "items"
    if not folder.exists():
        return

    commands = [f"# Generated commands for items in {namespace}", ""]
    for image in sorted(folder.glob("*.png")):
        parts = image.stem.rsplit("_", 1)
        if len(parts) != 2:
            print(f"  warning: skipping {image.name} (use name_baseItem.png)")
            continue

        name, base_item = parts
        write_json(
            rp_path / "assets" / namespace / "items" / f"{name}.json",
            {"model": {"type": "minecraft:model", "model": f"{namespace}:item/{name}"}},
        )
        parent = "minecraft:item/generated" if base_item == "generated" else f"minecraft:item/{base_item}"
        write_json(
            rp_path / "assets" / namespace / "models" / "item" / f"{name}.json",
            {"parent": parent, "textures": {"layer0": f"{namespace}:item/{name}"}},
        )
        copy_if_exists(image, rp_path / "assets" / namespace / "textures" / "item" / f"{name}.png")
        commands.extend(
            [
                f"# {name.replace('_', ' ').title()}",
                f"give @p {base_item}[custom_name='{{\"text\":\"{namespace}:{name}\"}}'] 1",
                "",
            ]
        )
        print(f"  item {name} (base: {base_item})")

    if len(commands) > 2:
        command_file = dp_path / "data" / namespace / "function" / "get_items.mcfunction"
        command_file.parent.mkdir(parents=True, exist_ok=True)
        command_file.write_text("\n".join(commands), encoding="utf-8")

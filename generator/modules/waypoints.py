import re
from pathlib import Path

from PIL import Image

try:
    from generator.utils import copy_if_exists, write_json
except ModuleNotFoundError:
    from utils import copy_if_exists, write_json


def resize_image(source: Path, destination: Path, size: tuple[int, int]):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.convert("RGBA").resize(size, Image.Resampling.LANCZOS).save(destination, "PNG")


def process(input_path: Path, rp_path: Path, namespace: str):
    print("Processing locator bar waypoints...")
    folder = input_path / "waypoints"
    if not folder.exists():
        return

    for image in sorted(folder.glob("*.png")):
        match = re.fullmatch(r"(.+)_([0-9]+)_([0-9]+)_([0-9]+)", image.stem)
        name, large, medium, far = match.groups() if match else (image.stem, "4", "16", "32")
        textures_dir = rp_path / "assets" / namespace / "textures" / "gui" / "sprites" / "hud" / "locator_bar"
        variants = ((name, (16, 16)), (f"{name}_small", (10, 10)), (f"{name}_tiny", (6, 6)))
        for variant_name, size in variants:
            resize_image(image, textures_dir / f"{variant_name}.png", size)
        write_json(
            rp_path / "assets" / namespace / "waypoint_style" / f"{name}.json",
            {
                "near_distance": int(large),
                "far_distance": int(far),
                "sprites": [f"{namespace}:{name}", f"{namespace}:{name}_small", f"{namespace}:{name}_tiny"],
            },
        )
        print(f"  waypoint {name} ({large}-{medium}-{far})")

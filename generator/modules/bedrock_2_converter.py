import json
from pathlib import Path
from PIL import Image

try:
    from generator.utils import write_json
except ModuleNotFoundError:
    from utils import write_json


def _ajustar_angulo_java(angulo: float) -> tuple[float, bool]:
    """Java (pre-cambios libres o estándar seguro) soporta -45, -22.5, 0, 22.5, 45 en un solo eje."""
    permitidos = [-45.0, -22.5, 0.0, 22.5, 45.0]
    cercano = min(permitidos, key=lambda x: abs(x - angulo))
    return cercano, cercano != 0.0


def _calcular_uv_box(uv_origin: list[float], size: list[float], tex_w: float, tex_h: float) -> dict:
    """Convierte el Box UV estándar de Bedrock a caras UV [0-16] de Java."""
    u, v = uv_origin
    dx, dy, dz = size

    def norm(x1, y1, x2, y2):
        return [
            round((x1 / tex_w) * 16, 4),
            round((y1 / tex_h) * 16, 4),
            round((x2 / tex_w) * 16, 4),
            round((y2 / tex_h) * 16, 4),
        ]

    return {
        "up":    {"uv": norm(u + dz + dx, v + dz, u + dz, v), "texture": "#0"},
        "down":  {"uv": norm(u + dz + dx * 2, v, u + dz + dx, v + dz), "texture": "#0"},
        "west":  {"uv": norm(u, v + dz, u + dz, v + dz + dy), "texture": "#0"},
        "north": {"uv": norm(u + dz, v + dz, u + dz + dx, v + dz + dy), "texture": "#0"},
        "east":  {"uv": norm(u + dz + dx, v + dz, u + dz * 2 + dx, v + dz + dy), "texture": "#0"},
        "south": {"uv": norm(u + dz * 2 + dx, v + dz, u + dz * 2 + dx * 2, v + dz + dy), "texture": "#0"},
    }


def _calcular_uv_per_face(uv_dict: dict, tex_w: float, tex_h: float) -> dict:
    """Convierte Per-Face UV de Bedrock a caras UV [0-16] de Java."""
    faces = {}
    for cara in ("north", "south", "east", "west", "up", "down"):
        if cara not in uv_dict:
            continue
        c_data = uv_dict[cara]
        uv = c_data.get("uv", [0, 0])
        uv_size = c_data.get("uv_size", [16, 16])
        faces[cara] = {
            "uv": [
                round((uv[0] / tex_w) * 16, 4),
                round((uv[1] / tex_h) * 16, 4),
                round(((uv[0] + uv_size[0]) / tex_w) * 16, 4),
                round(((uv[1] + uv_size[1]) / tex_h) * 16, 4),
            ],
            "texture": "#0",
        }
    return faces


def process(input_path: Path, rp_path: Path, dp_path: Path, namespace: str):
    staging_dir = input_path / "bedrock_staging"
    if not staging_dir.exists():
        return

    geo_files = sorted(staging_dir.glob("*.geo.json"))
    if not geo_files:
        return

    print("Converting staged Bedrock models to Java...")
    commands = [f"# Comandos generados para modelos Bedrock en {namespace}", ""]

    for geo_file in geo_files:
        name = geo_file.name.replace(".geo.json", "")
        png_file = staging_dir / f"{name}.png"

        if not png_file.exists():
            print(f"  [Advertencia] Falta textura {name}.png en staging. Omitido.")
            continue

        try:
            geo_json = json.loads(geo_file.read_text(encoding="utf-8"))
            geo_list = geo_json.get("minecraft:geometry", [])
            if not geo_list:
                continue

            geo = geo_list[0]
            desc = geo.get("description", {})
            tex_w = float(desc.get("texture_width", 16))
            tex_h = float(desc.get("texture_height", 16))

            elements = []
            for bone in geo.get("bones", []):
                bone_rot = bone.get("rotation", [0, 0, 0])
                bone_piv = bone.get("pivot", [0, 0, 0])

                for cube in bone.get("cubes", []):
                    origin = cube.get("origin", [0, 0, 0])
                    size = cube.get("size", [1, 1, 1])
                    inflate = cube.get("inflate", 0.0)

                    # Conversión espacial: En Bedrock X está invertido respecto a Java y el centro X/Z es 0 (en Java es +8)
                    fx = round(-(origin[0] + size[0]) + 8 - inflate, 4)
                    fy = round(origin[1] - inflate, 4)
                    fz = round(origin[2] + 8 - inflate, 4)

                    tx = round(-origin[0] + 8 + inflate, 4)
                    ty = round(origin[1] + size[1] + inflate, 4)
                    tz = round(origin[2] + size[2] + 8 + inflate, 4)

                    uv_raw = cube.get("uv", [0, 0])
                    if isinstance(uv_raw, dict):
                        faces = _calcular_uv_per_face(uv_raw, tex_w, tex_h)
                    else:
                        faces = _calcular_uv_box(uv_raw, size, tex_w, tex_h)

                    elem = {
                        "from": [fx, fy, fz],
                        "to": [tx, ty, tz],
                        "faces": faces,
                    }

                    # Rotación (prioriza rotación del cubo, si no usa la del bone)
                    rot = cube.get("rotation", bone_rot)
                    piv = cube.get("pivot", bone_piv)
                    if any(r != 0 for r in rot):
                        # Tomar el eje dominante para cumplir con el estándar de modelos de ítems en Java
                        ejes = [("x", -rot[0]), ("y", -rot[1]), ("z", rot[2])]
                        eje_dom, val_dom = max(ejes, key=lambda item: abs(item[1]))
                        ang_java, usar = _ajustar_angulo_java(val_dom)
                        if usar:
                            elem["rotation"] = {
                                "angle": ang_java,
                                "axis": eje_dom,
                                "origin": [round(-piv[0] + 8, 4), round(piv[1], 4), round(piv[2] + 8, 4)],
                            }

                    elements.append(elem)

            if not elements:
                continue

            # 1. Guardar textura PNG normalizada en Resource Pack
            tex_dest = rp_path / "assets" / namespace / "textures" / "item" / f"{name}.png"
            tex_dest.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(png_file) as img:
                img.convert("RGBA").save(tex_dest, "PNG")

            # 2. Guardar modelo 3D Java con display estándar para mano, inventario y cabeza
            modelo_java = {
                "texture_size": [int(tex_w), int(tex_h)],
                "textures": {
                    "0": f"{namespace}:item/{name}",
                    "particle": f"{namespace}:item/{name}",
                },
                "elements": elements,
                "display": {
                    "thirdperson_righthand": {"scale": [0.75, 0.75, 0.75]},
                    "thirdperson_lefthand": {"scale": [0.75, 0.75, 0.75]},
                    "firstperson_righthand": {"scale": [0.75, 0.75, 0.75]},
                    "firstperson_lefthand": {"scale": [0.75, 0.75, 0.75]},
                    "gui": {"rotation": [30, 225, 0], "scale": [0.625, 0.625, 0.625]},
                    "head": {"translation": [0, 6.4, 0], "scale": [1.6, 1.6, 1.6]},
                    "ground": {"scale": [0.5, 0.5, 0.5]},
                },
            }
            write_json(rp_path / "assets" / namespace / "models" / "item" / f"{name}.json", modelo_java)

            # 3. Definición de ítem moderno (1.21.4+)
            write_json(
                rp_path / "assets" / namespace / "items" / f"{name}.json",
                {"model": {"type": "minecraft:model", "model": f"{namespace}:item/{name}"}},
            )

            # 4. Comando /give en Data Pack (equipable en cabeza por defecto usando carved_pumpkin o stick)
            nombre_limpio = name.replace("_", " ").title()
            commands.extend([
                f"# Modelo Bedrock 3D: {nombre_limpio}",
                f"give @p stick[minecraft:item_model=\"{namespace}:{name}\",minecraft:equippable={{slot:\"head\"}},minecraft:item_name='{{\"text\":\"{nombre_limpio}\",\"italic\":false}}'] 1",
                "",
            ])
            print(f"  Convertido a Java: {name} ({len(elements)} cubos)")

        except Exception as e:
            print(f"  [Error] Convirtiendo {geo_file.name}: {e}")

    if len(commands) > 2:
        cmd_file = dp_path / "data" / namespace / "function" / "get_bedrock_items.mcfunction"
        cmd_file.parent.mkdir(parents=True, exist_ok=True)
        cmd_file.write_text("\n".join(commands), encoding="utf-8")
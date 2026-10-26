import io
import json
import shutil
import zipfile
from pathlib import Path


def _extraer_de_zip(zf: zipfile.ZipFile, staging_dir: Path) -> tuple[int, int]:
    archivos = zf.namelist()
    geos = {}
    pngs = {}

    for nombre in archivos:
        if nombre.endswith("/"):
            continue
        p = Path(nombre)
        low = nombre.lower()

        # Si un .mcaddon trae un .mcpack o .zip adentro (Resource Pack anidado)
        if low.endswith((".mcpack", ".zip")):
            with zf.open(nombre) as nested_bytes:
                with zipfile.ZipFile(io.BytesIO(nested_bytes.read())) as nested_zf:
                    g, t = _extraer_de_zip(nested_zf, staging_dir)
                    geos_nested, pngs_nested = g, t
            continue

        # Ignorar bloques y mobs complejos por ruta común en Bedrock
        if any(ign in low for ign in ("/blocks/", "/Attachables_ign/", "/gui/", "/environment/", "pack_icon.png")):
            continue

        if low.endswith(".geo.json") or (low.endswith(".json") and "/models/" in low):
            stem = p.name.replace(".geo.json", "").replace(".json", "")
            geos[stem.lower()] = nombre
        elif low.endswith(".png") and "/textures/" in low:
            pngs[p.stem.lower()] = nombre

    extraidos_geo = 0
    extraidos_png = 0

    for stem, geo_internal in geos.items():
        # Verificar que sea realmente una geometría válida de Bedrock y no un mob complejo con animaciones masivas
        try:
            raw_geo = json.loads(zf.read(geo_internal).decode("utf-8"))
        except Exception:
            continue

        if "minecraft:geometry" not in raw_geo:
            continue

        # Buscar textura con nombre exacto o coincidencia parcial
        png_internal = pngs.get(stem)
        if not png_internal:
            coincidencias = [ruta for k, ruta in pngs.items() if stem in k or k in stem]
            if coincidencias:
                png_internal = coincidencias[0]

        if not png_internal:
            continue

        # Guardar par limpio en bedrock_staging
        geo_dest = staging_dir / f"{stem}.geo.json"
        png_dest = staging_dir / f"{stem}.png"

        with zf.open(geo_internal) as src, open(geo_dest, "wb") as dst:
            shutil.copyfileobj(src, dst)
        extraidos_geo += 1

        with zf.open(png_internal) as src, open(png_dest, "wb") as dst:
            shutil.copyfileobj(src, dst)
        extraidos_png += 1

    return extraidos_geo, extraidos_png


def process(input_path: Path, rp_path: Path, namespace: str):
    addons_dir = input_path / "bedrock_addons"
    staging_dir = input_path / "bedrock_staging"

    if not addons_dir.exists():
        return

    paquetes = (
        list(addons_dir.glob("*.mcaddon"))
        + list(addons_dir.glob("*.mcpack"))
        + list(addons_dir.glob("*.zip"))
    )
    if not paquetes:
        return

    print("Processing Bedrock addons extraction...")
    staging_dir.mkdir(parents=True, exist_ok=True)

    for pack in sorted(paquetes):
        try:
            with zipfile.ZipFile(pack, "r") as zf:
                g_count, p_count = _extraer_de_zip(zf, staging_dir)
                print(f"  Addon {pack.name} -> {g_count} modelos y {p_count} texturas movidos a staging.")
        except zipfile.BadZipFile:
            print(f"  [Error] Archivo corrupto o inválido: {pack.name}")
# Usage guide

[Español](USAGE.es.md) | **English**

This guide explains how to prepare inputs, run Auto-DP-RP, and locate its generated Java Edition packs.

## 1. Install and run

From the project root, install the requirements and run the generator:

```powershell
python -m pip install -r requirements.txt
python generator/main.py
```

The generator reads `config.json` relative to the current working directory. Run it from the project root. To use alternate input and output roots:

```powershell
python generator/main.py --input another-input --output another-output
```

The namespace, Minecraft version, and pack folder names still come from `config.json`. The configured input subfolders are created automatically under the selected input directory.

> **Important:** each run recursively clears the configured resource-pack and data-pack output folders before generating them again. Do not store source files or hand-edited files in those output folders.

## 2. Input folders

The current `config.json` creates this layout in `pendientes/`:

```text
pendientes/
├── equipment/
├── items/
├── waypoints/
├── paintings/
├── music/
├── importar_zips/
├── bedrock_addons/
└── bedrock_staging/
```

Put source files in the corresponding folder. The generator processes files directly inside each folder, not arbitrary nested subfolders.

## 3. Prepare each asset type

### Custom items

Put PNG files in `pendientes/items/` and name them `name_baseItem.png`, for example:

```text
emerald_badge_diamond.png
```

The generator splits the name at the **last underscore**: `emerald_badge` becomes the generated item name and `diamond` becomes the base item ID used by its `/give` command. Therefore, the base item portion must be a single segment without underscores; the portion before it can contain underscores.

The generator creates a custom item definition, model, texture, and `get_items.mcfunction` command file when at least one valid item is found.

### Equipment

Put PNG textures in `pendientes/equipment/` and use `name_slot.png`. Supported slots are:

| Slot | Equipment layer |
| --- | --- |
| `head` | `humanoid` |
| `chest` | `humanoid` |
| `legs` | `humanoid_leggings` |
| `feet` | `humanoid` |
| `body` | `wings` |
| `elytra` | `wings` |

An optional inventory icon can be provided as `name_slot_icon.png`. If it is absent, the full texture is also used as the item icon. For example, `silver_wolf_head.png` can use `silver_wolf_head_icon.png`.

### Locator-bar waypoints

Place PNG files in `pendientes/waypoints/`. The accepted naming pattern is:

```text
name_near_medium_far.png
```

For example, `town_4_16_32.png`. A file without the three numeric suffixes is still processed with default values `4`, `16`, and `32`. Each image is converted to 16×16, 10×10, and 6×6 sprites. The style JSON uses the first value as `near_distance` and the third as `far_distance`; the middle value is currently not written to the generated JSON.

### Paintings

Place PNG, JPG, JPEG, or WebP images in `pendientes/paintings/` and name each file:

```text
name_widthxheight_author_survival.ext
```

Example: `sunset_2x3_Alex_si.png`. Use one underscore-free value for each name, size, and author field. Set the last field to `si` to include the painting in the generated `minecraft:painting_variant/placeable` tag; any other value excludes it. The image is also reduced to a 16×16 item icon.

### Music discs

For each song, place an OGG file and a matching image in `pendientes/music/`:

```text
evening.ogg
evening_Alex_12.png
```

The image name must start with the exact OGG filename stem, followed by `_author_comparator`. Use one underscore-free author value. The image can be PNG, JPG, JPEG, or WebP. The comparator field should be numeric; an invalid value falls back to `15`. The generator reads the OGG duration with Mutagen and creates the sound, icon, jukebox song definition, and `get_discs.mcfunction` command file.

### Import images from ZIP resource packs

Place `.zip` files directly in `pendientes/importar_zips/`. The importer scans PNGs in the archives and uses their internal paths to classify likely entity/armor/model textures as equipment textures and item textures as inventory icons. It skips paths containing `gui` or `environment`. This is a heuristic importer; review the extracted images in `pendientes/equipment/` and correct names or mismatches before relying on the generated pack.

### Convert supported Bedrock models

Place `.mcaddon`, `.mcpack`, or `.zip` files in `pendientes/bedrock_addons/`. The extractor looks for Bedrock geometry JSON and matching textures, including packs nested inside an archive, and stages compatible pairs in `pendientes/bedrock_staging/`. The converter then writes Java item models and a `get_bedrock_items.mcfunction` file.

You can also place a matching pair directly in staging:

```text
pendientes/bedrock_staging/example.geo.json
pendientes/bedrock_staging/example.png
```

Conversion is best-effort: unsupported geometry or missing texture pairs may be skipped. Inspect the generated model and test it in Minecraft before publishing it.

## 4. Find the generated files

The current settings in `config.json` write the packs to:

```text
output/
├── BTC Assets/    Resource pack
└── BTC DP/        Data pack
```

These names are configurable through `RP_FOLDER_NAME` and `DP_FOLDER_NAME`. Each pack receives a `pack.mcmeta` generated from `ACTIVE_VERSION` and its entry in `MINECRAFT_VERSIONS`.

Generated command files are written under `data/<namespace>/function/` in the data pack:

- `get_items.mcfunction`
- `get_paintings.mcfunction`
- `get_discs.mcfunction`
- `get_bedrock_items.mcfunction`

Only files for asset types that produced valid entries are created. Equipment and waypoints do not generate command files.

## 5. Configuration and format updates

Edit `config.json` to set:

- `NAMESPACE`: namespace used in generated IDs and paths.
- `INPUT_FOLDER`, `OUTPUT_FOLDER`: input and output root folders.
- `RP_FOLDER_NAME`, `DP_FOLDER_NAME`: resource-pack and data-pack folder names.
- `ACTIVE_VERSION`: target version; it must be a key in `MINECRAFT_VERSIONS`.
- `INPUT_SUBFOLDERS`: folders initialized under the input root.

To refresh the format mapping from the upstream data source, run:

```powershell
python generator/update_formats.py
```

This optional step requires internet access and replaces the `MINECRAFT_VERSIONS` mapping in `config.json`. It preserves `ACTIVE_VERSION`; verify that the active version remains available before generating.

## Troubleshooting

- **Unknown Minecraft version:** set `ACTIVE_VERSION` to a key present in `MINECRAFT_VERSIONS`.
- **Missing input folder:** run from the project root or check `INPUT_FOLDER` / `--input`.
- **No assets generated:** confirm the files are directly in the expected folder and follow that asset type's filename rule.
- **Music is skipped:** install requirements again and check that the audio is OGG and the matching image follows the naming rule.
- **Unexpected or missing imported textures:** review the ZIP importer's extracted output and rename or remove incorrect files before rerunning.
- **Output seems to disappear:** the configured pack output directories are cleared at the start of every run.

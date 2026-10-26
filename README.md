# Auto-DP-RP

[![Minecraft Java Edition](https://img.shields.io/badge/Minecraft-Java%20Edition-62B47A?logo=minecraft&logoColor=white)](https://www.minecraft.net/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pillow](https://img.shields.io/badge/Pillow-image%20processing-FFB000)](https://python-pillow.org/)
[![Mutagen](https://img.shields.io/badge/Mutagen-audio%20metadata-8A2BE2)](https://mutagen.readthedocs.io/)
[![English](https://img.shields.io/badge/docs-English-1f6feb)](README.md)
[![Español](https://img.shields.io/badge/docs-Espa%C3%B1ol-EF5350)](README.es.md)

**English** | [Español](README.es.md)

**Auto-DP-RP** is a modular Python automation tool designed to convert organized images, audio files, and selected Bedrock add-on assets into fully compliant **Minecraft Java Edition** Resource Packs and Data Packs. It automates repetitive JSON generation, asset scaling, model translation, and `/give` command scripts for any configured Minecraft version and namespace.

Simply place your source assets inside `pendientes/`, run a single command, and find your ready-to-use packs in `output/`.

---

## Features

- **Modular Architecture:** Extensible processing pipeline for items, equipment, locator-bar waypoints, paintings, and music discs.
- **Automatic Asset Scaling:** Generates multiple resolutions (e.g., `16x16`, `10x10`, `6x6` sprites) automatically from a single PNG for waypoints and UI elements.
- **Centralized Version Control:** Manages and updates Minecraft pack formats independently via `config.json` and an upstream format synchronization script.
- **Smart Bedrock Converter:** Extracts geometries (`.geo.json`) and textures from `.mcaddon`, `.mcpack`, or `.zip` files and translates them into modern Java item models.
- **Automated Command Generation:** Automatically outputs precise `/give` commands into `.mcfunction` files for effortless in-game acquisition.

---

## Quick Start

### Prerequisites

- Python 3.9 or higher.

### Installation & Execution

1. Install the required Python dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

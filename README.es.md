# Auto-DP-RP

[![Minecraft Java Edition](https://img.shields.io/badge/Minecraft-Java%20Edition-62B47A?logo=minecraft&logoColor=white)](https://www.minecraft.net/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pillow](https://img.shields.io/badge/Pillow-procesamiento%20de%20im%C3%A1genes-FFB000)](https://python-pillow.org/)
[![Mutagen](https://img.shields.io/badge/Mutagen-metadatos%20de%20audio-8A2BE2)](https://mutagen.readthedocs.io/)
[![English](https://img.shields.io/badge/docs-English-1f6feb)](README.md)
[![Español](https://img.shields.io/badge/docs-Espa%C3%B1ol-EF5350)](README.es.md)

[English](README.md) | **Español**

Auto-DP-RP es una herramienta en Python que convierte imágenes, audio y ciertos recursos de complementos Bedrock organizados en archivos de resource pack y data pack para Minecraft Java Edition. Automatiza la creación de archivos JSON, modelos, texturas y comandos `/give` para una versión y un namespace configurados.

Coloca los recursos de origen en `pendientes/`, ejecuta el generador y encuentra los packs en `output/`. La configuración actual usa el namespace `btc`, la versión de Minecraft `26.3` y las carpetas de salida `BTC Assets` y `BTC DP`.

## Qué genera

- **Items y equipamiento personalizados:** definiciones de items, modelos y texturas Java; el equipamiento admite los slots `head`, `chest`, `legs`, `feet`, `body` y `elytra`.
- **Waypoints de la barra localizadora:** tres tamaños de sprite y una definición de estilo por cada PNG.
- **Pinturas personalizadas:** texturas, modelos de item, variantes data-driven, inclusión opcional en supervivencia y comandos `/give`.
- **Discos de música:** sonidos OGG, iconos de 16×16, definiciones de canciones para jukebox, eventos de sonido y comandos `/give`.
- **Recursos Bedrock:** extracción de pares compatibles de geometría y textura desde complementos, seguida de la conversión de modelos preparados a modelos de item Java.
- **Metadatos de resource pack y data pack:** genera `pack.mcmeta` según los formatos de pack de la versión activa en `config.json`.

El proyecto genera packs para Java Edition. Los complementos Bedrock son una entrada opcional para el flujo de conversión de modelos; la salida no es un pack Bedrock.

## Inicio rápido

Requisito: Python 3.9 o posterior.

```powershell
python -m pip install -r requirements.txt
python generator/main.py
```

Ejecuta los comandos desde la raíz del proyecto para que el generador encuentre `config.json`. En cada ejecución, se vacían y regeneran las carpetas configuradas para el resource pack y el data pack. Haz una copia de cualquier archivo que quieras conservar antes de ejecutar el generador.

## Documentación

- [Guía de uso en español](docs/USAGE.es.md)
- [Usage guide in English](docs/USAGE.md)
- [English introduction](README.md)

## Estructura del proyecto

```text
config.json                 Configuración y formatos de pack admitidos
generator/
  main.py                   Punto de entrada del generador
  config.py                 Carga la configuración desde config.json
  update_formats.py         Actualizador opcional de formatos de Minecraft
  modules/                  Procesadores de items, equipamiento, waypoints,
                            pinturas, música, ZIP y recursos Bedrock
pendientes/                 Recursos de entrada (creados desde config.json)
output/                     Resource pack y data pack Java generados
docs/                       Guías de uso paso a paso
```

## Configuración general

Edita `config.json` para cambiar el namespace, las carpetas de entrada/salida, los nombres de las carpetas de packs, la versión activa o las subcarpetas de entrada. La versión activa debe existir en `MINECRAFT_VERSIONS`.

El actualizador opcional puede obtener la tabla de formatos desde la fuente de datos de Minecraft:

```powershell
python generator/update_formats.py
```

Necesita conexión a internet y reemplaza la tabla `MINECRAFT_VERSIONS` de `config.json`; no cambia `ACTIVE_VERSION`. Revisa la configuración antes de generar los packs.

## Referencias

- [Iconos de la barra localizadora por Colebot](https://youtu.be/UY1kFVoLf5E?si=FSxYw3GQCGO3FQkC)
- [Modelos personalizados para Model Applier por Braytonks](https://youtu.be/AIHpN6QYQMA?si=gJ_iKANpi5cT2B6O)

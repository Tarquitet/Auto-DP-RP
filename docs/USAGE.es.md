# Guía de uso

**Español** | [English](USAGE.md)

Esta guía explica cómo preparar los archivos de entrada, ejecutar Auto-DP-RP y encontrar los packs generados para Minecraft Java Edition.

## 1. Instalar y ejecutar

Desde la raíz del proyecto, instala los requisitos y ejecuta el generador:

```powershell
python -m pip install -r requirements.txt
python generator/main.py
```

El generador lee `config.json` desde el directorio de trabajo actual. Ejecuta los comandos desde la raíz del proyecto. Para usar otras carpetas raíz de entrada y salida:

```powershell
python generator/main.py --input otra-entrada --output otra-salida
```

El namespace, la versión de Minecraft y los nombres de las carpetas de los packs siguen obteniéndose de `config.json`. Las subcarpetas de entrada configuradas se crean automáticamente dentro de la carpeta seleccionada.

> **Importante:** cada ejecución borra de forma recursiva las carpetas configuradas para el resource pack y el data pack antes de volver a generarlas. No guardes archivos de origen ni archivos editados manualmente dentro de esas carpetas.

## 2. Carpetas de entrada

La configuración actual crea esta estructura en `pendientes/`:

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

Coloca los archivos de origen en la carpeta correspondiente. El generador procesa los archivos directamente dentro de cada carpeta, no subcarpetas arbitrarias.

## 3. Preparar cada tipo de recurso

### Items personalizados

Coloca archivos PNG en `pendientes/items/` y nómbralos `nombre_itemBase.png`. Por ejemplo:

```text
emerald_badge_diamond.png
```

El generador separa el nombre en el **último guion bajo**: `emerald_badge` será el nombre del item generado y `diamond` será el ID del item base usado por el comando `/give`. Por tanto, la parte del item base debe ser un solo segmento sin guiones bajos; la parte anterior sí puede contenerlos.

Cuando encuentra al menos un item válido, genera su definición, modelo, textura y el archivo de comandos `get_items.mcfunction`.

### Equipamiento

Coloca texturas PNG en `pendientes/equipment/` y usa el formato `nombre_slot.png`. Slots admitidos:

| Slot | Capa de equipamiento |
| --- | --- |
| `head` | `humanoid` |
| `chest` | `humanoid` |
| `legs` | `humanoid_leggings` |
| `feet` | `humanoid` |
| `body` | `wings` |
| `elytra` | `wings` |

También puedes proporcionar un icono de inventario opcional llamado `nombre_slot_icon.png`. Si no existe, la textura completa se usa también como icono. Por ejemplo, `silver_wolf_head.png` puede tener como icono `silver_wolf_head_icon.png`.

### Waypoints de la barra localizadora

Coloca archivos PNG en `pendientes/waypoints/`. El patrón admitido es:

```text
nombre_cerca_medio_lejos.png
```

Por ejemplo, `town_4_16_32.png`. Si el archivo no tiene los tres sufijos numéricos, se procesa con los valores predeterminados `4`, `16` y `32`. Cada imagen se convierte en sprites de 16×16, 10×10 y 6×6. El JSON de estilo usa el primer valor como `near_distance` y el tercero como `far_distance`; actualmente el valor del medio no se escribe en el JSON generado.

### Pinturas

Coloca imágenes PNG, JPG, JPEG o WebP en `pendientes/paintings/` y nombra cada archivo así:

```text
nombre_anchoXalto_autor_supervivencia.ext
```

Ejemplo: `sunset_2x3_Alex_si.png`. Usa un único valor sin guiones bajos para cada campo de nombre, tamaño y autor. Escribe `si` en el último campo para incluir la pintura en el tag generado `minecraft:painting_variant/placeable`; cualquier otro valor la excluye. La imagen también se reduce a un icono de item de 16×16.

### Discos de música

Para cada canción, coloca un archivo OGG y una imagen relacionada en `pendientes/music/`:

```text
evening.ogg
evening_Alex_12.png
```

El nombre de la imagen debe empezar exactamente con el nombre base del archivo OGG, seguido de `_autor_comparador`. Usa un solo valor de autor sin guiones bajos. La imagen puede ser PNG, JPG, JPEG o WebP. El comparador debe ser numérico; un valor no válido se reemplaza por `15`. El generador lee la duración del OGG con Mutagen y crea el sonido, el icono, la definición de la canción para jukebox y el archivo de comandos `get_discs.mcfunction`.

### Importar imágenes de ZIP de resource packs

Coloca archivos `.zip` directamente en `pendientes/importar_zips/`. El importador busca PNG dentro de los archivos y usa sus rutas internas para clasificar posibles texturas de entidad/armadura/modelo como equipamiento y texturas de item como iconos de inventario. Omite rutas que contengan `gui` o `environment`. Es un importador heurístico: revisa las imágenes extraídas en `pendientes/equipment/` y corrige nombres o asociaciones antes de confiar en el pack generado.

### Convertir modelos Bedrock compatibles

Coloca archivos `.mcaddon`, `.mcpack` o `.zip` en `pendientes/bedrock_addons/`. El extractor busca JSON de geometría Bedrock y texturas coincidentes, incluso dentro de packs anidados en un archivo, y prepara los pares compatibles en `pendientes/bedrock_staging/`. Después, el conversor genera modelos de item Java y el archivo `get_bedrock_items.mcfunction`.

También puedes colocar directamente un par coincidente en staging:

```text
pendientes/bedrock_staging/example.geo.json
pendientes/bedrock_staging/example.png
```

La conversión es de mejor esfuerzo: puede omitir geometrías no compatibles o pares sin textura. Revisa el modelo generado y pruébalo en Minecraft antes de publicarlo.

## 4. Encontrar los archivos generados

La configuración actual de `config.json` coloca los packs en:

```text
output/
├── BTC Assets/    Resource pack
└── BTC DP/        Data pack
```

Estos nombres se pueden cambiar con `RP_FOLDER_NAME` y `DP_FOLDER_NAME`. Cada pack recibe un `pack.mcmeta` generado a partir de `ACTIVE_VERSION` y su entrada en `MINECRAFT_VERSIONS`.

Los archivos de comandos se escriben en `data/<namespace>/function/` dentro del data pack:

- `get_items.mcfunction`
- `get_paintings.mcfunction`
- `get_discs.mcfunction`
- `get_bedrock_items.mcfunction`

Solo se crean archivos para los tipos de recursos que generaron entradas válidas. El equipamiento y los waypoints no generan archivos de comandos.

## 5. Configuración y actualización de formatos

Edita `config.json` para configurar:

- `NAMESPACE`: namespace usado en IDs y rutas generados.
- `INPUT_FOLDER`, `OUTPUT_FOLDER`: carpetas raíz de entrada y salida.
- `RP_FOLDER_NAME`, `DP_FOLDER_NAME`: nombres de las carpetas de resource pack y data pack.
- `ACTIVE_VERSION`: versión de destino; debe ser una clave de `MINECRAFT_VERSIONS`.
- `INPUT_SUBFOLDERS`: carpetas que se crean bajo la carpeta raíz de entrada.

Para actualizar la tabla de formatos desde la fuente de datos externa, ejecuta:

```powershell
python generator/update_formats.py
```

Este paso opcional necesita conexión a internet y reemplaza la tabla `MINECRAFT_VERSIONS` de `config.json`. Conserva `ACTIVE_VERSION`; comprueba que la versión activa siga disponible antes de generar los packs.

## Solución de problemas

- **Versión de Minecraft desconocida:** asigna a `ACTIVE_VERSION` una clave existente en `MINECRAFT_VERSIONS`.
- **No se encuentra la carpeta de entrada:** ejecuta desde la raíz del proyecto o revisa `INPUT_FOLDER` / `--input`.
- **No se generan recursos:** confirma que los archivos estén directamente en la carpeta correcta y respeten la regla de nombres correspondiente.
- **Se omite la música:** vuelve a instalar los requisitos y comprueba que el audio sea OGG y que su imagen coincidente use el formato esperado.
- **Texturas importadas incorrectas o ausentes:** revisa los archivos extraídos por el importador ZIP y renombra o elimina los archivos incorrectos antes de volver a ejecutar.
- **Parece que desapareció la salida:** las carpetas configuradas de los packs se vacían al inicio de cada ejecución.

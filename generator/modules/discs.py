import json
import shutil
from pathlib import Path
from PIL import Image

try:
    from mutagen.oggvorbis import OggVorbis
except ImportError:
    OggVorbis = None

try:
    from generator.utils import write_json
except ModuleNotFoundError:
    from utils import write_json

def process(input_path: Path, rp_path: Path, dp_path: Path, namespace: str):
    print("Processing custom music discs...")
    folder = input_path / "music"
    if not folder.exists():
        return
        
    if OggVorbis is None:
        print("  [Error] La librería 'mutagen' no está instalada. Canciones omitidas.")
        print("  Ejecuta: pip install mutagen")
        return
        
    commands = [f"# Comandos generados para discos en {namespace}", ""]
    sounds_json = {}
    
    # Buscar todos los archivos de audio OGG
    for audio_file in sorted(folder.glob("*.ogg")):
        base_name = audio_file.stem
        
        # Buscar la imagen complementaria que tiene los datos en su nombre
        image_files = list(folder.glob(f"{base_name}_*.*"))
        if not image_files:
            print(f"  [Advertencia] No hay imagen/metadatos para {audio_file.name}. (Usa: cancion_Autor_Señal.png)")
            continue
            
        image_path = image_files[0]
        if image_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.webp']:
            continue
            
        parts = image_path.stem.split("_")
        if len(parts) != 3:
            print(f"  [Advertencia] Formato incorrecto: {image_path.name} (Usa: cancion_Autor_Señal.png)")
            continue
            
        _, author, comparator = parts
        
        try:
            comparator = int(comparator)
        except ValueError:
            comparator = 15
            
        # 1. MÁGIA: Leer los segundos exactos de la canción
        try:
            audio_info = OggVorbis(audio_file)
            length_seconds = int(audio_info.info.length)
        except Exception as e:
            print(f"  [Error] No se pudo procesar la duración de {audio_file.name}: {e}")
            continue
            
        # 2. Copiar Audio al Resource Pack
        audio_dest = rp_path / "assets" / namespace / "sounds" / "records" / f"{base_name}.ogg"
        audio_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(audio_file, audio_dest)
        
        # Registrar evento de sonido
        sounds_json[f"music_disc.{base_name}"] = {
            "sounds": [{"name": f"{namespace}:records/{base_name}", "stream": True}]
        }
        
        # 3. Procesar Ícono miniatura 16x16
        tex_item_dir = rp_path / "assets" / namespace / "textures" / "item"
        tex_item_dir.mkdir(parents=True, exist_ok=True)
        with Image.open(image_path) as img:
            img.convert("RGBA").resize((16, 16), Image.Resampling.NEAREST).save(tex_item_dir / f"{base_name}.png", "PNG")
            
        # 4. Crear Modelo del Ítem
        write_json(
            rp_path / "assets" / namespace / "models" / "item" / f"{base_name}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"{namespace}:item/{base_name}"}}
        )
        
        # 5. Data Pack (Jukebox Song Data-driven)
        titulo_limpio = base_name.replace('-', ' ').replace('_', ' ').title()
        write_json(
            dp_path / "data" / namespace / "jukebox_song" / f"{base_name}.json",
            {
                "sound_event": {"sound_id": f"{namespace}:music_disc.{base_name}"},
                "description": {"text": f"{author} - {titulo_limpio}"},
                "length_in_seconds": length_seconds,
                "comparator_output": comparator
            }
        )
        
        # 6. Crear comando give con componentes modernos 1.21
        commands.extend([
            f"# Disco: {titulo_limpio} por {author}",
            f"give @p music_disc_11[minecraft:jukebox_playable={{song:\"{namespace}:{base_name}\"}},minecraft:item_model=\"{namespace}:item/{base_name}\",minecraft:item_name='{{\"text\":\"Disco de Musica\", \"italic\":false}}',minecraft:lore=['{{\"text\":\"{author} - {titulo_limpio}\",\"color\":\"gray\",\"italic\":false}}']] 1",
            ""
        ])
        print(f"  Disco: {base_name} | Duración: {length_seconds}s | Señal Redstone: {comparator}")
        
    # Escribir sounds.json acumulado
    if sounds_json:
        write_json(rp_path / "assets" / namespace / "sounds.json", sounds_json)
        
    # Escribir el mcfunction
    if len(commands) > 2:
        command_file = dp_path / "data" / namespace / "function" / "get_discs.mcfunction"
        command_file.parent.mkdir(parents=True, exist_ok=True)
        command_file.write_text("\n".join(commands), encoding="utf-8")
from pathlib import Path
from mutagen.oggvorbis import OggVorbis

try:
    from generator.utils import write_json
except ModuleNotFoundError:
    from utils import write_json

def process(input_path: Path, rp_path: Path, dp_path: Path, namespace: str):
    print("\n🎵 Procesando discos de música...")
    folder = input_path / "music"
    
    if not folder.exists():
        print("  ⚠️ Carpeta 'music' no existe. Saltando.")
        return
    
    sounds_json = {}
    archivos_procesados = 0
    
    for audio_path in sorted(folder.glob("*.ogg")):
        parts = audio_path.stem.split("_")
        
        # ACEPTA 3 O 4 PARTES
        if len(parts) == 3:
            base_name, author, comparator_str = parts
        elif len(parts) == 4:
            base_name, author, comparator_str, _ = parts
        else:
            print(f"  ⚠️ Saltando {audio_path.name} (usa: nombre_Autor_15 o nombre_Autor_15_si)")
            continue
        
        try:
            comparator = int(comparator_str)
        except ValueError:
            print(f"  ❌ Comparador inválido en {audio_path.name}. Usa un número.")
            continue
        
        sounds_dir = rp_path / "assets" / namespace / "sounds" / "music_disc"
        sounds_dir.mkdir(parents=True, exist_ok=True)
        
        dest_audio = sounds_dir / f"{base_name}.ogg"
        with open(audio_path, "rb") as f_in, open(dest_audio, "wb") as f_out:
            f_out.write(f_in.read())
        
        try:
            audio = OggVorbis(str(audio_path))
            length_seconds = round(audio.info.length, 2)
        except Exception:
            length_seconds = 0.0
        
        sounds_json[f"music_disc.{base_name}"] = {
            "sounds": [f"{namespace}:music_disc/{base_name}"]
        }
        
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
        
        archivos_procesados += 1
        print(f"  ✅ {base_name} ({length_seconds}s, comparador: {comparator})")
    
    if sounds_json:
        write_json(rp_path / "assets" / namespace / "sounds.json", sounds_json)
    
    print(f"  📊 Total discos procesados: {archivos_procesados}\n")
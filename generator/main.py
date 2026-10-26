import argparse
import pkgutil
import inspect
import json
from pathlib import Path

try:
    from generator import config
    from generator import modules
    from generator.utils import clean_and_create, write_json, inicializar_carpetas
except ModuleNotFoundError:
    import config
    import modules
    from utils import clean_and_create, write_json, inicializar_carpetas


def crear_mcmeta(fmt, description: str) -> dict:
    if isinstance(fmt, list):
        return {
            "pack": {
                "description": description,
                "min_format": fmt,
                "max_format": fmt,
            }
        }
    return {"pack": {"pack_format": fmt, "description": description}}


def main():
    parser = argparse.ArgumentParser(description="Generate Minecraft Java packs.")
    parser.add_argument("--input", type=str, default=str(config.INPUT_FOLDER))
    parser.add_argument("--output", type=str, default=str(config.OUTPUT_FOLDER))
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # 0. GENERAR CARPETAS AUTOMÁTICAMENTE AL INICIAR DESDE EL JSON
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            raw_config = json.load(f)
        inicializar_carpetas(raw_config, input_path, output_path)

    version_config = config.MINECRAFT_VERSIONS.get(config.ACTIVE_VERSION)
    if version_config is None:
        parser.error(f"Unknown Minecraft version: {config.ACTIVE_VERSION}")
    if not input_path.exists():
        parser.error(f"Input folder does not exist: {input_path}")

    java_rp = output_path / config.RP_FOLDER_NAME
    java_dp = output_path / config.DP_FOLDER_NAME

    print(f"Starting Resourcepack generator ({config.ACTIVE_VERSION})...")
    for path in (java_rp, java_dp):
        clean_and_create(path)

    # 1. EJECUTAR TODOS LOS MIGRADORES PRIMERO (Zips y Addons de Bedrock)
    if hasattr(modules, "migrator"):
        modules.migrator.procesar_zips_automaticamente(input_path)
    if hasattr(modules, "bedrock_migrator"):
        modules.bedrock_migrator.process(input_path, java_rp, config.NAMESPACE)

    # 2. GENERAR PACK.MCMETA COMPATIBLE CON VERSIONES VIEJAS Y 26.X ([major, minor])
    description = f"Builtechraft Auto-Pack (v{config.ACTIVE_VERSION})"
    write_json(
        java_rp / "pack.mcmeta",
        crear_mcmeta(version_config["resource_pack_format"], description),
    )
    write_json(
        java_dp / "pack.mcmeta",
        crear_mcmeta(version_config["data_pack_format"], description),
    )

    # 3. EJECUCIÓN DINÁMICA DE TODOS LOS DEMÁS MÓDULOS
    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
        if module_name in ("migrator", "bedrock_migrator"):
            continue

        module = getattr(modules, module_name, None)
        if module and hasattr(module, "process"):
            sig = inspect.signature(module.process)
            params_count = len(sig.parameters)

            if params_count == 3:
                module.process(input_path, java_rp, config.NAMESPACE)
            elif params_count >= 4:
                module.process(input_path, java_rp, java_dp, config.NAMESPACE)

    print("Java generation completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
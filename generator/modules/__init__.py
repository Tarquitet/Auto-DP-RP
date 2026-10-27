import os
import importlib

# Cargar automáticamente todos los .py de esta carpeta
_dir = os.path.dirname(__file__)
for _f in os.listdir(_dir):
    if _f.endswith('.py') and not _f.startswith('_'):
        _name = _f[:-3]
        try:
            globals()[_name] = importlib.import_module(f".{_name}", package=__name__)
        except ImportError:
            globals()[_name] = importlib.import_module(f"generator.modules.{_name}")
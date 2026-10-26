import pkgutil
from pathlib import Path

# Carga dinámica automática de todos los módulos en esta carpeta
for _, module_name, _ in pkgutil.iter_modules([str(Path(__file__).parent)]):
    __import__(f"{__name__}.{module_name}")
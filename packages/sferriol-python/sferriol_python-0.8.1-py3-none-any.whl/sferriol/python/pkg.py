import importlib
import pkgutil
import sys

from sferriol.python import module_name_from_file


def reload(pkg):
    "Reload package and its sub modules"
    pkg_name = pkg.__name__
    pkg_path = pkg.__path__
    if pkg_name in sys.modules:
        importlib.reload(sys.modules[pkg_name])
    for _, module_name, _ in pkgutil.iter_modules(pkg_path):
        module = f"{pkg_name}.{module_name}"
        if module in sys.modules:
            importlib.reload(sys.modules[module])

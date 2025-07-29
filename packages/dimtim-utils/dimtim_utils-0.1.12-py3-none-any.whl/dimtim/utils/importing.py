import os
import sys
from importlib import import_module
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader


def safe_import(module: str, silence: bool = True, reraise: bool = False):
    try:
        return import_module(module)
    except ImportError as e:
        if not silence:
            sys.stdout.write(f'Module {module} importing error: {e}\n')
        if reraise:
            raise e


def import_string(path: str):
    try:
        module_path, class_name = path.strip().rsplit('.', 1)
    except ValueError as e:
        raise ImportError(f'"{path}" doesn\'t look like a module path') from e

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(f'Module "{module_path}" does not define a "{class_name}" attribute') from e


def load_file_as_module(path: str, name: str = None, execute: bool = True):
    name = name or os.path.splitext(os.path.basename(path))[0]
    loader = SourceFileLoader(name, path)
    module = module_from_spec(spec_from_loader(loader.name, loader))
    if execute:
        loader.exec_module(module)
    return loader, module

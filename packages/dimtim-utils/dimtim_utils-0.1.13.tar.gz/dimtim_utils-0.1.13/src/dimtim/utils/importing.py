import os
import sys
from importlib import import_module
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader


def safe_import(module: str, silence: bool = True, reraise: bool = False):
    """
    Safely import a module, with options to handle import errors.

    This function attempts to import a module and provides options for handling
    import errors gracefully.

    Parameters:
        module (str): The name of the module to import.
        silence (bool, optional): If True, suppress error messages. Default is True.
        reraise (bool, optional): If True, re-raise ImportError. Default is False.

    Returns:
        module or None: The imported module if successful, None otherwise (unless reraise is True).

    Raises:
        ImportError: If the module cannot be imported and reraise is True.

    Example:
        >>> # Try to import an optional dependency
        >>> numpy = safe_import('numpy')
        >>> if numpy:
        ...     # Use numpy
        ...     pass
        ... else:
        ...     # Fall back to alternative implementation
        ...     pass
    """
    try:
        return import_module(module)
    except ImportError as e:
        if not silence:
            sys.stdout.write(f'Module {module} importing error: {e}\n')
        if reraise:
            raise e
        return None


def import_string(path: str):
    """
    Import a class or object by its string path.

    This function imports a class, function, or other object from a module
    using a dotted path string (e.g., 'package.module.Class').

    Parameters:
        path (str): The dotted path to the object to import.

    Returns:
        Any: The imported class or object.

    Raises:
        ImportError: If the module or attribute cannot be found.

    Example:
        >>> # Import a class by string
        >>> JsonResponse = import_string('django.http.JsonResponse')

        >>> # Use the imported class
        >>> response = JsonResponse({'status': 'ok'})
    """
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
    """
    Load a Python file as a module without importing it through the Python path.

    This function allows loading a Python file directly from a file path,
    without requiring it to be in the Python path.

    Parameters:
        path (str): The file path to the Python file.
        name (str, optional): The name to give the module. If None, uses the filename.
        execute (bool, optional): If True, execute the module code. Default is True.

    Returns:
        tuple: A tuple containing (loader, module).

    Example:
        >>> # Load a Python file as a module
        >>> loader, module = load_file_as_module('/path/to/script.py')

        >>> # Access attributes or functions from the module
        >>> result = module.some_function()
    """
    name = name or os.path.splitext(os.path.basename(path))[0]
    loader = SourceFileLoader(name, path)
    module = module_from_spec(spec_from_loader(loader.name, loader))
    if execute:
        loader.exec_module(module)
    return loader, module

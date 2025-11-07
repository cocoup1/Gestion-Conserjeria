#!/usr/bin/env python
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import sys

if sys.stdout is None:
    import io
    sys.stdout = io.StringIO()
if sys.stderr is None:
    import io
    sys.stderr = io.StringIO()

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Agregar la lógica para ejecutar 'runserver' si no se pasa un subcomando
    if len(sys.argv) == 1:
        sys.argv.append("runserver")  # Ejecutar el servidor por defecto si no se pasa argumento

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

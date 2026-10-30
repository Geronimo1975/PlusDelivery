#!/usr/bin/env python
"""Utilitarul de linie de comanda Django (migrari, pornire server etc.)."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plusdelivery.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Nu am gasit Django. Ai activat mediul virtual si ai rulat "
            "'pip install -r requirements.txt'?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

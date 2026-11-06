"""
Файл запуска программы FinSafe.

Именно этот файл указывают в PyInstaller при сборке exe-файла (лабораторная работа 6),
а при разработке запускают командой: python run_finsafe.py
"""

from finsafe.cli import main

if __name__ == "__main__":
    main()

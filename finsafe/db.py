"""
Модуль работы с базой данных.

Отвечает за три вещи:
    1. Выбор места, где лежит файл базы (get_default_db_path).
    2. Открытие соединения с базой (connect).
    3. Создание таблиц и справочника категорий при первом запуске (init_db).

Все суммы хранятся в базе в копейках (целые числа). Так мы не получаем
ошибок округления, которые бывают у дробных чисел: 0.1 + 0.2 != 0.3.
"""

import os
import sqlite3
from pathlib import Path

# Имя папки программы внутри каталога данных пользователя.
APP_DIR_NAME = "FinSafe"

# Справочник категорий, который создаётся при первом запуске.
# Формат записи: (название, тип), где "income" это доход, "expense" это расход.
DEFAULT_CATEGORIES = [
    ("Зарплата", "income"),
    ("Подработка", "income"),
    ("Продукты", "expense"),
    ("Транспорт", "expense"),
    ("Жильё", "expense"),
    ("Развлечения", "expense"),
    ("Здоровье", "expense"),
    ("Одежда", "expense"),
]

# SQL-скрипт создания таблиц. Это упрощённая версия схемы finsafe_db
# из лабораторной работы 3: пять таблиц вместо восьми, без пользователей и банков.
# Слова IF NOT EXISTS позволяют запускать скрипт повторно без ошибок.
SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id_account  INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    balance     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id_category INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    kind        TEXT    NOT NULL CHECK (kind IN ('income', 'expense'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id_transaction INTEGER PRIMARY KEY AUTOINCREMENT,
    id_account     INTEGER NOT NULL
        REFERENCES accounts(id_account)    ON DELETE CASCADE ON UPDATE CASCADE,
    id_category    INTEGER NOT NULL
        REFERENCES categories(id_category) ON DELETE CASCADE ON UPDATE CASCADE,
    amount         INTEGER NOT NULL CHECK (amount > 0),
    kind           TEXT    NOT NULL CHECK (kind IN ('income', 'expense')),
    trans_date     TEXT    NOT NULL,
    comment        TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS budget_plans (
    id_budget    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_category  INTEGER NOT NULL
        REFERENCES categories(id_category) ON DELETE CASCADE ON UPDATE CASCADE,
    month        TEXT    NOT NULL,
    limit_amount INTEGER NOT NULL CHECK (limit_amount > 0),
    UNIQUE (id_category, month)
);

CREATE TABLE IF NOT EXISTS financial_goals (
    id_goal        INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    target_amount  INTEGER NOT NULL CHECK (target_amount > 0),
    current_amount INTEGER NOT NULL DEFAULT 0,
    status         TEXT    NOT NULL DEFAULT 'Активна'
        CHECK (status IN ('Активна', 'Завершена', 'Отменена'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(trans_date);
"""


def get_default_db_path():
    """
    Возвращает путь к файлу базы данных по умолчанию.

    Файл нельзя хранить рядом с программой: после установки в Program Files
    Windows запрещает обычному пользователю писать в эту папку. Поэтому база
    лежит в каталоге данных пользователя, например
    C:\\Users\\Maria\\AppData\\Roaming\\FinSafe\\finsafe.db
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        # Windows: переменная APPDATA указывает на папку AppData\Roaming.
        base = Path(appdata)
    else:
        # Linux и macOS: используем скрытую папку в домашнем каталоге.
        base = Path.home() / ".local" / "share"

    folder = base / APP_DIR_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "finsafe.db"


def connect(db_path=None):
    """
    Открывает соединение с базой и подготавливает его к работе.

    db_path: путь к файлу базы. Если не указан, берётся путь по умолчанию.
             Строка ":memory:" создаёт временную базу в оперативной памяти,
             её используют автоматические тесты.
    """
    if db_path is None:
        db_path = get_default_db_path()

    conn = sqlite3.connect(str(db_path))

    # Row позволяет обращаться к столбцам по имени: row["name"].
    conn.row_factory = sqlite3.Row

    # По умолчанию SQLite не проверяет внешние ключи, включаем проверку.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    """Создаёт таблицы и заполняет справочник категорий, если он пуст."""
    conn.executescript(SCHEMA)

    row = conn.execute("SELECT COUNT(*) AS cnt FROM categories").fetchone()
    if row["cnt"] == 0:
        conn.executemany(
            "INSERT INTO categories (name, kind) VALUES (?, ?)",
            DEFAULT_CATEGORIES,
        )
        conn.commit()

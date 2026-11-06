"""
Консольный интерфейс FinSafe.

Главное меню повторяет три блока веб-приложения и макетов Figma:
    1. Добавление данных
    2. Просмотр и управление данными
    3. Аналитика

Запуск:
    python run_finsafe.py            обычный запуск
    python run_finsafe.py --demo     заполнить пустую базу демонстрационными данными
    python run_finsafe.py --db my.db использовать другой файл базы
"""

import argparse
import sys
from datetime import date

from finsafe import __version__
from finsafe import db
from finsafe import services


# ---------------------------------------------------------------------------
# Вспомогательные функции ввода и вывода
# ---------------------------------------------------------------------------

def ask(prompt, default=None):
    """
    Запрашивает строку у пользователя.
    Если пользователь нажал Enter и значение по умолчанию задано, возвращает его.
    """
    if default is not None:
        text = input("{} [{}]: ".format(prompt, default)).strip()
        if text == "":
            return default
        return text
    return input("{}: ".format(prompt)).strip()


def ask_int(prompt):
    """Запрашивает целое число. Если ввод не число, вызывает ValueError."""
    text = ask(prompt)
    try:
        return int(text)
    except ValueError:
        raise ValueError("Нужно ввести целое число")


def print_title(text):
    """Печатает заголовок раздела с линией."""
    print()
    print(text)
    print("-" * len(text))


def print_accounts(conn):
    """Печатает список счетов с остатками и возвращает True, если счета есть."""
    accounts = services.list_accounts(conn)
    if len(accounts) == 0:
        print("Счетов пока нет. Добавьте счёт в блоке «Добавление данных».")
        return False
    for acc in accounts:
        print("  {}. {:<24}{:>16}".format(
            acc["id_account"], acc["name"], services.format_money(acc["balance"])))
    return True


def print_categories(conn, kind):
    """Печатает список категорий нужного типа."""
    for cat in services.list_categories(conn, kind):
        print("  {}. {}".format(cat["id_category"], cat["name"]))


def print_transactions(rows):
    """Печатает таблицу операций."""
    if len(rows) == 0:
        print("Операций нет.")
        return
    print("{:>4}  {:<10}  {:<22}  {:<12}  {:<20}{:>14}".format(
        "№", "Дата", "Счёт", "Категория", "Комментарий", "Сумма"))
    for row in rows:
        # Доход показываем со знаком +, расход со знаком -.
        if row["kind"] == services.KIND_INCOME:
            amount = "+" + services.format_money(row["amount"])
        else:
            amount = "-" + services.format_money(row["amount"])
        print("{:>4}  {:<10}  {:<22}  {:<12}  {:<20}{:>14}".format(
            row["id_transaction"], row["trans_date"], row["account_name"],
            row["category_name"], row["comment"][:20], amount))


# ---------------------------------------------------------------------------
# Блок 1. Добавление данных
# ---------------------------------------------------------------------------

def action_add_transaction(conn):
    """Диалог добавления дохода или расхода."""
    print_title("Новая операция")

    kind_text = ask("Тип операции (1 - расход, 2 - доход)", "1")
    if kind_text == "1":
        kind = services.KIND_EXPENSE
    elif kind_text == "2":
        kind = services.KIND_INCOME
    else:
        raise ValueError("Введите 1 или 2")

    print("Счета:")
    if not print_accounts(conn):
        return
    id_account = ask_int("Номер счёта")

    print("Категории:")
    print_categories(conn, kind)
    id_category = ask_int("Номер категории")

    amount = services.to_kopecks(ask("Сумма, ₽"))
    trans_date = ask("Дата (ГГГГ-ММ-ДД)", date.today().isoformat())
    comment = ask("Комментарий (можно пропустить)", "")

    services.add_transaction(conn, id_account, id_category, amount, kind, trans_date, comment)
    balance = services.get_balance(conn, id_account)
    print("Операция сохранена. Остаток на счёте: {}".format(services.format_money(balance)))


def action_add_account(conn):
    """Диалог создания счёта."""
    print_title("Новый счёт")
    name = ask("Название счёта")
    balance_text = ask("Начальный остаток, ₽", "0")

    # Ноль допустим для счёта, поэтому проверяем его отдельно от to_kopecks.
    if balance_text == "0":
        balance = 0
    else:
        balance = services.to_kopecks(balance_text)

    services.create_account(conn, name, balance)
    print("Счёт создан.")


def action_set_budget(conn):
    """Диалог задания месячного лимита по категории расходов."""
    print_title("Бюджетный план")
    print("Категории расходов:")
    print_categories(conn, services.KIND_EXPENSE)
    id_category = ask_int("Номер категории")
    month = ask("Месяц (ГГГГ-ММ)", services.current_month())
    limit = services.to_kopecks(ask("Лимит на месяц, ₽"))

    services.set_budget(conn, id_category, month, limit)
    print("Лимит сохранён.")


def action_create_goal(conn):
    """Диалог создания цели накопления."""
    print_title("Новая цель накопления")
    name = ask("Название цели")
    target = services.to_kopecks(ask("Целевая сумма, ₽"))
    services.create_goal(conn, name, target)
    print("Цель создана со статусом «{}».".format(services.STATUS_ACTIVE))


def action_add_to_goal(conn):
    """Диалог пополнения цели."""
    print_title("Пополнение цели")
    print_goals(conn)
    id_goal = ask_int("Номер цели")
    amount = services.to_kopecks(ask("Сумма пополнения, ₽"))
    status = services.add_to_goal(conn, id_goal, amount)
    print("Цель пополнена. Статус: {}".format(status))


def menu_add(conn):
    """Подменю «Добавление данных»."""
    while True:
        print_title("1. Добавление данных")
        print("  1. Добавить операцию")
        print("  2. Добавить счёт")
        print("  3. Задать бюджетный план")
        print("  4. Создать цель накопления")
        print("  5. Пополнить цель")
        print("  0. Назад")
        choice = ask("Выберите пункт")

        if choice == "0":
            return
        run_action(conn, choice, {
            "1": action_add_transaction,
            "2": action_add_account,
            "3": action_set_budget,
            "4": action_create_goal,
            "5": action_add_to_goal,
        })


# ---------------------------------------------------------------------------
# Блок 2. Просмотр и управление данными
# ---------------------------------------------------------------------------

def print_goals(conn):
    """Печатает цели с процентом выполнения."""
    goals = services.list_goals(conn)
    if len(goals) == 0:
        print("Целей пока нет.")
        return
    for goal in goals:
        percent = int(goal["current_amount"] * 100 / goal["target_amount"])
        print("  {}. {:<22}{:>14} из {:<14} {:>3}%  {}".format(
            goal["id_goal"], goal["name"],
            services.format_money(goal["current_amount"]),
            services.format_money(goal["target_amount"]),
            percent, goal["status"]))


def action_list_transactions(conn):
    """Показывает последние 15 операций."""
    print_title("Последние операции")
    print_transactions(services.list_transactions(conn, limit=15))


def action_delete_transaction(conn):
    """Удаляет операцию по номеру."""
    print_title("Удаление операции")
    print_transactions(services.list_transactions(conn, limit=10))
    id_transaction = ask_int("Номер операции для удаления")
    answer = ask("Удалить операцию {}? (да/нет)".format(id_transaction), "нет")
    if answer.lower() == "да":
        services.delete_transaction(conn, id_transaction)
        print("Операция удалена, остаток счёта пересчитан.")
    else:
        print("Удаление отменено.")


def action_show_accounts(conn):
    """Показывает счета и общий баланс."""
    print_title("Счета")
    if print_accounts(conn):
        total = services.get_total_balance(conn)
        print("  Общий баланс: {}".format(services.format_money(total)))


def action_show_goals(conn):
    """Показывает цели накопления."""
    print_title("Цели накопления")
    print_goals(conn)


def menu_view(conn):
    """Подменю «Просмотр и управление данными»."""
    while True:
        print_title("2. Просмотр и управление данными")
        print("  1. Последние операции")
        print("  2. Удалить операцию")
        print("  3. Счета и общий баланс")
        print("  4. Цели накопления")
        print("  0. Назад")
        choice = ask("Выберите пункт")

        if choice == "0":
            return
        run_action(conn, choice, {
            "1": action_list_transactions,
            "2": action_delete_transaction,
            "3": action_show_accounts,
            "4": action_show_goals,
        })


# ---------------------------------------------------------------------------
# Блок 3. Аналитика
# ---------------------------------------------------------------------------

def action_month_summary(conn):
    """Итоги выбранного месяца: доходы, расходы и сбережения."""
    print_title("Итоги месяца")
    month = ask("Месяц (ГГГГ-ММ)", services.current_month())
    income, expense = services.month_summary(conn, month)
    print("  Доходы:     {:>16}".format(services.format_money(income)))
    print("  Расходы:    {:>16}".format(services.format_money(expense)))
    print("  Сбережения: {:>16}".format(services.format_money(income - expense)))


def action_expenses_by_category(conn):
    """Расходы по категориям с долей от общей суммы и текстовой полоской."""
    print_title("Расходы по категориям")
    month = ask("Месяц (ГГГГ-ММ)", services.current_month())
    rows = services.expenses_by_category(conn, month)
    if len(rows) == 0:
        print("За этот месяц расходов нет.")
        return

    total = 0
    for name, amount in rows:
        total = total + amount

    for name, amount in rows:
        share = int(amount * 100 / total)
        # Одна «галочка» полоски равна пяти процентам.
        bar = "#" * (share // 5)
        print("  {:<12}{:>14}  {:>3}%  {}".format(
            name, services.format_money(amount), share, bar))


def action_budget_status(conn):
    """Исполнение бюджетных планов месяца."""
    print_title("Исполнение бюджета")
    month = ask("Месяц (ГГГГ-ММ)", services.current_month())
    budgets = services.list_budgets(conn, month)
    if len(budgets) == 0:
        print("На этот месяц бюджетные планы не заданы.")
        return

    for info in budgets:
        if info["exceeded"]:
            mark = "ЛИМИТ ПРЕВЫШЕН"
        else:
            mark = "в пределах лимита"
        print("  {:<12}{:>14} из {:<14}{:>4}%  {}".format(
            info["category_name"],
            services.format_money(info["spent"]),
            services.format_money(info["limit"]),
            info["percent"], mark))


def menu_analytics(conn):
    """Подменю «Аналитика»."""
    while True:
        print_title("3. Аналитика")
        print("  1. Итоги месяца")
        print("  2. Расходы по категориям")
        print("  3. Исполнение бюджета")
        print("  0. Назад")
        choice = ask("Выберите пункт")

        if choice == "0":
            return
        run_action(conn, choice, {
            "1": action_month_summary,
            "2": action_expenses_by_category,
            "3": action_budget_status,
        })


# ---------------------------------------------------------------------------
# Главное меню и точка входа
# ---------------------------------------------------------------------------

def run_action(conn, choice, actions):
    """
    Запускает действие по выбранному пункту меню.
    Ошибки ввода (ValueError) показываются пользователю, программа не завершается.
    """
    if choice not in actions:
        print("Нет такого пункта меню.")
        return
    try:
        actions[choice](conn)
    except ValueError as error:
        print("Ошибка: {}".format(error))


def main_menu(conn):
    """Главное меню программы."""
    while True:
        print_title("FinSafe {}: учёт личных финансов".format(__version__))
        print("  1. Добавление данных")
        print("  2. Просмотр и управление данными")
        print("  3. Аналитика")
        print("  0. Выход")
        choice = ask("Выберите пункт")

        if choice == "0":
            print("До свидания!")
            return
        elif choice == "1":
            menu_add(conn)
        elif choice == "2":
            menu_view(conn)
        elif choice == "3":
            menu_analytics(conn)
        else:
            print("Нет такого пункта меню.")


def main(argv=None):
    """Точка входа: разбирает параметры командной строки и запускает меню."""
    parser = argparse.ArgumentParser(description="FinSafe: учёт личных финансов")
    parser.add_argument("--db", help="путь к файлу базы данных")
    parser.add_argument("--demo", action="store_true",
                        help="заполнить пустую базу демонстрационными данными")
    parser.add_argument("--version", action="store_true", help="показать версию и выйти")
    args = parser.parse_args(argv)

    # Если вывод перенаправлен в файл или канал, символы вроде ₽ могут не помещаться
    # в кодировку по умолчанию. Параметр errors="replace" заменяет их на «?» вместо падения.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    if args.version:
        print("FinSafe {}".format(__version__))
        return

    conn = db.connect(args.db)
    db.init_db(conn)

    if args.demo:
        try:
            services.seed_demo(conn)
            print("Демонстрационные данные добавлены.")
        except ValueError as error:
            print("Ошибка: {}".format(error))

    try:
        main_menu(conn)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C или конец ввода: завершаем программу без длинного сообщения об ошибке.
        print()
        print("Работа прервана.")
    finally:
        # Закрываем соединение, даже если программу прервали сочетанием Ctrl+C.
        conn.close()

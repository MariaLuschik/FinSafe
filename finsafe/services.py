"""
Модуль бизнес-логики FinSafe.

Здесь собраны все действия над данными, не зависящие от интерфейса:
    - преобразование сумм (рубли <-> копейки);
    - добавление и удаление операций с пересчётом баланса счёта;
    - бюджетные планы и контроль лимитов;
    - цели накопления со сменой статуса;
    - аналитика за месяц;
    - заполнение базы демонстрационными данными.

Интерфейс (cli.py) и автоматические тесты (tests/) вызывают именно эти функции.
Благодаря такому разделению логику можно проверять тестами без ввода с клавиатуры.
"""

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# Допустимые типы операции.
KIND_INCOME = "income"
KIND_EXPENSE = "expense"

# Статусы цели накопления. Они совпадают с состояниями объекта FinancialGoal
# на диаграмме состояний из лабораторной работы 3.
STATUS_ACTIVE = "Активна"
STATUS_DONE = "Завершена"
STATUS_CANCELLED = "Отменена"


class InsufficientFundsError(ValueError):
    """Ошибка: на счёте не хватает денег для операции."""


# ---------------------------------------------------------------------------
# Работа с суммами
# ---------------------------------------------------------------------------

def to_kopecks(text):
    """
    Переводит введённую сумму в копейки.

    Принимает строки вида "1250", "1250.5", "1 250,50".
    Пробелы внутри числа игнорируются, запятая заменяется на точку.
    Если сумма не число или не больше нуля, вызывает ValueError.
    """
    # Убираем обычные и неразрывные пробелы, запятую меняем на точку.
    cleaned = str(text).replace(" ", "").replace("\u00a0", "").replace(",", ".")

    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ValueError("Сумма должна быть числом, например 1250,50")

    if value <= 0:
        raise ValueError("Сумма должна быть больше нуля")

    # Округляем до копеек и умножаем на 100, чтобы получить целое число.
    value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(value * 100)


def format_money(kopecks):
    """Переводит копейки в строку для вывода: 125050 -> '1 250,50 ₽'."""
    sign = "-" if kopecks < 0 else ""
    rubles, kop = divmod(abs(kopecks), 100)
    # Формат {:,} ставит запятые между тысячами, заменяем их на пробелы.
    rubles_text = "{:,}".format(rubles).replace(",", " ")
    return "{}{},{:02d} ₽".format(sign, rubles_text, kop)


def check_date(text):
    """Проверяет, что строка является датой в формате ГГГГ-ММ-ДД, и возвращает её."""
    try:
        date.fromisoformat(text)
    except ValueError:
        raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД, например 2026-10-17")
    return text


def current_month():
    """Возвращает текущий месяц в виде строки ГГГГ-ММ, например '2026-10'."""
    return date.today().isoformat()[:7]


# ---------------------------------------------------------------------------
# Счета и категории
# ---------------------------------------------------------------------------

def create_account(conn, name, balance_kopecks=0):
    """Создаёт счёт с начальным остатком и возвращает его номер."""
    name = name.strip()
    if name == "":
        raise ValueError("Название счёта не может быть пустым")
    if balance_kopecks < 0:
        raise ValueError("Начальный остаток не может быть отрицательным")

    cursor = conn.execute(
        "INSERT INTO accounts (name, balance) VALUES (?, ?)",
        (name, balance_kopecks),
    )
    conn.commit()
    return cursor.lastrowid


def list_accounts(conn):
    """Возвращает все счета, отсортированные по номеру."""
    return conn.execute(
        "SELECT id_account, name, balance FROM accounts ORDER BY id_account"
    ).fetchall()


def get_balance(conn, id_account):
    """Возвращает остаток на счёте в копейках."""
    row = conn.execute(
        "SELECT balance FROM accounts WHERE id_account = ?", (id_account,)
    ).fetchone()
    if row is None:
        raise ValueError("Счёт с номером {} не найден".format(id_account))
    return row["balance"]


def get_total_balance(conn):
    """Возвращает суммарный остаток по всем счетам в копейках."""
    row = conn.execute("SELECT COALESCE(SUM(balance), 0) AS total FROM accounts").fetchone()
    return row["total"]


def list_categories(conn, kind=None):
    """Возвращает категории. Если указан kind, то только категории этого типа."""
    if kind is None:
        return conn.execute(
            "SELECT id_category, name, kind FROM categories ORDER BY id_category"
        ).fetchall()
    return conn.execute(
        "SELECT id_category, name, kind FROM categories WHERE kind = ? ORDER BY id_category",
        (kind,),
    ).fetchall()


# ---------------------------------------------------------------------------
# Операции (транзакции)
# ---------------------------------------------------------------------------

def add_transaction(conn, id_account, id_category, amount_kopecks, kind,
                    trans_date, comment=""):
    """
    Добавляет доход или расход и сразу меняет остаток на счёте.

    Это сценарий «Добавить транзакцию» из диаграммы последовательности
    лабораторной работы 3: сначала проверка данных, затем сохранение.
    Возвращает номер новой операции.
    """
    # --- Шаг 1. Проверка входных данных ---
    if kind != KIND_INCOME and kind != KIND_EXPENSE:
        raise ValueError("Тип операции должен быть income или expense")
    if amount_kopecks <= 0:
        raise ValueError("Сумма должна быть больше нуля")
    check_date(trans_date)

    category = conn.execute(
        "SELECT kind FROM categories WHERE id_category = ?", (id_category,)
    ).fetchone()
    if category is None:
        raise ValueError("Категория с номером {} не найдена".format(id_category))
    if category["kind"] != kind:
        raise ValueError("Тип категории не совпадает с типом операции")

    balance = get_balance(conn, id_account)
    if kind == KIND_EXPENSE and balance < amount_kopecks:
        raise InsufficientFundsError(
            "Недостаточно средств: на счёте {}, а расход {}".format(
                format_money(balance), format_money(amount_kopecks)
            )
        )

    # --- Шаг 2. Сохранение ---
    # Новый остаток: доход увеличивает счёт, расход уменьшает.
    if kind == KIND_INCOME:
        new_balance = balance + amount_kopecks
    else:
        new_balance = balance - amount_kopecks

    # Конструкция "with conn" выполняет обе команды как одну транзакцию БД:
    # если вторая команда упадёт, первая тоже будет отменена.
    with conn:
        cursor = conn.execute(
            "INSERT INTO transactions "
            "(id_account, id_category, amount, kind, trans_date, comment) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (id_account, id_category, amount_kopecks, kind, trans_date, comment.strip()),
        )
        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id_account = ?",
            (new_balance, id_account),
        )
    return cursor.lastrowid


def list_transactions(conn, limit=20, month=None):
    """
    Возвращает последние операции вместе с названиями счёта и категории.

    limit: сколько операций вернуть.
    month: если указан (ГГГГ-ММ), то только операции этого месяца.
    """
    sql = (
        "SELECT t.id_transaction, t.trans_date, t.kind, t.amount, t.comment, "
        "       a.name AS account_name, c.name AS category_name "
        "FROM transactions t "
        "JOIN accounts a   ON a.id_account = t.id_account "
        "JOIN categories c ON c.id_category = t.id_category "
    )
    params = []
    if month is not None:
        sql += "WHERE substr(t.trans_date, 1, 7) = ? "
        params.append(month)
    sql += "ORDER BY t.trans_date DESC, t.id_transaction DESC LIMIT ?"
    params.append(limit)
    return conn.execute(sql, params).fetchall()


def delete_transaction(conn, id_transaction):
    """Удаляет операцию и возвращает остаток счёта к значению до неё."""
    row = conn.execute(
        "SELECT id_account, kind, amount FROM transactions WHERE id_transaction = ?",
        (id_transaction,),
    ).fetchone()
    if row is None:
        raise ValueError("Операция с номером {} не найдена".format(id_transaction))

    balance = get_balance(conn, row["id_account"])

    # Удаление дохода уменьшает остаток, удаление расхода возвращает деньги на счёт.
    if row["kind"] == KIND_INCOME:
        new_balance = balance - row["amount"]
    else:
        new_balance = balance + row["amount"]

    if new_balance < 0:
        raise InsufficientFundsError(
            "Нельзя удалить доход: часть этих денег уже потрачена"
        )

    with conn:
        conn.execute("DELETE FROM transactions WHERE id_transaction = ?", (id_transaction,))
        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id_account = ?",
            (new_balance, row["id_account"]),
        )


# ---------------------------------------------------------------------------
# Бюджетные планы
# ---------------------------------------------------------------------------

def set_budget(conn, id_category, month, limit_kopecks):
    """
    Задаёт лимит расходов на категорию в месяце.
    Если лимит уже был, он заменяется новым.
    """
    if limit_kopecks <= 0:
        raise ValueError("Лимит должен быть больше нуля")

    category = conn.execute(
        "SELECT kind FROM categories WHERE id_category = ?", (id_category,)
    ).fetchone()
    if category is None:
        raise ValueError("Категория с номером {} не найдена".format(id_category))
    if category["kind"] != KIND_EXPENSE:
        raise ValueError("Лимит можно задать только для категории расходов")

    # ON CONFLICT ... DO UPDATE: если запись для пары «категория + месяц»
    # уже есть, обновляем лимит вместо добавления дубликата.
    conn.execute(
        "INSERT INTO budget_plans (id_category, month, limit_amount) VALUES (?, ?, ?) "
        "ON CONFLICT (id_category, month) DO UPDATE SET limit_amount = excluded.limit_amount",
        (id_category, month, limit_kopecks),
    )
    conn.commit()


def check_budget(conn, id_category, month):
    """
    Сравнивает расходы категории за месяц с лимитом.

    Возвращает словарь с ключами limit, spent, remaining, percent, exceeded.
    Если для категории нет плана на этот месяц, возвращает None.
    """
    plan = conn.execute(
        "SELECT limit_amount FROM budget_plans WHERE id_category = ? AND month = ?",
        (id_category, month),
    ).fetchone()
    if plan is None:
        return None

    spent_row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS spent FROM transactions "
        "WHERE id_category = ? AND kind = 'expense' AND substr(trans_date, 1, 7) = ?",
        (id_category, month),
    ).fetchone()

    limit = plan["limit_amount"]
    spent = spent_row["spent"]
    return {
        "limit": limit,
        "spent": spent,
        "remaining": limit - spent,
        "percent": int(spent * 100 / limit),
        "exceeded": spent > limit,
    }


def list_budgets(conn, month):
    """Возвращает список планов месяца вместе с фактическими расходами."""
    rows = conn.execute(
        "SELECT b.id_category, c.name AS category_name "
        "FROM budget_plans b JOIN categories c ON c.id_category = b.id_category "
        "WHERE b.month = ? ORDER BY c.id_category",
        (month,),
    ).fetchall()

    result = []
    for row in rows:
        info = check_budget(conn, row["id_category"], month)
        info["category_name"] = row["category_name"]
        result.append(info)
    return result


# ---------------------------------------------------------------------------
# Цели накопления
# ---------------------------------------------------------------------------

def create_goal(conn, name, target_kopecks):
    """Создаёт цель со статусом «Активна» и возвращает её номер."""
    name = name.strip()
    if name == "":
        raise ValueError("Название цели не может быть пустым")
    if target_kopecks <= 0:
        raise ValueError("Целевая сумма должна быть больше нуля")

    cursor = conn.execute(
        "INSERT INTO financial_goals (name, target_amount) VALUES (?, ?)",
        (name, target_kopecks),
    )
    conn.commit()
    return cursor.lastrowid


def get_goal(conn, id_goal):
    """Возвращает строку цели или вызывает ValueError, если цели нет."""
    row = conn.execute(
        "SELECT id_goal, name, target_amount, current_amount, status "
        "FROM financial_goals WHERE id_goal = ?",
        (id_goal,),
    ).fetchone()
    if row is None:
        raise ValueError("Цель с номером {} не найдена".format(id_goal))
    return row


def list_goals(conn):
    """Возвращает все цели, отсортированные по номеру."""
    return conn.execute(
        "SELECT id_goal, name, target_amount, current_amount, status "
        "FROM financial_goals ORDER BY id_goal"
    ).fetchall()


def add_to_goal(conn, id_goal, amount_kopecks):
    """
    Пополняет цель и возвращает её новый статус.

    Правила перехода состояний:
        Активна -> Активна     пока накоплено меньше цели;
        Активна -> Завершена   когда накоплено столько же или больше.
    Пополнять можно только активную цель.
    """
    if amount_kopecks <= 0:
        raise ValueError("Сумма пополнения должна быть больше нуля")

    goal = get_goal(conn, id_goal)
    if goal["status"] != STATUS_ACTIVE:
        raise ValueError("Пополнять можно только активную цель")

    new_current = goal["current_amount"] + amount_kopecks

    if new_current >= goal["target_amount"]:
        new_status = STATUS_DONE
    else:
        new_status = STATUS_ACTIVE

    conn.execute(
        "UPDATE financial_goals SET current_amount = ?, status = ? WHERE id_goal = ?",
        (new_current, new_status, id_goal),
    )
    conn.commit()
    return new_status


def cancel_goal(conn, id_goal):
    """Переводит активную цель в статус «Отменена»."""
    goal = get_goal(conn, id_goal)
    if goal["status"] != STATUS_ACTIVE:
        raise ValueError("Отменить можно только активную цель")

    conn.execute(
        "UPDATE financial_goals SET status = ? WHERE id_goal = ?",
        (STATUS_CANCELLED, id_goal),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Аналитика
# ---------------------------------------------------------------------------

def month_summary(conn, month):
    """Возвращает кортеж (доходы, расходы) за месяц в копейках."""
    row = conn.execute(
        "SELECT "
        "  COALESCE(SUM(CASE WHEN kind = 'income'  THEN amount END), 0) AS income, "
        "  COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount END), 0) AS expense "
        "FROM transactions WHERE substr(trans_date, 1, 7) = ?",
        (month,),
    ).fetchone()
    return row["income"], row["expense"]


def expenses_by_category(conn, month):
    """Возвращает расходы месяца по категориям, от больших к меньшим."""
    rows = conn.execute(
        "SELECT c.name AS category_name, SUM(t.amount) AS total "
        "FROM transactions t JOIN categories c ON c.id_category = t.id_category "
        "WHERE t.kind = 'expense' AND substr(t.trans_date, 1, 7) = ? "
        "GROUP BY c.id_category ORDER BY total DESC",
        (month,),
    ).fetchall()
    return [(row["category_name"], row["total"]) for row in rows]


# ---------------------------------------------------------------------------
# Демонстрационные данные
# ---------------------------------------------------------------------------

def shift_month(today, back):
    """Возвращает (год, месяц) на back месяцев раньше даты today."""
    index = today.year * 12 + (today.month - 1) - back
    return index // 12, index % 12 + 1


# Шаблон одного месяца: (день, категория, тип, базовая сумма в рублях, комментарий, счёт).
DEMO_MONTH_TEMPLATE = [
    (3, "Жильё", KIND_EXPENSE, 28000, "Аренда квартиры", "Карта Сбербанк"),
    (4, "Продукты", KIND_EXPENSE, 3400, "Пятёрочка", "Карта Сбербанк"),
    (5, "Зарплата", KIND_INCOME, 85000, "Зарплата за месяц", "Карта Сбербанк"),
    (6, "Транспорт", KIND_EXPENSE, 2100, "Проездной на месяц", "Карта Сбербанк"),
    (8, "Продукты", KIND_EXPENSE, 4200, "Супермаркет", "Карта Сбербанк"),
    (9, "Развлечения", KIND_EXPENSE, 2800, "Кинотеатр", "Т-Банк накопительный"),
    (11, "Здоровье", KIND_EXPENSE, 1900, "Аптека", "Наличные"),
    (12, "Подработка", KIND_INCOME, 12000, "Оплата заказа", "Т-Банк накопительный"),
    (14, "Продукты", KIND_EXPENSE, 3900, "Рынок", "Наличные"),
    (16, "Одежда", KIND_EXPENSE, 5400, "Зимняя куртка", "Карта Сбербанк"),
]

# Множители расходов по месяцам, от самого старого к текущему.
# Благодаря им столбцы на диаграмме «Доходы и расходы» получаются разной высоты.
DEMO_FACTORS = [0.94, 1.02, 0.97, 1.09, 1.00, 1.06]


def seed_demo(conn, today=None):
    """
    Заполняет пустую базу демонстрационными данными за шесть месяцев.

    Данные совпадают с макетами интерфейса из лабораторной работы 4,
    поэтому экран программы можно сравнить с макетом Figma.
    today: дата, от которой считаются месяцы (по умолчанию сегодняшняя).
    """
    if today is None:
        today = date.today()

    # Если счета уже есть, данные не трогаем, чтобы не задвоить записи.
    if len(list_accounts(conn)) > 0:
        raise ValueError("База уже содержит данные, демонстрационные данные не добавлены")

    # Начальные остатки подобраны так, чтобы счета не уходили в минус.
    account_ids = {
        "Карта Сбербанк": create_account(conn, "Карта Сбербанк", 5000000),
        "Т-Банк накопительный": create_account(conn, "Т-Банк накопительный", 12000000),
        "Наличные": create_account(conn, "Наличные", 4500000),
    }

    # Словарь «название категории -> номер», чтобы не искать её в базе каждый раз.
    category_ids = {}
    for category in list_categories(conn):
        category_ids[category["name"]] = category["id_category"]

    # Проходим месяцы от самого старого (5 месяцев назад) до текущего (0).
    for position in range(6):
        back = 5 - position
        year, month = shift_month(today, back)
        factor = DEMO_FACTORS[position]

        for day, category, kind, base, comment, account in DEMO_MONTH_TEMPLATE:
            # В текущем месяце не создаём операции «из будущего».
            if back == 0 and day > today.day:
                continue
            # Подработка бывает не каждый месяц: только при чётном back.
            if category == "Подработка" and back % 2 == 1:
                continue

            # Аренда и зарплата не меняются, остальные расходы умножаем на множитель.
            if category == "Жильё" or kind == KIND_INCOME:
                rubles = base
            else:
                # Округляем до десятков рублей: 3400 * 1.06 = 3604 -> 3600.
                rubles = int(round(base * factor / 10.0)) * 10

            add_transaction(
                conn,
                account_ids[account],
                category_ids[category],
                rubles * 100,
                kind,
                "{:04d}-{:02d}-{:02d}".format(year, month, day),
                comment,
            )

    # Бюджетные планы на текущий месяц.
    this_month = "{:04d}-{:02d}".format(today.year, today.month)
    set_budget(conn, category_ids["Продукты"], this_month, 1500000)
    set_budget(conn, category_ids["Транспорт"], this_month, 200000)
    set_budget(conn, category_ids["Развлечения"], this_month, 350000)

    # Цели накопления. Вторая цель сразу достигает значения 90 000 и получает статус «Завершена».
    first = create_goal(conn, "Отпуск на Байкале", 12000000)
    add_to_goal(conn, first, 7800000)
    second = create_goal(conn, "Новый ноутбук", 9000000)
    add_to_goal(conn, second, 9000000)
    third = create_goal(conn, "Резервный фонд", 30000000)
    add_to_goal(conn, third, 12450000)

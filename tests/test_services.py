"""
Автоматические тесты FinSafe.

Запуск вручную из корня проекта:  pytest -v
GitHub Actions запускает эти же тесты при каждой отправке изменений (push).

Каждый тест работает с чистой базой в оперативной памяти (":memory:"),
поэтому тесты не портят настоящую базу и не зависят друг от друга.
"""

import pytest

from finsafe import db, services


@pytest.fixture
def conn():
    """Создаёт пустую базу со справочником категорий и закрывает её после теста."""
    connection = db.connect(":memory:")
    db.init_db(connection)
    yield connection
    connection.close()


def test_expense_reduces_balance(conn):
    """
    Тест 1. Расход уменьшает остаток счёта на свою сумму.

    Счёт: 10 000,00 ₽. Расход на продукты: 2 500,50 ₽.
    Ожидаемый остаток: 7 499,50 ₽, то есть 749 950 копеек.
    """
    # Начальный остаток передаём в копейках: 10 000 рублей = 1 000 000 копеек.
    id_account = services.create_account(conn, "Карта", 1000000)

    # Берём первую категорию расходов из справочника (это «Продукты»).
    id_category = services.list_categories(conn, services.KIND_EXPENSE)[0][
        "id_category"
    ]

    services.add_transaction(
        conn,
        id_account,
        id_category,
        services.to_kopecks("2 500,50"),
        services.KIND_EXPENSE,
        "2026-10-17",
        "Пятёрочка",
    )

    assert services.get_balance(conn, id_account) == 749950


def test_goal_becomes_completed_when_target_reached(conn):
    """
    Тест 2. Цель накопления меняет статус по диаграмме состояний.

    Цель: 5 000 ₽. После взноса 3 000 ₽ цель остаётся активной,
    после второго взноса 2 000 ₽ накоплено 5 000 ₽ и цель становится завершённой.
    """
    id_goal = services.create_goal(conn, "Отпуск", services.to_kopecks("5000"))

    first_status = services.add_to_goal(conn, id_goal, services.to_kopecks("3000"))
    assert first_status == services.STATUS_ACTIVE

    second_status = services.add_to_goal(conn, id_goal, services.to_kopecks("2000"))
    assert second_status == services.STATUS_DONE

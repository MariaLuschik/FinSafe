-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1
-- Время создания: Сен 26 2026 г., 01:04
-- Версия сервера: 10.4.32-MariaDB
-- Версия PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `finsafe_db`
--

-- --------------------------------------------------------

--
-- Структура таблицы `accounts`
--

CREATE TABLE `accounts` (
  `id_account` int(50) NOT NULL,
  `id_user` int(50) NOT NULL,
  `id_bank` int(10) NOT NULL,
  `account_type` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `accounts`
--

INSERT INTO `accounts` (`id_account`, `id_user`, `id_bank`, `account_type`) VALUES
(1, 1, 1, 'Дебетовый счет'),
(2, 2, 2, 'Кредитный счет'),
(3, 3, 3, 'Накопительный счет'),
(4, 4, 4, 'Зарплатный счет'),
(5, 5, 5, 'Сберегательный счет'),
(6, 6, 6, 'Валютный счет'),
(7, 7, 7, 'Инвестиционный счет'),
(8, 8, 8, 'Расчетный счет'),
(9, 9, 9, 'Мультивалютный счет'),
(10, 10, 10, 'Пенсионный счет');

-- --------------------------------------------------------

--
-- Структура таблицы `audit_log`
--

CREATE TABLE `audit_log` (
  `id` int(11) NOT NULL COMMENT 'Уникальный идентификатор записи аудита',
  `user_name` varchar(50) NOT NULL COMMENT 'Имя пользователя MySQL, выполнившего операцию',
  `operation_type` varchar(10) NOT NULL COMMENT 'Тип операции',
  `table_name` varchar(50) NOT NULL COMMENT 'Имя таблицы, в которой произошло изменение',
  `record_id` int(11) DEFAULT NULL COMMENT 'Идентификатор изменённой записи',
  `action_time` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Время выполнения операции',
  `description` text DEFAULT NULL COMMENT 'Описание изменений'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `audit_log`
--

INSERT INTO `audit_log` (`id`, `user_name`, `operation_type`, `table_name`, `record_id`, `action_time`, `description`) VALUES
(1, 'root@localhost', 'INSERT', 'transactions', 11, '2026-03-29 15:19:13', 'Добавлена транзакция: сумма=5000.00, дата=2025-03-29, счет=1, категория=1'),
(2, 'root@localhost', 'UPDATE', 'transactions', 1, '2026-03-29 15:24:47', 'Изменена транзакция. Было: сумма=85000.00, дата=2025-02-01. Стало: сумма=6000.00, дата=2025-03-28'),
(3, 'root@localhost', 'DELETE', 'transactions', 1, '2026-03-29 15:44:38', 'Удалена транзакция: сумма=6000.00, дата=2025-03-28, счет=4, категория=1');

-- --------------------------------------------------------

--
-- Структура таблицы `banks`
--

CREATE TABLE `banks` (
  `id_bank` int(10) NOT NULL,
  `bank_name` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `banks`
--

INSERT INTO `banks` (`id_bank`, `bank_name`) VALUES
(1, 'Sberbank'),
(2, 'Tinkoff'),
(3, 'Alfa Bank'),
(4, 'VTB'),
(5, 'Optima'),
(6, 'DemirBank'),
(7, 'KICB'),
(8, 'Kompanion'),
(9, 'RSK Bank'),
(10, 'Aiyl Bank');

-- --------------------------------------------------------

--
-- Структура таблицы `budget_plans`
--

CREATE TABLE `budget_plans` (
  `id_plan` int(11) NOT NULL COMMENT 'Уникальный идентификатор плана',
  `id_user` int(11) NOT NULL COMMENT 'Ссылка на пользователя (FK)',
  `plan_name` varchar(50) NOT NULL COMMENT 'Название бюджетного плана',
  `start_date` date NOT NULL COMMENT 'Дата начала периода',
  `end_date` date NOT NULL COMMENT 'Дата окончания периода',
  `planned_amount` decimal(10,2) NOT NULL COMMENT 'Плановая сумма',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Дата создания'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `budget_plans`
--

INSERT INTO `budget_plans` (`id_plan`, `id_user`, `plan_name`, `start_date`, `end_date`, `planned_amount`, `created_at`) VALUES
(1, 1, 'Ежемесячный бюджет', '2025-03-01', '2025-03-31', 50000.00, '2026-03-23 04:39:32'),
(2, 1, 'Отпускной фонд', '2025-04-01', '2025-06-30', 120000.00, '2026-03-23 04:39:32'),
(3, 2, 'Бюджет на продукты', '2025-03-01', '2025-03-31', 15000.00, '2026-03-23 04:39:32'),
(4, 2, 'Накопление на авто', '2025-01-01', '2025-12-31', 300000.00, '2026-03-23 04:39:32'),
(5, 3, 'Студенческий бюджет', '2025-03-01', '2025-03-31', 20000.00, '2026-03-23 04:39:32'),
(6, 4, 'Семейный план', '2025-03-01', '2025-03-31', 80000.00, '2026-03-23 04:39:32'),
(7, 5, 'Инвестиционный план', '2025-02-01', '2025-08-31', 200000.00, '2026-03-23 04:39:32'),
(8, 1, 'Ремонт квартиры', '2025-05-01', '2025-09-30', 250000.00, '2026-03-23 04:39:32'),
(9, 3, 'Подготовка к экзаменам', '2025-04-01', '2025-06-30', 10000.00, '2026-03-23 04:39:32'),
(10, 4, 'Путешествие в Европу', '2025-06-01', '2025-08-31', 150000.00, '2026-03-23 04:39:32');

-- --------------------------------------------------------

--
-- Структура таблицы `categories`
--

CREATE TABLE `categories` (
  `id_category` int(20) NOT NULL,
  `category_name` varchar(20) NOT NULL,
  `category_type` enum('income','expense') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `categories`
--

INSERT INTO `categories` (`id_category`, `category_name`, `category_type`) VALUES
(1, 'Зарплата', 'income'),
(2, 'Стипендия', 'income'),
(3, 'Еда', 'expense'),
(4, 'Транспорт', 'expense'),
(5, 'Развлечение ', 'expense'),
(6, 'Интернет', 'expense'),
(7, 'Одежда', 'expense'),
(8, 'Спортзал', 'expense'),
(9, 'Медицина', 'expense'),
(10, 'Связь', 'expense');

-- --------------------------------------------------------

--
-- Структура таблицы `financial_goals`
--

CREATE TABLE `financial_goals` (
  `id_goal` int(11) NOT NULL COMMENT 'Уникальный идентификатор цели',
  `id_user` int(11) NOT NULL COMMENT 'Ссылка на пользователя (FK)',
  `goal_name` varchar(100) NOT NULL COMMENT 'Название цели',
  `target_amount` decimal(10,2) NOT NULL COMMENT 'Целевая сумма',
  `current_amount` decimal(10,2) DEFAULT 0.00 COMMENT 'Текущая накопленная сумма',
  `deadline` date NOT NULL COMMENT 'Срок достижения цели',
  `goal_type` enum('Накопления','Покупка','Долг','Другое') NOT NULL DEFAULT 'Накопления' COMMENT 'Тип финансовой цели',
  `status` enum('Активна','Завершена','Отменена') NOT NULL DEFAULT 'Активна' COMMENT 'Статус цели',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Дата создания '
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `financial_goals`
--

INSERT INTO `financial_goals` (`id_goal`, `id_user`, `goal_name`, `target_amount`, `current_amount`, `deadline`, `goal_type`, `status`, `created_at`) VALUES
(1, 1, 'Накопить на ноутбук', 80000.00, 35000.00, '2025-06-01', 'Покупка', 'Активна', '2026-03-23 04:39:32'),
(2, 1, 'Подушка безопасности', 100000.00, 75000.00, '2025-12-31', 'Накопления', 'Активна', '2026-03-23 04:39:32'),
(3, 2, 'Первый взнос за квартиру', 500000.00, 120000.00, '2026-01-01', 'Покупка', 'Активна', '2026-03-23 04:39:32'),
(4, 2, 'Погасить кредит', 50000.00, 48000.00, '2025-04-30', 'Долг', 'Активна', '2026-03-23 04:39:32'),
(5, 3, 'Новый телефон', 40000.00, 15000.00, '2025-05-15', 'Покупка', 'Активна', '2026-03-23 04:39:32'),
(6, 4, 'Образование детей', 300000.00, 50000.00, '2027-09-01', 'Накопления', 'Активна', '2026-03-23 04:39:32'),
(7, 5, 'Стартап-фонд', 500000.00, 200000.00, '2026-06-30', 'Другое', 'Активна', '2026-03-23 04:39:32'),
(8, 1, 'Отпуск на море', 60000.00, 60000.00, '2025-07-01', 'Покупка', 'Завершена', '2026-03-23 04:39:32'),
(9, 3, 'Курсы программирования', 25000.00, 10000.00, '2025-08-01', 'Другое', 'Активна', '2026-03-23 04:39:32'),
(10, 4, 'Ремонт автомобиля', 70000.00, 20000.00, '2025-10-01', 'Покупка', 'Активна', '2026-03-23 04:39:32');

-- --------------------------------------------------------

--
-- Структура таблицы `transactions`
--

CREATE TABLE `transactions` (
  `id_transaction` int(11) NOT NULL,
  `transaction_date` date NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `id_account` int(11) NOT NULL,
  `id_category` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `transactions`
--

INSERT INTO `transactions` (`id_transaction`, `transaction_date`, `amount`, `id_account`, `id_category`) VALUES
(2, '2025-02-02', 1200.00, 1, 3),
(3, '2025-02-03', 3500.00, 2, 4),
(4, '2025-05-02', 15000.00, 5, 5),
(5, '2025-02-07', 2500.00, 6, 6),
(6, '2025-10-02', 4000.00, 3, 7),
(7, '2025-12-02', 20000.00, 7, 4),
(8, '2025-12-02', 18000.00, 10, 2),
(9, '2025-11-02', 75000.00, 8, 9),
(10, '2025-02-20', 3200.00, 9, 7),
(11, '2025-03-29', 5000.00, 1, 1);

--
-- Триггеры `transactions`
--
DELIMITER $$
CREATE TRIGGER `trg_transactions_delete` AFTER DELETE ON `transactions` FOR EACH ROW INSERT INTO `audit_log` (`user_name`, `operation_type`, `table_name`, `record_id`, `description`)
VALUES (
    USER(), 
    'DELETE', 
    'transactions', 
    OLD.id_transaction, 
    CONCAT('Удалена транзакция: сумма=', OLD.amount, ', дата=', OLD.transaction_date, ', счет=', OLD.id_account, ', категория=', OLD.id_category)
)
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_transactions_insert` AFTER INSERT ON `transactions` FOR EACH ROW INSERT INTO `audit_log` (`user_name`, `operation_type`, `table_name`, `record_id`, `description`)
VALUES (
    USER(), 
    'INSERT', 
    'transactions', 
    NEW.id_transaction, 
    CONCAT('Добавлена транзакция: сумма=', NEW.amount, ', дата=', NEW.transaction_date, ', счет=', NEW.id_account, ', категория=', NEW.id_category)
)
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_transactions_update` AFTER UPDATE ON `transactions` FOR EACH ROW INSERT INTO `audit_log` (`user_name`, `operation_type`, `table_name`, `record_id`, `description`)
VALUES (
    USER(), 
    'UPDATE', 
    'transactions', 
    NEW.id_transaction, 
    CONCAT('Изменена транзакция. Было: сумма=', OLD.amount, ', дата=', OLD.transaction_date, '. Стало: сумма=', NEW.amount, ', дата=', NEW.transaction_date)
)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `id_user` int(50) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `email` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Дамп данных таблицы `users`
--

INSERT INTO `users` (`id_user`, `last_name`, `first_name`, `email`) VALUES
(1, 'Иванов', 'Иван', 'ivan@mail.ru'),
(2, 'Петров ', 'Петр', 'petr@mail.ru'),
(3, 'Сидоров', 'Алекс', 'alex@mail.ru'),
(4, 'Смирнова ', 'Анна', 'anna@mail.ru'),
(5, 'Ким', 'Алина', 'alina@mail.ru'),
(6, 'Быков', 'Тимур', 'timur@mail.ru'),
(7, 'Орлова', 'Марина', 'marina@mail.ru'),
(8, 'Ли', 'Диана', 'diana@mail.ru'),
(9, 'Носов', 'Артем', 'artem@mail.ru'),
(10, 'Кучеров', 'Рустам', 'rustam@mail.ru');

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id_account`),
  ADD KEY `id_user` (`id_user`),
  ADD KEY `id_bank` (`id_bank`);

--
-- Индексы таблицы `audit_log`
--
ALTER TABLE `audit_log`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `banks`
--
ALTER TABLE `banks`
  ADD PRIMARY KEY (`id_bank`);

--
-- Индексы таблицы `budget_plans`
--
ALTER TABLE `budget_plans`
  ADD PRIMARY KEY (`id_plan`),
  ADD KEY `idx_user` (`id_user`),
  ADD KEY `idx_period` (`start_date`,`end_date`);

--
-- Индексы таблицы `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id_category`);

--
-- Индексы таблицы `financial_goals`
--
ALTER TABLE `financial_goals`
  ADD PRIMARY KEY (`id_goal`),
  ADD KEY `idx_user` (`id_user`),
  ADD KEY `idx_deadline` (`deadline`),
  ADD KEY `idx_status` (`status`);

--
-- Индексы таблицы `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id_transaction`),
  ADD KEY `id_account` (`id_account`),
  ADD KEY `id_category` (`id_category`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `accounts`
--
ALTER TABLE `accounts`
  MODIFY `id_account` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT для таблицы `audit_log`
--
ALTER TABLE `audit_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор записи аудита', AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT для таблицы `banks`
--
ALTER TABLE `banks`
  MODIFY `id_bank` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT для таблицы `budget_plans`
--
ALTER TABLE `budget_plans`
  MODIFY `id_plan` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор плана', AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT для таблицы `categories`
--
ALTER TABLE `categories`
  MODIFY `id_category` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT для таблицы `financial_goals`
--
ALTER TABLE `financial_goals`
  MODIFY `id_goal` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор цели', AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT для таблицы `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id_transaction` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT для таблицы `users`
--
ALTER TABLE `users`
  MODIFY `id_user` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON UPDATE CASCADE,
  ADD CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`id_bank`) REFERENCES `banks` (`id_bank`) ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `budget_plans`
--
ALTER TABLE `budget_plans`
  ADD CONSTRAINT `budget_plans_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `financial_goals`
--
ALTER TABLE `financial_goals`
  ADD CONSTRAINT `financial_goals_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`id_account`) REFERENCES `accounts` (`id_account`) ON UPDATE CASCADE,
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`id_category`) REFERENCES `categories` (`id_category`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

import sqlite3


DATABASE = "finance.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL CHECK(amount > 0)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL CHECK(target_amount > 0),
            saved_amount REAL NOT NULL DEFAULT 0
                CHECK(saved_amount >= 0),
            deadline TEXT,
            description TEXT
        )
    """)

    connection.commit()
    connection.close()


# -------------------------
# Transaction Functions
# -------------------------

def add_transaction(transaction_type, amount, category, description, date):
    connection = get_db_connection()

    connection.execute("""
        INSERT INTO transactions
        (type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_type,
        amount,
        category,
        description,
        date
    ))

    connection.commit()
    connection.close()


def get_all_transactions(
    transaction_type=None,
    category=None,
    search=None,
    start_date=None,
    end_date=None
):
    connection = get_db_connection()

    query = """
        SELECT *
        FROM transactions
        WHERE 1 = 1
    """

    parameters = []

    if transaction_type:
        query += " AND type = ?"
        parameters.append(transaction_type)

    if category:
        query += " AND category = ?"
        parameters.append(category)

    if search:
        query += """
            AND (
                description LIKE ?
                OR category LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.append(search_value)
        parameters.append(search_value)

    if start_date:
        query += " AND date >= ?"
        parameters.append(start_date)

    if end_date:
        query += " AND date <= ?"
        parameters.append(end_date)

    query += " ORDER BY date DESC, id DESC"

    transactions = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return transactions


def get_transaction(transaction_id):
    connection = get_db_connection()

    transaction = connection.execute("""
        SELECT *
        FROM transactions
        WHERE id = ?
    """, (transaction_id,)).fetchone()

    connection.close()

    return transaction


def update_transaction(
    transaction_id,
    transaction_type,
    amount,
    category,
    description,
    date
):
    connection = get_db_connection()

    connection.execute("""
        UPDATE transactions
        SET type = ?,
            amount = ?,
            category = ?,
            description = ?,
            date = ?
        WHERE id = ?
    """, (
        transaction_type,
        amount,
        category,
        description,
        date,
        transaction_id
    ))

    connection.commit()
    connection.close()


def delete_transaction(transaction_id):
    connection = get_db_connection()

    connection.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    connection.commit()
    connection.close()


def get_financial_summary():
    connection = get_db_connection()

    total_income = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'income'
    """).fetchone()[0]

    total_expenses = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'expense'
    """).fetchone()[0]

    transaction_count = connection.execute("""
        SELECT COUNT(*)
        FROM transactions
    """).fetchone()[0]

    connection.close()

    balance = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "transaction_count": transaction_count
    }


# -------------------------
# Budget Functions
# -------------------------

def add_budget(category, amount):
    connection = get_db_connection()

    connection.execute("""
        INSERT INTO budgets (category, amount)
        VALUES (?, ?)
        ON CONFLICT(category)
        DO UPDATE SET amount = excluded.amount
    """, (
        category,
        amount
    ))

    connection.commit()
    connection.close()


def get_all_budgets():
    connection = get_db_connection()

    budgets = connection.execute("""
        SELECT *
        FROM budgets
        ORDER BY category ASC
    """).fetchall()

    connection.close()

    return budgets


def get_budget(budget_id):
    connection = get_db_connection()

    budget = connection.execute("""
        SELECT *
        FROM budgets
        WHERE id = ?
    """, (budget_id,)).fetchone()

    connection.close()

    return budget


def update_budget(budget_id, category, amount):
    connection = get_db_connection()

    connection.execute("""
        UPDATE budgets
        SET category = ?,
            amount = ?
        WHERE id = ?
    """, (
        category,
        amount,
        budget_id
    ))

    connection.commit()
    connection.close()


def delete_budget(budget_id):
    connection = get_db_connection()

    connection.execute("""
        DELETE FROM budgets
        WHERE id = ?
    """, (budget_id,))

    connection.commit()
    connection.close()


def get_budget_data():
    connection = get_db_connection()

    budgets = connection.execute("""
        SELECT *
        FROM budgets
        ORDER BY category ASC
    """).fetchall()

    budget_data = []

    for budget in budgets:

        spent = connection.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE type = 'expense'
            AND category = ?
        """, (budget["category"],)).fetchone()[0]

        remaining = budget["amount"] - spent

        percentage = 0

        if budget["amount"] > 0:
            percentage = (spent / budget["amount"]) * 100

        budget_data.append({
            "id": budget["id"],
            "category": budget["category"],
            "budget": budget["amount"],
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage
        })

    connection.close()

    return budget_data


# -------------------------
# Monthly Analytics
# -------------------------

def get_monthly_analytics(month):
    connection = get_db_connection()

    monthly_income = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'income'
        AND substr(date, 1, 7) = ?
    """, (month,)).fetchone()[0]

    monthly_expenses = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'expense'
        AND substr(date, 1, 7) = ?
    """, (month,)).fetchone()[0]

    transaction_count = connection.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE substr(date, 1, 7) = ?
    """, (month,)).fetchone()[0]

    category_spending = connection.execute("""
        SELECT
            category,
            SUM(amount) AS total
        FROM transactions
        WHERE type = 'expense'
        AND substr(date, 1, 7) = ?
        GROUP BY category
        ORDER BY total DESC
    """, (month,)).fetchall()

    daily_spending = connection.execute("""
        SELECT
            date,
            SUM(amount) AS total
        FROM transactions
        WHERE type = 'expense'
        AND substr(date, 1, 7) = ?
        GROUP BY date
        ORDER BY date ASC
    """, (month,)).fetchall()

    connection.close()

    monthly_savings = monthly_income - monthly_expenses

    if monthly_income > 0:
        savings_rate = (
            monthly_savings / monthly_income
        ) * 100
    else:
        savings_rate = 0

    if category_spending:
        top_category = category_spending[0]["category"]
        top_category_amount = category_spending[0]["total"]
    else:
        top_category = "No spending"
        top_category_amount = 0

    return {
        "month": month,
        "income": monthly_income,
        "expenses": monthly_expenses,
        "savings": monthly_savings,
        "savings_rate": savings_rate,
        "transaction_count": transaction_count,
        "top_category": top_category,
        "top_category_amount": top_category_amount,
        "category_spending": category_spending,
        "daily_spending": daily_spending
    }


# -------------------------
# Goal Functions
# -------------------------

def add_goal(name, target_amount, saved_amount, deadline, description):
    connection = get_db_connection()

    connection.execute("""
        INSERT INTO goals
        (name, target_amount, saved_amount, deadline, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        target_amount,
        saved_amount,
        deadline,
        description
    ))

    connection.commit()
    connection.close()


def get_all_goals():
    connection = get_db_connection()

    goals = connection.execute("""
        SELECT *
        FROM goals
        ORDER BY
            CASE
                WHEN deadline IS NULL OR deadline = '' THEN 1
                ELSE 0
            END,
            deadline ASC,
            id DESC
    """).fetchall()

    connection.close()

    return goals


def get_goal(goal_id):
    connection = get_db_connection()

    goal = connection.execute("""
        SELECT *
        FROM goals
        WHERE id = ?
    """, (goal_id,)).fetchone()

    connection.close()

    return goal


def update_goal(
    goal_id,
    name,
    target_amount,
    saved_amount,
    deadline,
    description
):
    connection = get_db_connection()

    connection.execute("""
        UPDATE goals
        SET name = ?,
            target_amount = ?,
            saved_amount = ?,
            deadline = ?,
            description = ?
        WHERE id = ?
    """, (
        name,
        target_amount,
        saved_amount,
        deadline,
        description,
        goal_id
    ))

    connection.commit()
    connection.close()


def delete_goal(goal_id):
    connection = get_db_connection()

    connection.execute("""
        DELETE FROM goals
        WHERE id = ?
    """, (goal_id,))

    connection.commit()
    connection.close()


def get_goal_data():
    connection = get_db_connection()

    goals = connection.execute("""
        SELECT *
        FROM goals
        ORDER BY id DESC
    """).fetchall()

    goal_data = []

    for goal in goals:

        remaining = goal["target_amount"] - goal["saved_amount"]

        percentage = 0

        if goal["target_amount"] > 0:
            percentage = (
                goal["saved_amount"] /
                goal["target_amount"]
            ) * 100

        percentage = min(percentage, 100)

        goal_data.append({
            "id": goal["id"],
            "name": goal["name"],
            "target_amount": goal["target_amount"],
            "saved_amount": goal["saved_amount"],
            "remaining": remaining,
            "deadline": goal["deadline"],
            "description": goal["description"],
            "percentage": percentage
        })

    connection.close()

    return goal_data

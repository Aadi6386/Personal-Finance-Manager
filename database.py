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

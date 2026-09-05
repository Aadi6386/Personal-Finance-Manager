import os
import sqlite3
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from datetime import date

from database import (
    initialize_database,

    add_transaction,
    get_all_transactions,
    get_transaction,
    update_transaction,
    delete_transaction,
    get_financial_summary,

    add_budget,
    get_all_budgets,
    get_budget,
    update_budget,
    delete_budget,
    get_budget_data,

    get_monthly_analytics,

    add_goal,
    get_all_goals,
    get_goal,
    update_goal,
    delete_goal,
    get_goal_data
)


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-secret-key"
)


initialize_database()


# -------------------------
# Dashboard
# -------------------------

@app.route("/")
def index():

    summary = get_financial_summary()

    recent_transactions = get_all_transactions()[:5]

    return render_template(
        "index.html",
        summary=summary,
        recent_transactions=recent_transactions
    )


# -------------------------
# Transactions
# -------------------------

@app.route("/transactions")
def transactions():

    transaction_type = request.args.get("type")
    category = request.args.get("category")
    search = request.args.get("search")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    transaction_list = get_all_transactions(
        transaction_type=transaction_type,
        category=category,
        search=search,
        start_date=start_date,
        end_date=end_date
    )

    return render_template(
        "transactions.html",
        transactions=transaction_list,
        selected_type=transaction_type,
        selected_category=category,
        search=search,
        start_date=start_date,
        end_date=end_date
    )


@app.route("/transactions/add", methods=["GET", "POST"])
def add_transaction_page():

    if request.method == "POST":

        transaction_type = request.form.get("type")
        amount = request.form.get("amount")
        category = request.form.get("category")
        description = request.form.get("description")
        transaction_date = request.form.get("date")

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            flash("Please enter a valid amount.", "error")
            return render_template(
                "add_transaction.html",
                today=date.today().isoformat()
            )

        if transaction_type not in ["income", "expense"]:
            flash("Please select a valid transaction type.", "error")

            return render_template(
                "add_transaction.html",
                today=date.today().isoformat()
            )

        if amount <= 0:
            flash("Amount must be greater than zero.", "error")

            return render_template(
                "add_transaction.html",
                today=date.today().isoformat()
            )

        if not category:
            flash("Category is required.", "error")

            return render_template(
                "add_transaction.html",
                today=date.today().isoformat()
            )

        if not transaction_date:
            flash("Date is required.", "error")

            return render_template(
                "add_transaction.html",
                today=date.today().isoformat()
            )

        add_transaction(
            transaction_type,
            amount,
            category.strip(),
            description.strip() if description else "",
            transaction_date
        )

        flash("Transaction added successfully.", "success")

        return redirect(url_for("transactions"))

    return render_template(
        "add_transaction.html",
        today=date.today().isoformat()
    )


@app.route(
    "/transactions/edit/<int:transaction_id>",
    methods=["GET", "POST"]
)
def edit_transaction_page(transaction_id):

    transaction = get_transaction(transaction_id)

    if not transaction:
        flash("Transaction not found.", "error")
        return redirect(url_for("transactions"))

    if request.method == "POST":

        transaction_type = request.form.get("type")
        amount = request.form.get("amount")
        category = request.form.get("category")
        description = request.form.get("description")
        transaction_date = request.form.get("date")

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            flash("Please enter a valid amount.", "error")

            return render_template(
                "edit_transaction.html",
                transaction=transaction
            )

        if transaction_type not in ["income", "expense"]:
            flash("Please select a valid transaction type.", "error")

            return render_template(
                "edit_transaction.html",
                transaction=transaction
            )

        if amount <= 0:
            flash("Amount must be greater than zero.", "error")

            return render_template(
                "edit_transaction.html",
                transaction=transaction
            )

        if not category:
            flash("Category is required.", "error")

            return render_template(
                "edit_transaction.html",
                transaction=transaction
            )

        if not transaction_date:
            flash("Date is required.", "error")

            return render_template(
                "edit_transaction.html",
                transaction=transaction
            )

        update_transaction(
            transaction_id,
            transaction_type,
            amount,
            category.strip(),
            description.strip() if description else "",
            transaction_date
        )

        flash("Transaction updated successfully.", "success")

        return redirect(url_for("transactions"))

    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )


@app.route(
    "/transactions/delete/<int:transaction_id>",
    methods=["POST"]
)
def delete_transaction_page(transaction_id):

    transaction = get_transaction(transaction_id)

    if not transaction:
        flash("Transaction not found.", "error")
        return redirect(url_for("transactions"))

    delete_transaction(transaction_id)

    flash("Transaction deleted successfully.", "success")

    return redirect(url_for("transactions"))


# -------------------------
# Budgets
# -------------------------

@app.route("/budgets")
def budgets():

    budget_list = get_all_budgets()

    budget_data = get_budget_data()

    return render_template(
        "budgets.html",
        budgets=budget_list,
        budget_data=budget_data
    )


@app.route("/budgets/add", methods=["GET", "POST"])
def add_budget_page():

    if request.method == "POST":

        category = request.form.get("category")
        amount = request.form.get("amount")

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            flash("Please enter a valid budget amount.", "error")
            return render_template("add_budget.html")

        if not category:
            flash("Category is required.", "error")
            return render_template("add_budget.html")

        if amount <= 0:
            flash("Budget amount must be greater than zero.", "error")
            return render_template("add_budget.html")

        add_budget(
            category.strip(),
            amount
        )

        flash("Budget saved successfully.", "success")

        return redirect(url_for("budgets"))

    return render_template("add_budget.html")


@app.route(
    "/budgets/edit/<int:budget_id>",
    methods=["GET", "POST"]
)
@app.route("/edit-budget/<int:budget_id>", methods=["GET", "POST"])
def edit_budget_page(budget_id):
    budget = get_budget(budget_id)

    if budget is None:
        return "Budget not found.", 404

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        amount = request.form.get("amount", "").strip()

        if not category or not amount:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("edit_budget_page", budget_id=budget_id))

        try:
            amount = float(amount)
        except ValueError:
            flash("Budget amount must be a valid number.", "error")
            return redirect(url_for("edit_budget_page", budget_id=budget_id))

        if amount <= 0:
            flash("Budget amount must be greater than zero.", "error")
            return redirect(url_for("edit_budget_page", budget_id=budget_id))

        try:
            update_budget(budget_id, category, amount)
        except sqlite3.IntegrityError:
            flash("A budget for this category already exists.", "error")
            return redirect(url_for("edit_budget_page", budget_id=budget_id))

        flash("Budget updated successfully.", "success")
        return redirect(url_for("budgets_page"))

    return render_template("edit_budget.html", budget=budget)

@app.route(
    "/budgets/delete/<int:budget_id>",
    methods=["POST"]
)
def delete_budget_page(budget_id):

    budget = get_budget(budget_id)

    if not budget:
        flash("Budget not found.", "error")
        return redirect(url_for("budgets"))

    delete_budget(budget_id)

    flash("Budget deleted successfully.", "success")

    return redirect(url_for("budgets"))


# -------------------------
# Analytics
# -------------------------

@app.route("/analytics")
def analytics():

    selected_month = request.args.get("month")

    if not selected_month:
        selected_month = date.today().strftime("%Y-%m")

    analytics_data = get_monthly_analytics(
        selected_month
    )

    return render_template(
        "analytics.html",
        analytics=analytics_data,
        selected_month=selected_month
    )


# -------------------------
# Goals
# -------------------------

@app.route("/goals")
def goals():

    goal_list = get_all_goals()

    goal_data = get_goal_data()

    return render_template(
        "goals.html",
        goals=goal_list,
        goal_data=goal_data
    )


@app.route("/goals/add", methods=["GET", "POST"])
def add_goal_page():

    if request.method == "POST":

        name = request.form.get("name")
        target_amount = request.form.get("target_amount")
        saved_amount = request.form.get("saved_amount")
        deadline = request.form.get("deadline")
        description = request.form.get("description")

        try:
            target_amount = float(target_amount)

            if saved_amount:
                saved_amount = float(saved_amount)
            else:
                saved_amount = 0

        except (TypeError, ValueError):
            flash("Please enter valid amounts.", "error")
            return render_template("add_goal.html")

        if not name:
            flash("Goal name is required.", "error")
            return render_template("add_goal.html")

        if target_amount <= 0:
            flash(
                "Target amount must be greater than zero.",
                "error"
            )
            return render_template("add_goal.html")

        if saved_amount < 0:
            flash(
                "Saved amount cannot be negative.",
                "error"
            )
            return render_template("add_goal.html")

        if saved_amount > target_amount:
            flash(
                "Saved amount cannot exceed the target amount.",
                "error"
            )
            return render_template("add_goal.html")

        add_goal(
            name.strip(),
            target_amount,
            saved_amount,
            deadline,
            description.strip() if description else ""
        )

        flash("Goal created successfully.", "success")

        return redirect(url_for("goals"))

    return render_template("add_goal.html")


@app.route(
    "/goals/edit/<int:goal_id>",
    methods=["GET", "POST"]
)
def edit_goal_page(goal_id):

    goal = get_goal(goal_id)

    if not goal:
        flash("Goal not found.", "error")
        return redirect(url_for("goals"))

    if request.method == "POST":

        name = request.form.get("name")
        target_amount = request.form.get("target_amount")
        saved_amount = request.form.get("saved_amount")
        deadline = request.form.get("deadline")
        description = request.form.get("description")

        try:
            target_amount = float(target_amount)

            if saved_amount:
                saved_amount = float(saved_amount)
            else:
                saved_amount = 0

        except (TypeError, ValueError):
            flash("Please enter valid amounts.", "error")

            return render_template(
                "edit_goal.html",
                goal=goal
            )

        if not name:
            flash("Goal name is required.", "error")

            return render_template(
                "edit_goal.html",
                goal=goal
            )

        if target_amount <= 0:
            flash(
                "Target amount must be greater than zero.",
                "error"
            )

            return render_template(
                "edit_goal.html",
                goal=goal
            )

        if saved_amount < 0:
            flash(
                "Saved amount cannot be negative.",
                "error"
            )

            return render_template(
                "edit_goal.html",
                goal=goal
            )

        if saved_amount > target_amount:
            flash(
                "Saved amount cannot exceed the target amount.",
                "error"
            )

            return render_template(
                "edit_goal.html",
                goal=goal
            )

        update_goal(
            goal_id,
            name.strip(),
            target_amount,
            saved_amount,
            deadline,
            description.strip() if description else ""
        )

        flash("Goal updated successfully.", "success")

        return redirect(url_for("goals"))

    return render_template(
        "edit_goal.html",
        goal=goal
    )


@app.route(
    "/goals/delete/<int:goal_id>",
    methods=["POST"]
)
def delete_goal_page(goal_id):

    goal = get_goal(goal_id)

    if not goal:
        flash("Goal not found.", "error")
        return redirect(url_for("goals"))

    delete_goal(goal_id)

    flash("Goal deleted successfully.", "success")

    return redirect(url_for("goals"))


# -------------------------
# Run Application
# -------------------------

if __name__ == "__main__":
    app.run()

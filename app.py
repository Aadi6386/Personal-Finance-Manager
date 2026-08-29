from flask import Flask, render_template, request, redirect, url_for, flash
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
    get_monthly_analytics
)


app = Flask(__name__)
app.secret_key = "personal-finance-manager-secret-key"


initialize_database()


# -------------------------
# Dashboard
# -------------------------

@app.route("/")
def index():

    summary = get_financial_summary()
    transactions = get_all_transactions()

    return render_template(
        "index.html",
        summary=summary,
        transactions=transactions
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

        if not transaction_type or not amount or not category or not transaction_date:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("add_transaction_page"))

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except ValueError:
            flash("Amount must be a positive number.", "error")
            return redirect(url_for("add_transaction_page"))

        if transaction_type not in ["income", "expense"]:
            flash("Invalid transaction type.", "error")
            return redirect(url_for("add_transaction_page"))

        add_transaction(
            transaction_type,
            amount,
            category,
            description,
            transaction_date
        )

        flash("Transaction added successfully.", "success")

        return redirect(url_for("transactions"))

    return render_template(
        "add_transaction.html",
        today=date.today().isoformat()
    )


@app.route("/transactions/edit/<int:transaction_id>", methods=["GET", "POST"])
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

        if not transaction_type or not amount or not category or not transaction_date:
            flash("Please fill in all required fields.", "error")
            return redirect(
                url_for(
                    "edit_transaction_page",
                    transaction_id=transaction_id
                )
            )

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except ValueError:
            flash("Amount must be a positive number.", "error")
            return redirect(
                url_for(
                    "edit_transaction_page",
                    transaction_id=transaction_id
                )
            )

        if transaction_type not in ["income", "expense"]:
            flash("Invalid transaction type.", "error")
            return redirect(
                url_for(
                    "edit_transaction_page",
                    transaction_id=transaction_id
                )
            )

        update_transaction(
            transaction_id,
            transaction_type,
            amount,
            category,
            description,
            transaction_date
        )

        flash("Transaction updated successfully.", "success")

        return redirect(url_for("transactions"))

    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )


@app.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
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

    budget_data = get_budget_data()
    budgets_list = get_all_budgets()

    return render_template(
        "budgets.html",
        budgets=budgets_list,
        budget_data=budget_data
    )


@app.route("/budgets/add", methods=["GET", "POST"])
def add_budget_page():

    if request.method == "POST":

        category = request.form.get("category")
        amount = request.form.get("amount")

        if not category or not amount:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("add_budget_page"))

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except ValueError:
            flash("Budget amount must be a positive number.", "error")
            return redirect(url_for("add_budget_page"))

        add_budget(category, amount)

        flash("Budget saved successfully.", "success")

        return redirect(url_for("budgets"))

    return render_template("add_budget.html")


@app.route("/budgets/edit/<int:budget_id>", methods=["GET", "POST"])
def edit_budget_page(budget_id):

    budget = get_budget(budget_id)

    if not budget:
        flash("Budget not found.", "error")
        return redirect(url_for("budgets"))

    if request.method == "POST":

        category = request.form.get("category")
        amount = request.form.get("amount")

        if not category or not amount:
            flash("Please fill in all required fields.", "error")
            return redirect(
                url_for(
                    "edit_budget_page",
                    budget_id=budget_id
                )
            )

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except ValueError:
            flash("Budget amount must be a positive number.", "error")
            return redirect(
                url_for(
                    "edit_budget_page",
                    budget_id=budget_id
                )
            )

        update_budget(
            budget_id,
            category,
            amount
        )

        flash("Budget updated successfully.", "success")

        return redirect(url_for("budgets"))

    return render_template(
        "edit_budget.html",
        budget=budget
    )


@app.route("/budgets/delete/<int:budget_id>", methods=["POST"])
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

    selected_month = request.args.get(
        "month",
        date.today().strftime("%Y-%m")
    )

    analytics_data = get_monthly_analytics(selected_month)

    return render_template(
        "analytics.html",
        analytics=analytics_data,
        selected_month=selected_month
    )


# -------------------------
# Error Handling
# -------------------------

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html",
        summary=get_financial_summary(),
        transactions=get_all_transactions()
    ), 404


# -------------------------
# Run Application
# -------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

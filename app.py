from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  category TEXT,
                  amount REAL,
                  note TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Home page: view all expenses
@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT * FROM expenses ORDER BY date DESC")
    expenses = c.fetchall()
    conn.close()
    total = sum([x[3] for x in expenses]) if expenses else 0
    return render_template('index.html', expenses=expenses, total=total)

# Add expense
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']
        note = request.form['note']

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
                  (date, category, amount, note))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_expense.html')

# Delete expense
@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Summary page
@app.route('/summary')
def summary():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = c.fetchall()
    conn.close()

    # Extract data into separate lists
    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    summary_data = dict(zip(categories, amounts))

    return render_template(
        'summary.html',
        summary_data=summary_data,
        categories=categories,
        amounts=amounts
    )

# Smart Expense Assistant
@app.route('/assistant', methods=['GET', 'POST'])
def assistant():
    response = ""
    if request.method == 'POST':
        query = request.form['query'].lower()

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()

        if "food" in query:
            c.execute("SELECT SUM(amount) FROM expenses WHERE category LIKE '%Food%'")
            total = c.fetchone()[0] or 0
            response = f"You spent ₹{total} on Food."

        elif "travel" in query:
            c.execute("SELECT SUM(amount) FROM expenses WHERE category LIKE '%Travel%'")
            total = c.fetchone()[0] or 0
            response = f"You spent ₹{total} on Travel."

        elif "shopping" in query:
            c.execute("SELECT SUM(amount) FROM expenses WHERE category LIKE '%Shopping%'")
            total = c.fetchone()[0] or 0
            response = f"You spent ₹{total} on Shopping."

        elif "total" in query:
            c.execute("SELECT SUM(amount) FROM expenses")
            total = c.fetchone()[0] or 0
            response = f"Your total spending so far is ₹{total}."

        elif "categories" in query:
            c.execute("SELECT DISTINCT category FROM expenses")
            categories = [row[0] for row in c.fetchall()]
            response = f"Your expense categories are: {', '.join(categories)}."

        else:
            response = "I'm not sure about that. Try asking like 'How much did I spend on food?'"

        conn.close()

    return render_template('assistant.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if request.method == 'POST':
        item = request.form['item']
        amount = float(request.form['amount'])
        client = request.form['client']
        conn = get_db_connection()
        conn.execute('INSERT INTO sales (item, amount, client) VALUES (?, ?, ?)', (item, amount, client))
        conn.commit()
        conn.close()
        return redirect('/add_sale')
    return render_template('add_sale.html')

@app.route('/export_sales')
def export_sales():
    import csv
    from flask import Response
    conn = get_db_connection()
    sales = conn.execute('SELECT * FROM sales').fetchall()
    conn.close()

    def generate():
        yield 'ID,Item,Amount,Client,Date\n'
        for row in sales:
            yield f"{row['id']},{row['item']},{row['amount']},{row['client']},{row['date']}\n"

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=sales.csv"})


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        cost = float(request.form['cost'])
        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (description, cost) VALUES (?, ?)', (description, cost))
        conn.commit()
        conn.close()
        return redirect('/add_expense')
    return render_template('add_expense.html')

@app.route('/summary')
def summary():
    conn = get_db_connection()
    sales = conn.execute('SELECT SUM(amount) as total_sales FROM sales').fetchone()['total_sales'] or 0
    sales = sales*20
    expenses = conn.execute('SELECT SUM(cost) as total_expenses FROM expenses').fetchone()['total_expenses'] or 0
    conn.close()
    profit = (sales or 0) - (expenses or 0)
    return render_template('view_summary.html', sales=sales, expenses=expenses, profit=profit)
    
@app.route('/delete_sales', methods=['POST'])
def delete_sales():
    conn = get_db_connection()
    conn.execute('DELETE FROM sales')
    conn.commit()
    conn.close()
    return redirect('/summary')
@app.route('/delete_expences', methods=['POST'])
def delete_expenses():
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses')
    conn.commit()
    conn.close()
    return redirect('/')
@app.route('/all_sales')
def all_sales():
    conn = get_db_connection()
    sales = conn.execute('SELECT * FROM sales ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('all_sales.html', sales=sales)

@app.route('/all_expenses')
def all_expenses():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('all_expenses.html', expenses=expenses)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's port or default to 5000
    app.run(host='0.0.0.0', port=port)


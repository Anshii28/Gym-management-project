from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('gym.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS trainers (id INTEGER PRIMARY KEY, name TEXT, specialty TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, duration TEXT, description TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, plan TEXT, trainer TEXT)''')

    # Agar trainers kam hai to sahi karo
    count = conn.execute("SELECT COUNT(*) FROM trainers").fetchone()[0]
    if count < 3:
        conn.execute("DELETE FROM trainers")
        conn.execute("INSERT INTO trainers (name, specialty) VALUES ('Rahul', 'Weight Gain'), ('Aman', 'Weight Loss'), ('Neha', 'Yoga & Zumba')")

    # Agar plans galat naam ke hai to sahi karo
    count2 = conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0]
    if count2!= 3:
        conn.execute("DELETE FROM plans")
    # Check karo naam Basic hai ya nahi
    check = conn.execute("SELECT * FROM plans WHERE name='Basic'").fetchone()
    if not check:
        conn.execute("DELETE FROM plans")
        conn.execute("INSERT INTO plans (name, price, duration, description) VALUES ('Basic', 500, '30 Days', 'Basic Access')")
        conn.execute("INSERT INTO plans (name, price, duration, description) VALUES ('Premium', 1000, '90 Days', 'Gym + Cardio')")
        conn.execute("INSERT INTO plans (name, price, duration, description) VALUES ('VIP', 2000, '365 Days', 'All Access + PT')")

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db()
    total_members = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    total_trainers = conn.execute("SELECT COUNT(*) FROM trainers").fetchone()[0]
    total_plans = conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0]
    # Revenue fix
    revenue_data = conn.execute("SELECT COALESCE(SUM(p.price),0) as total FROM members m LEFT JOIN plans p ON m.plan=p.name").fetchone()
    total_revenue = revenue_data['total']
    conn.close()
    return render_template('dashboard.html', total_members=total_members, total_trainers=total_trainers, total_plans=total_plans, total_revenue=total_revenue)

@app.route('/members')
def members_page():
    conn = get_db()
    members = conn.execute("SELECT * FROM members").fetchall()
    trainers = conn.execute("SELECT * FROM trainers").fetchall()
    plans = conn.execute("SELECT * FROM plans").fetchall()
    conn.close()
    return render_template('members.html', members=members, trainers=trainers, plans=plans)

@app.route('/trainers')
def trainers_page():
    conn = get_db()
    trainers = conn.execute("SELECT * FROM trainers").fetchall()
    conn.close()
    return render_template('trainers.html', trainers=trainers)

@app.route('/plans')
def plans_page():
    conn = get_db()
    plans = conn.execute("SELECT * FROM plans").fetchall()
    conn.close()
    return render_template('plans.html', plans=plans)

@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name']
    phone = request.form['phone']
    plan = request.form['plan']
    trainer = request.form['trainer']
    conn = get_db()
    conn.execute("INSERT INTO members (name, phone, plan, trainer) VALUES (?,?,?,?)", (name, phone, plan, trainer))
    conn.commit()
    conn.close()
    return redirect(url_for('members_page'))

@app.route('/delete_member/<int:id>')
def delete_member(id):
    conn = get_db()
    conn.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('members_page'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)             
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import hashlib
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'supersecretkey'

def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                content TEXT,
                status TEXT,
                category TEXT
            )
        ''')


def get_user_id(username):
    with sqlite3.connect('database.db') as conn:
        result = conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
        return result[0] if result else None

init_db()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    
    user_id = get_user_id(session['username'])
    with sqlite3.connect('database.db') as conn:
        tasks = conn.execute('SELECT * FROM tasks WHERE user_id=?', (user_id,)).fetchall()
    return render_template('index.html', tasks=tasks, username=session['username'])

@app.route('/add', methods=['POST'])
def add():
    if 'username' not in session:
        return redirect('/login')
    
    content = request.form['content']
    category = request.form['category']

    if not content.strip():
        return "Empty task not allowed", 400

    # Validate due date (must not be in the past)


    user_id = get_user_id(session['username'])
    with sqlite3.connect('database.db') as conn:
        conn.execute('INSERT INTO tasks (user_id, content, category, status) VALUES (?, ?, ?, ?)', 
                     (user_id, content, category, 'pending'))
    return redirect('/')

@app.route('/done/<int:id>')
def done(id):
    if 'username' not in session:
        return redirect('/login')
    with sqlite3.connect('database.db') as conn:
        conn.execute('UPDATE tasks SET status=? WHERE id=?', ('done', id))
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    if 'username' not in session:
        return redirect('/login')
    with sqlite3.connect('database.db') as conn:
        conn.execute('DELETE FROM tasks WHERE id=?', (id,))
    return redirect('/')

@app.route('/filter', methods=['GET'])
def filter_tasks():
    if 'username' not in session:
        return redirect('/login')

    category = request.args.get('category')

    user_id = get_user_id(session['username'])
    query = 'SELECT * FROM tasks WHERE user_id=?'
    params = [user_id]

    if category:
        query += ' AND category=?'
        params.append(category)
    

    with sqlite3.connect('database.db') as conn:
        tasks = conn.execute(query, params).fetchall()

    return render_template('index.html', tasks=tasks, username=session['username'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        try:
            with sqlite3.connect('database.db') as conn:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Username already exists", 400
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            result = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
            if result:
                session['username'] = username
                return redirect('/')
            else:
                return "Invalid credentials", 401
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

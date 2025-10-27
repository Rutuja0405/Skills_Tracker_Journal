from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this!

# Database helper function
def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect('instance/database.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Home/Landing Page
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get user's goals
    goals_raw = conn.execute(
        'SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    
    # Get total hours for each goal and convert to dict
    goal_stats = []
    for goal in goals_raw:
        total_hours = conn.execute(
            'SELECT SUM(hours_spent) as total FROM logs WHERE goal_id = ?',
            (goal['id'],)
        ).fetchone()
        
        goal_stats.append({
            'id': goal['id'],
            'name': goal['goal_name'],
            'target_date': goal['target_date'],
            'total_hours': total_hours['total'] if total_hours['total'] else 0
        })
    
    conn.close()
    
    return render_template('dashboard.html', goals=goal_stats, username=session['username'])

# Add Goal
@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        goal_name = request.form['goal_name']
        target_date = request.form.get('target_date', None)
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO goals (user_id, goal_name, target_date) VALUES (?, ?, ?)',
            (session['user_id'], goal_name, target_date if target_date else None)
        )
        conn.commit()
        conn.close()
        
        flash('Goal added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_goal.html')

# Edit Goal
@app.route('/edit_goal/<int:goal_id>', methods=['GET', 'POST'])
def edit_goal(goal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        goal_name = request.form['goal_name']
        target_date = request.form.get('target_date', None)
        
        conn.execute(
            'UPDATE goals SET goal_name = ?, target_date = ? WHERE id = ? AND user_id = ?',
            (goal_name, target_date if target_date else None, goal_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    goal = conn.execute(
        'SELECT * FROM goals WHERE id = ? AND user_id = ?',
        (goal_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if not goal:
        flash('Goal not found!', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_goal.html', goal=goal)

# Delete Goal
@app.route('/delete_goal/<int:goal_id>')
def delete_goal(goal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM goals WHERE id = ? AND user_id = ?',
        (goal_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

# Add Log Entry
@app.route('/log_entry/<int:goal_id>', methods=['GET', 'POST'])
def log_entry(goal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        log_date = request.form['date']
        hours_spent = float(request.form['hours_spent'])
        notes = request.form.get('notes', '')
        
        # Validate hours (between 0.1 and 24)
        if hours_spent < 0.1 or hours_spent > 24:
            flash('Hours must be between 0.1 and 24', 'error')
            goal = conn.execute(
                'SELECT * FROM goals WHERE id = ? AND user_id = ?',
                (goal_id, session['user_id'])
            ).fetchone()
            conn.close()
            today = date.today().isoformat()
            return render_template('log_entry.html', goal=goal, today=today)
        
        conn.execute(
            'INSERT INTO logs (goal_id, date, hours_spent, notes) VALUES (?, ?, ?, ?)',
            (goal_id, log_date, hours_spent, notes)
        )
        conn.commit()
        conn.close()
        
        flash('Log entry added successfully!', 'success')
        return redirect(url_for('view_logs', goal_id=goal_id))
    
    goal = conn.execute(
        'SELECT * FROM goals WHERE id = ? AND user_id = ?',
        (goal_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if not goal:
        flash('Goal not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Pass today's date to template
    today = date.today().isoformat()
    return render_template('log_entry.html', goal=goal, today=today)

# View Logs
@app.route('/view_logs/<int:goal_id>')
def view_logs(goal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    goal = conn.execute(
        'SELECT * FROM goals WHERE id = ? AND user_id = ?',
        (goal_id, session['user_id'])
    ).fetchone()
    
    if not goal:
        flash('Goal not found!', 'error')
        return redirect(url_for('dashboard'))
    
    logs_raw = conn.execute(
        'SELECT * FROM logs WHERE goal_id = ? ORDER BY date DESC',
        (goal_id,)
    ).fetchall()
    
    conn.close()
    
    # Convert Row objects to dictionaries for JSON serialization
    logs = []
    for log in logs_raw:
        logs.append({
            'id': log['id'],
            'goal_id': log['goal_id'],
            'date': log['date'],
            'hours_spent': log['hours_spent'],
            'notes': log['notes'] if log['notes'] else '',
            'created_at': log['created_at']
        })
    
    return render_template('view_logs.html', goal=goal, logs=logs)

# API endpoint for chart data
@app.route('/api/weekly_data')
def weekly_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    
    # Get last 7 days of data
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    logs = conn.execute('''
        SELECT logs.date, SUM(logs.hours_spent) as total_hours
        FROM logs
        JOIN goals ON logs.goal_id = goals.id
        WHERE goals.user_id = ? AND logs.date >= ?
        GROUP BY logs.date
        ORDER BY logs.date
    ''', (session['user_id'], seven_days_ago)).fetchall()
    
    conn.close()
    
    # Convert to lists for JSON
    data = {
        'dates': [log['date'] for log in logs],
        'hours': [float(log['total_hours']) for log in logs]
    }
    
    return jsonify(data)

# Delete Log Entry
@app.route('/delete_log/<int:log_id>/<int:goal_id>')
def delete_log(log_id, goal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Verify the log belongs to a goal owned by this user
    log = conn.execute('''
        SELECT logs.* FROM logs
        JOIN goals ON logs.goal_id = goals.id
        WHERE logs.id = ? AND goals.user_id = ?
    ''', (log_id, session['user_id'])).fetchone()
    
    if log:
        conn.execute('DELETE FROM logs WHERE id = ?', (log_id,))
        conn.commit()
        flash('Log entry deleted successfully!', 'success')
    else:
        flash('Log entry not found!', 'error')
    
    conn.close()
    return redirect(url_for('view_logs', goal_id=goal_id))

# Edit Log Entry
@app.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
def edit_log(log_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get the log entry
    log = conn.execute('''
        SELECT logs.*, goals.id as goal_id, goals.goal_name
        FROM logs
        JOIN goals ON logs.goal_id = goals.id
        WHERE logs.id = ? AND goals.user_id = ?
    ''', (log_id, session['user_id'])).fetchone()
    
    if not log:
        flash('Log entry not found!', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        log_date = request.form['date']
        hours_spent = float(request.form['hours_spent'])
        notes = request.form.get('notes', '')
        
        # Validate hours
        if hours_spent < 0.1 or hours_spent > 24:
            flash('Hours must be between 0.1 and 24', 'error')
            conn.close()
            today = date.today().isoformat()
            return render_template('edit_log.html', log=log, today=today)
        
        conn.execute(
            'UPDATE logs SET date = ?, hours_spent = ?, notes = ? WHERE id = ?',
            (log_date, hours_spent, notes, log_id)
        )
        conn.commit()
        conn.close()
        
        flash('Log entry updated successfully!', 'success')
        return redirect(url_for('view_logs', goal_id=log['goal_id']))
    
    conn.close()
    today = date.today().isoformat()
    return render_template('edit_log.html', log=log, today=today)

if __name__ == '__main__':
    app.run(debug=True)
import sqlite3
import os

def init_database():
    """Initialize the SQLite database with required tables"""
    
    # Create instance folder if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Enable foreign key support
    cursor.execute('PRAGMA foreign_keys = ON;')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_name TEXT NOT NULL,
            target_date DATE,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            date DATE NOT NULL,
            hours_spent REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
        )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    print("📁 Location: instance/database.db")
    print("\nTables created:")
    print("  - users")
    print("  - goals")
    print("  - logs")

if __name__ == '__main__':
    init_database()
"""
Inicializa e configura o esquema do banco de dados
"""
import os
import sqlite3
from pathlib import Path

def init_database():
    """incializa o banco de dados"""

    db_path = Path("data/players.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create players table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # cria tabela de scores
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            level INTEGER NOT NULL,
            game_time REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
        ''')
        
        # cria indices para melhorar performance das consultas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_player_id ON scores(player_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_score ON scores(score DESC)')
        
        conn.commit()
    
    print(f"Database initialized successfully at {db_path.absolute()}")

if __name__ == "__main__":
    init_database()

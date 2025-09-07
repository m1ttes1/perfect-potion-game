"""
Script para atualizar o esquema do banco de dados.
Adiciona a coluna 'best_score' à tabela 'players' se ela não existir.
"""
import os
import sqlite3
from pathlib import Path

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Database file path
DB_PATH = os.path.join(BASE_DIR, 'data', 'players.db')

def update_database():
    """Atualiza o esquema do banco de dados."""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check if the best_score column exists in the players table
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add best_score column if it doesn't exist
        if 'best_score' not in columns:
            print("Adicionando coluna 'best_score' à tabela 'players'...")
            cursor.execute("""
                ALTER TABLE players 
                ADD COLUMN best_score INTEGER DEFAULT 0
            """)
            print("Coluna 'best_score' adicionada com sucesso!")
        else:
            print("A coluna 'best_score' já existe na tabela 'players'.")
            
        # Add last_played column if it doesn't exist
        if 'last_played' not in columns:
            print("Adicionando coluna 'last_played' à tabela 'players'...")
            cursor.execute("""
                ALTER TABLE players 
                ADD COLUMN last_played TIMESTAMP
            """)
            print("Coluna 'last_played' adicionada com sucesso!")
        else:
            print("A coluna 'last_played' já existe na tabela 'players'.")
            
        # Check if game_time column exists in scores table
        cursor.execute("PRAGMA table_info(scores)")
        score_columns = [column[1] for column in cursor.fetchall()]
        
        # Add game_time column if it doesn't exist
        if 'game_time' not in score_columns:
            print("Adicionando coluna 'game_time' à tabela 'scores'...")
            cursor.execute("""
                ALTER TABLE scores 
                ADD COLUMN game_time REAL DEFAULT 0
            """)
            print("Coluna 'game_time' adicionada com sucesso!")
        else:
            print("A coluna 'game_time' já existe na tabela 'scores'.")
            
        # Commit all changes at once
        conn.commit()
        
        # Close the connection
        conn.close()
        print("Atualização do banco de dados concluída com sucesso!")
        
    except sqlite3.Error as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False
    
    return True

if __name__ == "__main__":
    print("Iniciando atualização do banco de dados...")
    if update_database():
        print("Atualização concluída com sucesso!")
    else:
        print("Falha ao atualizar o banco de dados.")
    input("Pressione Enter para sair...")

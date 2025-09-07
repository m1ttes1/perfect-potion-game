# Gerenciador do banco de dados do jogo Perfect Potion
# Serve para criar ou resetar o banco de dados de jogadores e pontuações

import sys
import sqlite3
from pathlib import Path

def init_database():
    # Cria o banco de dados com todas as tabelas necessárias e adiciona dados de teste
    db_path = Path("data/players.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)  # garante que o diretório existe

    # Remove banco existente, se houver
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Cria a tabela de jogadores
        cursor.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Cria a tabela de pontuações
        cursor.execute('''
        CREATE TABLE scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            level INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
        ''')

        # Cria índices para melhorar performance das consultas
        cursor.execute('CREATE INDEX idx_scores_player_id ON scores(player_id)')
        cursor.execute('CREATE INDEX idx_scores_score ON scores(score DESC)')

        # Adiciona alguns dados de teste
        cursor.execute("INSERT INTO players (name) VALUES ('Player 1')")
        cursor.execute("INSERT INTO players (name) VALUES ('Player 2')")
        cursor.execute("""
            INSERT INTO scores (player_id, score, level) 
            VALUES (1, 1000, 1), (1, 1500, 2), (2, 2000, 1)
        """)

        conn.commit()

    print(f"Banco de dados criado com sucesso em {db_path.absolute()}")

def show_help():
    # Mostra instruções de uso do script
    print("""
Gerenciador do banco de dados Perfect Potion
Comandos:
  init    - Cria um novo banco de dados (apaga dados existentes!)
  help    - Mostra esta mensagem
""")

def main():
    # Interpreta o comando passado pelo usuário
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == 'init':
        confirm = input("Isso apagará todos os dados existentes. Tem certeza? (y/n): ")
        if confirm.lower() == 'y':
            init_database()
    else:
        show_help()

# Executa a função principal se rodar diretamente
if __name__ == "__main__":
    main()

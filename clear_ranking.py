# Script para limpar o ranking do jogo, mantendo os jogadores cadastrados.

import os
import sqlite3
from pathlib import Path

# Caminho para o banco de dados
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.path.join(BASE_DIR, 'data', 'players.db')

def clear_ranking(clear_players=False):
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if clear_players:
            # Limpa TODOS os dados: jogadores e pontuações
            cursor.execute("DELETE FROM scores")
            cursor.execute("DELETE FROM players")
            print("✅ Base de dados limpa com sucesso!")
            print("TODOS os jogadores e pontuações foram removidos.")
        else:
            # Limpa apenas as pontuações, mantendo os jogadores
            cursor.execute("DELETE FROM scores")
            cursor.execute("UPDATE players SET best_score = 0")
            print("✅ Ranking limpo com sucesso!")
            print("Todas as pontuações foram removidas e os melhores scores foram resetados.")
        
        # Salva as alterações
        conn.commit()
        
    except Exception as e:
        print(f"❌ Erro ao limpar o ranking: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=== LIMPAR RANKING ===")
    print("1. Limpar apenas as pontuações (mantém os jogadores)")
    print("2. Limpar TUDO (jogadores e pontuações)")
    print("3. Cancelar")
    
    choice = input("Escolha uma opção (1-3): ")
    
    if choice == "1":
        confirm = input("Tem certeza que deseja limpar todas as pontuações? (s/n): ")
        if confirm.lower() == 's':
            clear_ranking(clear_players=False)
        else:
            print("Operação cancelada.")
    elif choice == "2":
        confirm = input("ATENÇÃO: Isso removerá TODOS os jogadores e pontuações. Tem certeza? (s/n): ")
        if confirm.lower() == 's':
            clear_ranking(clear_players=True)
        else:
            print("Operação cancelada.")
    else:
        print("Operação cancelada.")

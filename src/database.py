"""
Módulo database - gerencia o banco de dados SQLite que guarda os perfis dos jogadores.
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class PlayerDatabase:
    """
    Gerencia tudo relacionado ao banco de dados de jogadores:
    criar, ler, atualizar perfis e registrar sessões de jogo.
    """

    def __init__(self, db_path: str = 'players.db'):
        """
        Inicia o banco de dados.
        Cria o arquivo se não existir e garante que as tabelas estejam prontas.

        db_path: caminho do arquivo .db que vai guardar os dados
        """
        # cria a pasta do banco caso não exista
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.db_path = db_path
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Abre uma conexão com o banco. Só um helper pra não repetir código."""
        return sqlite3.connect(self.db_path)

    def _init_database(self):
        """Cria as tabelas principais se ainda não existirem."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # tabela de jogadores
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_played TIMESTAMP,
                total_score INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                best_score INTEGER DEFAULT 0
            )
            ''')

            # tabela de sessões de jogo
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
            ''')

            conn.commit()

    def create_player(self, name: str) -> int:
        """
        Cria um jogador novo no banco.
        Se já existir um jogador com o mesmo nome, vai dar erro.

        name: nome do jogador
        retorna: id do jogador criado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO players (name, last_played) VALUES (?, ?)',
                (name, datetime.now().isoformat())
            )
            conn.commit()
            return cursor.lastrowid

    def get_player(self, player_id: int) -> Optional[Dict]:
        """
        Pega os dados de um jogador pelo ID.

        player_id: id do jogador
        retorna: dicionário com os dados ou None se não achar
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_player_by_name(self, name: str) -> Optional[Dict]:
        """
        Pega os dados de um jogador pelo nome.

        name: nome do jogador
        retorna: dicionário com os dados ou None se não achar
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE name = ?', (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_last_played(self, player_id: int):
        """
        Marca que o jogador acabou de jogar, atualizando a data/hora.

        player_id: id do jogador
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE players SET last_played = ? WHERE id = ?',
                (datetime.now().isoformat(), player_id)
            )
            conn.commit()

    def get_recent_players(self, limit: int = 3) -> List[Dict]:
        """
        Pega os últimos jogadores que jogaram.

        limit: quantos jogadores retornar no máximo
        retorna: lista de dicionários com os jogadores
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM players 
                WHERE last_played IS NOT NULL 
                ORDER BY last_played DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def record_game_session(self, player_id: int, score: int, duration_seconds: int) -> None:
        """
        Salva uma sessão de jogo no banco e atualiza estatísticas do jogador.

        player_id: id do jogador
        score: pontos da sessão
        duration_seconds: duração em segundos
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # registra a sessão
            cursor.execute('''
                INSERT INTO game_sessions (player_id, score, duration_seconds, played_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (player_id, score, duration_seconds))

            # atualiza stats gerais do jogador
            cursor.execute('''
                UPDATE players 
                SET total_score = total_score + ?,
                    games_played = games_played + 1,
                    best_score = MAX(best_score, ?),
                    last_played = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (score, score, player_id))

            conn.commit()

    def get_player_stats(self, player_id: int) -> Dict:
        """
        Pega estatísticas detalhadas de um jogador.

        player_id: id do jogador
        retorna: dicionário com stats e dados do jogador
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # dados básicos do jogador
            cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
            player_data = cursor.fetchone()
            if not player_data:
                return {}

            # stats adicionais das sessões
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_games,
                    AVG(score) as avg_score,
                    MAX(score) as max_score,
                    MIN(score) as min_score,
                    SUM(duration_seconds) as total_play_time
                FROM game_sessions 
                WHERE player_id = ?
            ''', (player_id,))

            stats = dict(player_data)
            stats.update(dict(cursor.fetchone()))
            return stats

# instância global do banco
DATABASE_PATH = os.path.join('data', 'players.db')
db = PlayerDatabase(DATABASE_PATH)

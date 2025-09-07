"""
Database module for Perfect Potion game.
Handles all database operations using SQLite.
"""
import os
import sqlite3
from pathlib import Path

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file path
DB_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DB_DIR, 'players.db')

# Ensure the data directory exists
os.makedirs(DB_DIR, exist_ok=True)

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.conn = None
            self.cursor = None
            self.connect()
            self.initialize_database()
            self._initialized = True
    
    def connect(self):
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row  # This enables column access by name
            self.cursor = self.conn.cursor()
            # Enable foreign key constraints
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def initialize_database(self):
        """Initialize the database with required tables if they don't exist."""
        try:
            # Create players table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    best_score INTEGER DEFAULT 0,
                    last_played TIMESTAMP
                )
            """)
            
            # Create scores table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    level INTEGER DEFAULT 1,
                    game_time REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scores_player_id ON scores (player_id)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scores_score ON scores (score DESC)
            """)
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
            self.conn.rollback()
            raise
    
    def get_players(self):
        """Get all players from the database."""
        try:
            self.cursor.execute("SELECT * FROM players ORDER BY best_score DESC, name")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting players: {e}")
            return []
    
    def get_player(self, player_id):
        """Get a player by ID."""
        try:
            self.cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting player {player_id}: {e}")
            return None
    
    def get_player_by_name(self, name):
        """Get a player by name."""
        try:
            self.cursor.execute("SELECT * FROM players WHERE name = ?", (name,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting player by name {name}: {e}")
            return None
    
    def create_player(self, name):
        """Create a new player."""
        try:
            self.cursor.execute(
                "INSERT INTO players (name) VALUES (?)",
                (name,)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Player with name '{name}' already exists")
            return None
        except sqlite3.Error as e:
            print(f"Error creating player {name}: {e}")
            self.conn.rollback()
            return None
    
    def update_player_last_played(self, player_id):
        """Update a player's last played timestamp."""
        try:
            self.cursor.execute(
                "UPDATE players SET last_played = CURRENT_TIMESTAMP WHERE id = ?",
                (player_id,)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating player {player_id} last played: {e}")
            self.conn.rollback()
            return False
    
    def add_score(self, player_id, score, level=1, game_time=0):
        """Add or update a player's score, keeping only their highest score."""
        try:
            # Verifica se o jogador já tem uma pontuação
            self.cursor.execute(
                """
                SELECT id, score FROM scores 
                WHERE player_id = ?
                ORDER BY score DESC
                LIMIT 1
                """,
                (player_id,)
            )
            existing_score = self.cursor.fetchone()
            
            if existing_score and existing_score['score'] >= score:
                # Se o jogador já tem uma pontuação maior ou igual, não faz nada
                return existing_score['id']
            
            # Se não houver pontuação existente ou a nova for maior, insere/atualiza
            if existing_score:
                # Atualiza a pontuação existente
                self.cursor.execute(
                    """
                    UPDATE scores 
                    SET score = ?, level = ?, game_time = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (score, level, game_time, existing_score['id'])
                )
                score_id = existing_score['id']
            else:
                # Insere uma nova pontuação
                self.cursor.execute(
                    """
                    INSERT INTO scores (player_id, score, level, game_time)
                    VALUES (?, ?, ?, ?)
                    """,
                    (player_id, score, level, game_time)
                )
                score_id = self.cursor.lastrowid
            
            # Atualiza a melhor pontuação do jogador
            self.cursor.execute(
                """
                UPDATE players 
                SET best_score = ?,
                    last_played = CURRENT_TIMESTAMP
                WHERE id = ? AND (best_score IS NULL OR best_score < ?)
                """,
                (score, player_id, score)
            )
            
            self.conn.commit()
            return score_id
        except sqlite3.Error as e:
            print(f"Error adding score for player {player_id}: {e}")
            self.conn.rollback()
            return None
    
    def get_high_scores(self, limit=10):
        """Get the highest scores with player information, only the best score per player."""
        try:
            self.cursor.execute("""
                SELECT p.id as player_id, p.name, MAX(s.score) as score, 
                       s.level, s.game_time, MIN(s.created_at) as created_at
                FROM scores s
                JOIN players p ON s.player_id = p.id
                GROUP BY p.id, p.name, s.level, s.game_time
                ORDER BY score DESC, created_at ASC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting high scores: {e}")
            return []
    
    def get_player_scores(self, player_id, limit=10):
        """Get all scores for a specific player."""
        try:
            self.cursor.execute("""
                SELECT * FROM scores 
                WHERE player_id = ? 
                ORDER BY score DESC, created_at DESC
                LIMIT ?
            """, (player_id, limit))
            
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting scores for player {player_id}: {e}")
            return []

# Create a singleton instance of the database
db = Database()

"""
Configurações do jogo Perfect Potion

Contém todas as constantes e parâmetros que definem o comportamento do jogo,
como tamanho da janela, velocidade do jogador, spawn de itens e cores da interface.
"""

import os

# Diretórios de recursos e salvamento
SAVE_DIR = 'saves'          # Pasta onde os jogos salvos serão guardados
ASSETS_DIR = 'assets'       # Pasta raiz dos assets do jogo
IMAGES_DIR = 'images'       # Subpasta para imagens
SOUNDS_DIR = 'sounds'       # Subpasta para sons

# Configurações da janela
WINDOW_WIDTH = 800          # Largura da tela em pixels
WINDOW_HEIGHT = 600         # Altura da tela em pixels
GAME_TITLE = "Perfect Potion"  # Título da janela
FPS = 60                    # Frames por segundo

# Configurações da arena (área jogável)
ARENA_FLOOR_Y = WINDOW_HEIGHT - 390  # Limite inferior da área de movimento do jogador

# Configurações de spawn de itens
SPAWN_AREA_X = 0                 # Posição X inicial para spawn de itens
SPAWN_AREA_Y = 390               # Posição Y inicial (parte inferior da tela)
SPAWN_AREA_WIDTH = WINDOW_WIDTH  # Largura da área de spawn
SPAWN_AREA_HEIGHT = WINDOW_HEIGHT - 390  # Altura da área de spawn

# Configurações do jogador
PLAYER_SPEED = 5                        # Velocidade do jogador
PLAYER_SHOOT_DELAY = 250                # Tempo em ms entre tiros consecutivos
PLAYER_START_LIVES = 3                  # Vidas iniciais do jogador
PLAYER_INVULNERABILITY_DURATION = 2000  # ms de invencibilidade após levar dano

# Configurações de itens
ITEM_SPAWN_INTERVAL = 80         # ms entre spawns de itens (itens aparecem rápido)
ITEM_SPEED_MIN = 3               # Velocidade mínima dos itens
ITEM_SPEED_MAX = 7               # Velocidade máxima dos itens
MAX_ITEMS_ON_SCREEN = 100        # Limite de itens na tela ao mesmo tempo

# Pesos para spawn de itens (chance relativa)
ITEM_SPAWN_WEIGHTS = {
    'ingredient': 25,  # Ingredientes têm alta probabilidade
    'hazard': 3,       # Perigos têm probabilidade menor
    'bomb': 2          # Bombas são raras
}

# Configurações de bombas
BOMB_EXPLOSION_RADIUS = 150  # Raio de efeito da explosão em pixels

# Configurações de pontuação
SCORE_INGREDIENT = 10  # Pontos ao pegar ingrediente
SCORE_HAZARD = -5      # Pontos ao pegar perigo
SCORE_BOMB = -20       # Pontos ao pegar bomba

# Configurações da interface (UI)
DATABASE_FILE = 'data/players.db'  # Caminho do arquivo do banco de dados SQLite

# Cores básicas
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Cores da interface
UI_BG_COLOR = (40, 40, 40)        # Fundo dos painéis
UI_TEXT_COLOR = (255, 255, 255)   # Cor do texto
UI_ACCENT_COLOR = (76, 175, 80)   # Cor de destaque
LIGHT_GRAY = (200, 200, 200)      # Cinza claro para detalhes

# Desempenho e debug
MAX_PARTICLES = 100  # Limite de partículas na tela
DEBUG = True         # Ativa informações de depuração (FPS, logs)
LOG_LEVEL = 'DEBUG'  # Nível de log: DEBUG, INFO, WARNING, ERROR, CRITICAL

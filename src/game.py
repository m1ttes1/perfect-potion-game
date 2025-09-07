# Arquivo principal do jogo Perfect Potion
# Controla o loop principal, estados do jogo e gerencia as telas

import os
import time
import random
import pygame as pg
import sys
import math
import json
from datetime import datetime

# Configurações e bibliotecas básicas
import os
import time
import random
import pygame as pg
import sys
import math
import json
from datetime import datetime

# Configurações do jogo
from src import settings

# Sons e áudios
from src.assets.sounds import sounds

# Telas do jogo
from src.menu.main_menu import MainMenu
from src.menu.splash_screen import SplashScreen

# Banco de dados
from src.data.db import db

# Módulos do jogo
from src.player import Alchemist
from src.items.ingredient import Ingredient
from src.items.hazard import Hazard
from src.items.bomb import Bomb
from src.utils.hud import HUD
from src.utils.item_spawner import ItemSpawner
from src.utils.explosion import Explosion
from src.utils.damage_indicator import DamageIndicator
from src.data.potions import POTION_DATA, good_potions
from src.utils.level_manager import LevelManager


class Game:

    # Classe principal que controla todo o jogo.

    def __init__(self):
        """
        Inicializa o jogo, configurando a janela, áudio e estado inicial.
        """
        pg.init()
        
        # Configura o sistema de áudio
        try:
            pg.mixer.init()
            self.sound_enabled = True
        except Exception as e:
            print(f"Aviso: falha ao inicializar áudio: {e}")
            self.sound_enabled = False

        # Configuração da janela
        self.WINDOW_WIDTH = settings.WINDOW_WIDTH
        self.WINDOW_HEIGHT = settings.WINDOW_HEIGHT
        self.screen = pg.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pg.display.set_caption(settings.GAME_TITLE)
        
        # Configuração de fonte e tempo
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 30)  # Fonte padrão
        self.big_font = pg.font.Font(None, 72)  # Fonte para títulos
        self.small_font = pg.font.Font(None, 24)  # Fonte para textos pequenos
        self.level_up_font = pg.font.Font(None, 48)  # Fonte para mensagem de level up
        self.show_level_up = False
        self.level_up_time = 0
        self.level_up_duration = 2000  # 2 segundos
        
        # Configuração de volume
        self.music_volume = 0.1  # Volume da música (0.0 a 1.0)
        self.sfx_volume = 0.2    # Volume dos efeitos sonoros (0.0 a 1.0)
        
        # Configuração do banco de dados e estado do jogo
        self.db = db
        self.last_score = 0
        self.active_player_id = None
        self.active_player_name = None
        self.state = "MENU"  # Estado inicial do jogo
        self.running = True  # Controla o loop principal
        self.score = 0
        self.high_score = self._load_high_score()
        self.game_start_time = 0
        
        # Grupos de sprites
        self.all_sprites = pg.sprite.Group()  # Todos os sprites do jogo
        self.projectiles = pg.sprite.Group()  # Projéteis atirados
        self.items = pg.sprite.Group()        # Itens coletáveis
        
        # Referências importantes
        self.player = None  # Será configurado quando o jogo começar
        self.hud = HUD(self)  # Interface do usuário
        self.item_spawner = ItemSpawner(self)  # Controla o spawn de itens
        self.damage_indicators = []  # Indicadores de dano flutuantes
        
        # Estatísticas do jogador
        self.ingredients_collected = 0  # Total de ingredientes coletados
        self.enemies_defeated = 0       # Inimigos derrotados
        self.potions_created = 0        # Poções criadas
        self.highest_combo = 0          # Maior sequência de acertos
        self.current_combo = 0          # Sequência atual de acertos
        
        # Sistema de níveis
        self.level_manager = LevelManager()  # Gerenciador de níveis
        self.level = 1                      # Nível atual
        self.level_start_time = 0           # Quando o nível começou
        self.level_complete = False         # Se o nível foi completado
        
        # Controle de estado
        self.is_game_over = False  # Se o jogo terminou
        
        # Carrega recursos e inicia o jogo
        self._load_data()  # Carrega sons e imagens
        
        # Configura o timer para spawn de itens
        self.item_spawn_timer = pg.USEREVENT + 1
        pg.time.set_timer(self.item_spawn_timer, settings.ITEM_SPAWN_INTERVAL)
        
        # Toca a música do menu
        self._play_background_music('menu')

    def _load_data(self):
        """
        Carrega todos os recursos necessários para o jogo, incluindo sons e imagens.
        
        Este método é chamado durante a inicialização do jogo para carregar todos os
        recursos que serão usados durante a execução. Se algum recurso não puder ser
        carregado, o jogo continuará funcionando com funcionalidade reduzida.
        """
        # Inicializa o dicionário de sons
        self.sounds = {}
        
        # Carrega os efeitos sonoros se o áudio estiver habilitado
        if self.sound_enabled:
            try:
                # Define o diretório base dos sons
                sounds_dir = os.path.join(settings.ASSETS_DIR, 'sounds')
                
                # Mapeamento dos efeitos sonoros para seus respectivos arquivos
                sound_files = {
                    'collect': os.path.join('pew', 'collect.wav'),      # Som ao coletar itens
                    'damage': os.path.join('pew', 'damage.wav'),        # Som ao sofrer dano
                    'explosion': os.path.join('pew', 'explosion.wav'),  # Som de explosão
                    'level_up': 'level_up.wav',                         # Som ao subir de nível
                    'shoot': os.path.join('pew', 'pewpew_2.wav')       # Som ao atirar
                }
                
                # Carrega cada som do dicionário
                for name, filename in sound_files.items():
                    path = os.path.join(sounds_dir, filename)
                    if os.path.exists(path):
                        self.sounds[name] = pg.mixer.Sound(path)
                    else:
                        print(f"[AVISO] Arquivo de som não encontrado: {path}")
                        
            except Exception as e:
                print(f"[ERRO] Falha ao carregar sons: {e}")
        
        # Carrega a imagem de fundo do jogo
        try:
            # Define o caminho para a imagem de fundo
            bg_path = os.path.join(settings.ASSETS_DIR, 'images', 'background', '4', 'dead forest.png')
            
            # Carrega e redimensiona a imagem para o tamanho da janela
            bg_orig = pg.image.load(bg_path).convert()
            self.background_image = pg.transform.scale(bg_orig, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            
        except FileNotFoundError:
            print("[AVISO] Arquivo de fundo não encontrado. Usando fundo preto.")
            self.background_image = None
            
        except Exception as e:
            print(f"[ERRO] Falha ao carregar imagem de fundo: {e}")
            self.background_image = None  # Fallback para fundo preto

    def run(self):
        """
        Executa o loop principal do jogo, gerenciando a máquina de estados.
        
        Este método é o coração do jogo, controlando a transição entre diferentes telas
        e estados (splash, menu, jogo, ranking, etc). O loop continua rodando até que
        self.running seja definido como False.
        """
        # Inicia no estado SPLASH (tela de abertura)
        self.state = "SPLASH"
        
        # Loop principal do jogo - continua até self.running ser False
        while self.running:
            # Estado SPLASH - Tela de abertura do jogo
            if self.state == "SPLASH":
                # Importa e inicia a tela de splash
                from src.menu.splash_screen import SplashScreen
                splash = SplashScreen(self)
                next_state = splash.run()  # Executa a tela de splash
                
                # Processa o próximo estado retornado pela tela de splash
                if next_state == "QUIT":
                    self.running = False  # Encerra o jogo
                else:
                    self.state = next_state  # Muda para o próximo estado
                    
            # Estado MENU - Menu principal do jogo
            elif self.state == "MENU":
                # Inicializa e executa o menu principal
                menu = MainMenu(self)
                next_state = menu.run()
                
                # Processa a ação selecionada no menu
                if next_state == "QUIT":
                    self.running = False  # Encerra o jogo
                else:
                    self.state = next_state  # Muda para o estado selecionado
                
            # Estado GAME - Jogo principal
            elif self.state == "GAME":
                # Prepara e inicia um novo jogo
                self.setup_new_game()      # Configura o estado inicial
                self._run_game_loop()      # Executa o loop principal do jogo
                
            # Estado RANKING - Tela de melhores pontuações
            elif self.state == "RANKING":
                # Importa e exibe a tela de ranking
                from src.menu.ranking_screen import RankingScreen
                ranking_screen = RankingScreen(self)
                ranking_screen.show()
                
                # Após fechar o ranking, retorna ao menu principal
                self.state = "MENU"
                
            # Estado QUIT - Encerra o jogo
            elif self.state == "QUIT":
                self.running = False  # Sai do loop principal

    def setup_new_game(self):
        """
        Prepara e inicia um novo jogo do zero.
        
        Este método é responsável por reiniciar todo o estado do jogo, incluindo:
        - Zerar pontuação e tempo
        - Limpar todos os sprites e itens
        - Criar um novo jogador
        - Configurar o spawn de itens
        - Iniciar a música de fundo
        - Iniciar o primeiro nível
        """
        # Reinicia a pontuação e o tempo de jogo
        self.score = 0
        self.game_start_time = pg.time.get_ticks()  # Marca o início do jogo
        
        # Limpa todos os grupos de sprites para remover resquícios de jogos anteriores
        self.all_sprites.empty()    # Remove todos os sprites do jogo
        self.projectiles.empty()    # Limpa projéteis ativos
        self.items.empty()          # Remove itens restantes
        
        # Cria uma nova instância do jogador na posição central inferior da tela
        player_x = self.WINDOW_WIDTH // 2
        player_y = self.WINDOW_HEIGHT - 100  # 100 pixels acima da parte inferior
        self.player = Alchemist(self, (player_x, player_y))
        self.all_sprites.add(self.player)  # Adiciona o jogador ao grupo de sprites
        
        # Configura o timer para spawn automático de itens
        # O intervalo é definido nas configurações do jogo
        pg.time.set_timer(self.item_spawn_timer, settings.ITEM_SPAWN_INTERVAL)
        
        # Inicia a trilha sonora do jogo
        self._play_background_music('game')
        
        # Reseta o estado de game over para permitir um novo jogo
        self.is_game_over = False
        
        # Inicia o jogo no nível 1
        self.start_level(1)
        
    def start_level(self, level: int):
        """
        Inicializa um novo nível do jogo com as configurações apropriadas.
        
        Este método é responsável por:
        - Configurar as variáveis do nível
        - Notificar o gerenciador de níveis
        - Ajustar a dificuldade
        - Atualizar a interface do usuário
        
        Args:
            level (int): Número do nível a ser iniciado (começando em 1)
        """
        # Define o nível atual e reseta o estado de conclusão
        self.level = level
        self.level_complete = False
        self.level_start_time = time.time()  # Marca o início do nível
        
        # Notifica o gerenciador de níveis para configurar os requisitos
        self.level_manager.start_level(level)
        
        # Remove itens restantes do nível anterior
        self.items.empty()
        
        # Aumenta a dificuldade progressivamente a cada nível
        # Reduz o intervalo entre spawns em 50ms por nível, com mínimo de 200ms
        settings.ITEM_SPAWN_INTERVAL = max(1000 - (level * 50), 200)
        # Aplica o novo intervalo de spawn
        pg.time.set_timer(self.item_spawn_timer, settings.ITEM_SPAWN_INTERVAL)
        
        # Atualiza o HUD para refletir o novo nível
        if hasattr(self, 'hud'):
            self.hud.update_level(level)
            
    def next_level(self):
        """
        Avança para o próximo nível do jogo, realizando a transição necessária.
        
        Este método é responsável por:
        - Limpar itens e projéteis do nível atual
        - Atualizar o contador de níveis
        - Notificar o gerenciador de níveis
        - Reproduzir efeitos visuais e sonoros
        - Atualizar a interface do usuário
        """
        # Limpa todos os itens e projéteis do nível atual
        self.items.empty()          # Remove itens restantes
        self.projectiles.empty()    # Remove projéteis em voo
        
        # Incrementa o contador de níveis e atualiza o estado
        self.level += 1
        self.level_complete = False
        
        # Mostra mensagem de level up
        self.show_level_up = True
        self.level_up_time = pg.time.get_ticks()
        
        # Notifica o gerenciador de níveis sobre a mudança
        self.level_manager.start_level(self.level)
        
        # Reproduz som de avanço de nível
        self._play_sound('level_up')
        
        # Atualiza o HUD para refletir o novo nível
        if hasattr(self, 'hud'):
            self.hud.update(level=self.level)
        
        # Toca o som de level up diretamente (backup caso _play_sound falhe)
        if hasattr(self, 'sounds') and 'level_up' in self.sounds:
            self.sounds['level_up'].play()
        
        # Limpa qualquer timer de próximo nível que possa estar pendente
        # Isso evita múltiplas chamadas acidentais a este método
        pg.time.set_timer(pg.USEREVENT + 2, 0)  # Cancela o timer

    def _run_game_loop(self):
        """
        Executa o loop principal do jogo, controlando a lógica de execução.
        
        Este método é o núcleo do jogo, responsável por:
        - Manter uma taxa de quadros constante (FPS)
        - Gerenciar o ciclo de vida do jogo
        - Coordenar eventos, atualizações e renderização
        - Verificar condições de término do jogo
        
        O loop continua executando até que o jogador perca todas as vidas
        ou mude para outro estado (como o menu).
        """
        # Flag que controla a execução do loop
        game_is_running = True
        
        # Loop principal do jogo - executa enquanto o jogo estiver ativo
        while game_is_running:
            # Controla a taxa de quadros para garantir uma jogabilidade suave
            # Usa o FPS definido nas configurações do jogo
            self.clock.tick(settings.FPS)
            
            # Verifica se o jogo ainda está no estado GAME
            # Se não estiver, encerra o loop para retornar ao menu ou sair
            if self.state != "GAME":
                game_is_running = False
                continue
                
            # Etapas principais do loop do jogo:
            # 1. Processa eventos (entrada do usuário, etc)
            self.events()
            
            # 2. Atualiza a lógica do jogo (movimento, colisões, etc)
            self.update()
            
            # 3. Renderiza todos os elementos na tela
            self.draw()
            
            # Verifica se o jogador perdeu todas as vidas
            if self.player and self.player.lives <= 0:
                # Se sim, inicia a sequência de game over
                self.game_over()
                game_is_running = False

    def events(self):
        """
        Processa todos os eventos do jogo em cada frame.
        
        Responsabilidades:
        - Captura eventos do sistema (fechar janela, etc)
        - Gerencia entradas do teclado
        - Controla eventos personalizados do jogo
        - Atualiza o HUD com as informações mais recentes
        
        Este método é chamado a cada iteração do loop principal do jogo.
        """
        # Processa todos os eventos pendentes na fila de eventos do Pygame
        for event in pg.event.get():
            # Evento de fechar a janela (clique no X)
            if event.type == pg.QUIT:
                self.state = "QUIT"
                self.running = False  # Encerra o jogo
                
            # Eventos de teclado (quando uma tecla é pressionada)
            if event.type == pg.KEYDOWN:
                # Tecla ESC: Retorna ao menu principal
                if event.key == pg.K_ESCAPE:
                    self.cleanup_game()
                    self.state = "MENU"
                    
                # Barra de ESPAÇO: Dispara poção
                if event.key == pg.K_SPACE and self.player:
                    self.player.shoot()
            
            # Evento de spawn de itens (disparado por um timer)
            if event.type == self.item_spawn_timer and not self.level_complete:
                self.item_spawner.spawn_item()  # Gera novos itens na tela
                
            # Evento personalizado para avançar de nível
            elif event.type == pg.USEREVENT + 2:
                self.next_level()  # Avança para o próximo nível
                
        # Atualiza o HUD (Heads-Up Display) se existir
        if hasattr(self, 'hud') and self.hud:
            # Coleta e envia as informações mais recentes para o HUD
            self.hud.update(
                score=self.score,  # Pontuação atual
                lives=self.player.lives if hasattr(self, 'player') and self.player else 0,  # Vidas restantes
                level=self.level,  # Nível atual
                combo=self.current_combo,  # Combo atual
                highest_combo=self.highest_combo,  # Maior combo alcançado
                # Poções necessárias para completar o nível
                required_potions=self.level_manager.required_potions if hasattr(self, 'level_manager') else [],
                # Poções já coletadas
                collected_potions=self.level_manager.collected_potions if hasattr(self, 'level_manager') else []
            )

    def update(self):
        """
        Atualiza o estado do jogo a cada frame.
        
        Responsabilidades:
        - Atualiza a posição e estado de todos os sprites
        - Detecta e processa colisões
        - Gerencia a pontuação e progresso do jogador
        - Controla a lógica de níveis e fases
        
        Este método é chamado a cada iteração do loop principal do jogo.
        """
        # Obtém o estado atual do teclado para movimentação contínua
        keys = pg.key.get_pressed()
        
        # Atualiza a posição de todos os sprites do jogo
        # baseado em suas velocidades e entrada do jogador
        self.all_sprites.update(keys)
        
        # Verificação de segurança - se não houver jogador, interrompe a atualização
        if self.player is None: 
            return
        
        # Detecta colisões entre o jogador e os itens coletáveis usando máscaras para precisão
        hits_player_item = []
        for item in self.items:
            if pg.sprite.collide_mask(self.player, item):
                hits_player_item.append(item)
                item.kill()  # Remove o item da tela
        
        # Processa cada item que colidiu com o jogador
        for hit in hits_player_item:
            # Inicializa variáveis para processar a colisão
            damage = 0              # Dano a ser causado (se for um item perigoso)
            sound_to_play = None    # Som a ser reproduzido
            show_error = False      # Se deve mostrar mensagem de erro
            
            try:
                # Verifica se o item coletado é um Ingrediente (poção boa)
                if isinstance(hit, Ingredient):
                    # Só processa se estivermos no modo de fases e o nível não estiver completo
                    if hasattr(self, 'level_manager') and not self.level_complete:
                        # Obtém o nome da poção do atributo do item
                        potion_name = getattr(hit, 'potion_file_name', None)
                        
                        # Verifica se esta poção é uma das que fazem parte do nível atual
                        if potion_name and potion_name in good_potions:
                            # Registra a coleta da poção e verifica se está na ordem correta
                            correct_order, level_complete = self.level_manager.register_potion_collected(potion_name)
                            
                            # Se a poção foi coletada na ordem correta
                            if correct_order:
                                # Calcula pontos com bônus baseado no nível atual
                                points = 10 * self.level  # Quanto maior o nível, mais pontos
                                self.add_score(points)    # Adiciona pontos ao placar
                                
                                # Configura feedback visual e sonoro
                                sound_to_play = 'collect'  # Som de coleta
                                self.ingredients_collected += 1  # Contador de itens coletados
                                self.current_combo += 1    # Incrementa o combo atual
                                # Atualiza o maior combo alcançado se necessário
                                self.highest_combo = max(self.highest_combo, self.current_combo)
                                
                                # Verifica se completou o nível com sucesso
                                if level_complete:
                                    self.level_complete = True
                                    # Marca o tempo de conclusão para delay visual
                                    self.level_complete_time = pg.time.get_ticks()
                                    # Agenda o próximo nível para ser carregado após um pequeno delay
                                    pg.time.set_timer(pg.USEREVENT + 2, 500)  # .5 segundos de delay
                            else:
                                # O jogador errou a sequência de poções
                                # Apenas mostra mensagem de erro, sem remover vidas
                                print("[ERRO] Ordem incorreta! Continue tentando.")
                                self.current_combo = 0  # Reseta o combo
                                
                                # Toca som de erro
                                if hasattr(self, 'sounds') and 'error' in self.sounds:
                                    self.sounds['error'].play()
                        else:
                            # Poção coletada não faz parte do nível atual
                            # Concede pontos normalmente sem verificar ordem
                            self._handle_normal_ingredient()
                    else:
                        # Modo de jogo livre ou nível já completo
                        # Concede pontos padrão sem verificação de sequência
                        self._handle_normal_ingredient()
                
                # Item do tipo Hazard (perigoso) - causa dano ao jogador
                elif isinstance(hit, Hazard):
                    damage = hit.damage  # Valor de dano definido no objeto Hazard
                    sound_to_play = 'damage'  # Som de dano
                    self.player.take_damage(damage)  # Aplica o dano ao jogador
                    self.current_combo = 0  # Reseta o combo ao sofrer dano
                    
                    # Cria um indicador visual de dano sobre o jogador
                    if hasattr(self, 'damage_indicators'):
                        indicator = DamageIndicator(
                            f'-{damage}',  # Texto exibido (ex: "-1")
                            (self.player.rect.centerx, self.player.rect.top - 20),  # Posição acima do jogador
                            color=(255, 50, 50),  # Cor vermelha para indicar dano
                            font_size=24  # Tamanho da fonte
                        )
                        self.damage_indicators.append(indicator)  # Adiciona à lista de indicadores ativos
                
                # Processa colisão com bombas
                elif isinstance(hit, Bomb):
                    damage = 2  # Dano fixo causado por bombas
                    sound_to_play = 'explosion'  # Som característico de explosão
                    self.player.take_damage(damage)  # Aplica o dano
                    self.current_combo = 0  # Reseta o combo ao ser atingido
                    
                    # Cria um efeito visual de explosão no local da bomba
                    if hasattr(self, 'damage_indicators'):
                        # Cria o efeito de explosão com o raio definido nas configurações
                        Explosion(self, hit.rect.center, settings.BOMB_EXPLOSION_RADIUS)
                        
                        # Cria um indicador de dano sobre o jogador
                        indicator = DamageIndicator(
                            f'-{damage}',  # Texto exibido (ex: "-2")
                            (self.player.rect.centerx, self.player.rect.top - 20),  # Posição
                            color=(255, 50, 50),  # Cor vermelha
                            font_size=24
                        )
                        self.damage_indicators.append(indicator)
                
                # Reproduz o som correspondente ao tipo de colisão, se disponível
                if sound_to_play and hasattr(self, 'sounds') and sound_to_play in self.sounds:
                    self.sounds[sound_to_play].play()  # Toca o efeito sonoro
                    
                # Verifica se o jogador perdeu todas as vidas após o dano
                if damage > 0 and self.player.lives <= 0 and not self.is_game_over:
                    print("Jogador sem vidas, chamando game over...")  # Debug
                    self.game_over()  # Inicia a sequência de fim de jogo
                    return  # Interrompe a atualização atual
                    
            except Exception as e:
                # Captura e exibe erros que possam ocorrer durante o processamento de colisões
                print(f"Erro ao processar colisão: {e}")
                import traceback
                traceback.print_exc()  # Imprime o stack trace para depuração
                
            finally:
                # Garante que o HUD seja atualizado mesmo em caso de erro
                if hasattr(self, 'update_hud'):
                    self.update_hud()  # Atualiza a interface do usuário
        
        # Filtra e remove indicadores de dano que já expiraram
        # Apenas mantém os indicadores cujo método update() retorna True (ainda ativos)
        self.damage_indicators = [ind for ind in self.damage_indicators if ind.update()]
        
        # Remove itens que saíram da tela para liberar memória
        self.item_spawner.cleanup_off_screen_items()
        
        # Verifica colisões entre projéteis do jogador e itens usando máscaras
        hits_projectile_item = {}
        for proj in self.projectiles:
            for item in self.items:
                if pg.sprite.collide_mask(proj, item):
                    if proj not in hits_projectile_item:
                        hits_projectile_item[proj] = []
                    hits_projectile_item[proj].append(item)
                    proj.kill()
                    item.kill()
        
        # Se houve colisões entre projéteis e itens
        if hits_projectile_item:
            self.add_score(5)  # Concede pontos por acertar itens com projéteis
            self._play_sound('explosion')  # Toca som de explosão
            self.enemies_defeated += len(hits_projectile_item)  # Atualiza contador de itens acertados

        # Limpeza final de indicadores de dano (repetida por segurança)
        # Garante que mesmo indicadores criados durante o processamento sejam limpos
        self.damage_indicators = [ind for ind in self.damage_indicators if ind.update()]
        
        # Limpeza final de itens fora da tela (repetida por segurança)
        self.item_spawner.cleanup_off_screen_items()

    def draw(self):
        """
        Renderiza todos os elementos gráficos do jogo na tela.
        
        Este método é responsável por desenhar todos os elementos visuais do jogo,
        incluindo o fundo, sprites, efeitos especiais, HUD e mensagens de feedback.
        É chamado a cada frame para atualizar a exibição.
        """
        # Desenha o fundo do jogo
        if self.background_image:
            # Usa a imagem de fundo carregada, se disponível
            self.screen.blit(self.background_image, (0, 0))
        else:
            # Fallback para fundo preto caso não haja imagem
            self.screen.fill(settings.BLACK)

        # Desenha todos os sprites do jogo na ordem de suas camadas (layers)
        # Isso inclui jogador, itens, projéteis, etc.
        self.all_sprites.draw(self.screen)

        # Efeito visual de invencibilidade (piscando) quando o jogador está protegido
        if self.player and hasattr(self.player, 'is_invulnerable') and self.player.is_invulnerable:
            self._draw_invulnerability_aura()

        # Desenha os indicadores de dano flutuantes (ex: "-1" quando o jogador leva dano)
        for indicator in self.damage_indicators:
            indicator.draw(self.screen)

        # Elementos de interface são desenhados apenas durante o jogo
        if self.state == "GAME":
            # Desenha o HUD (Heads-Up Display) com pontuação, vidas, etc.
            self.hud.draw()
            
            # Mostra mensagem de level up se necessário
            if hasattr(self, 'show_level_up') and self.show_level_up:
                current_time = pg.time.get_ticks()
                if current_time - self.level_up_time < 2000:  # 2 segundos
                    # Cria uma superfície semi-transparente
                    overlay = pg.Surface((self.WINDOW_WIDTH, 100), pg.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))  # Preto semi-transparente
                    
                    # Renderiza o texto "LEVEL UP!"
                    level_up_text = pg.font.Font(None, 48).render(
                        f'NÍVEL {self.level} DESBLOQUEADO!', 
                        True, 
                        (255, 215, 0)  # Dourado
                    )
                    text_rect = level_up_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
                    
                    # Desenha a mensagem
                    self.screen.blit(overlay, (0, self.WINDOW_HEIGHT // 2 - 50))
                    self.screen.blit(level_up_text, text_rect)
                else:
                    self.show_level_up = False
            
            # Código mantido para referência futura, caso seja necessário exibir
            # a sequência de poções necessárias em algum momento
            # if hasattr(self, 'level_manager'):
            #     self.level_manager.draw_requirements(self.screen, 20, 20)
            
            # Exibe uma mensagem de "Nível Completo" por 3 segundos após completar um nível
            if (hasattr(self, 'level_complete') and 
                hasattr(self, 'level_complete_time') and 
                self.level_complete and 
                time.time() - self.level_complete_time < 3):
                
                # Renderiza o texto em verde para indicar sucesso
                level_complete_text = self.big_font.render(
                    f"Nível {self.level} Completo!", 
                    True, 
                    (0, 255, 0)  # Cor RGB para verde
                )
                
                # Centraliza o texto na tela
                text_rect = level_complete_text.get_rect(
                    center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2)
                )
                
                # Desenha o texto na tela
                self.screen.blit(level_complete_text, text_rect)
        
            # Exibe mensagens temporárias na tela (como dicas, avisos ou instruções)
            if (hasattr(self, 'message') and 
                hasattr(self, 'message_end_time') and 
                pg.time.get_ticks() < self.message_end_time):
                
                # Cria uma superfície semi-transparente para melhorar a legibilidade do texto
                message_surface = pg.Surface((self.WINDOW_WIDTH, 40), pg.SRCALPHA)  # SRCALPHA permite transparência
                message_surface.fill((0, 0, 0, 180))  # Preto com 70% de opacidade
                
                # Renderiza o texto da mensagem em branco para melhor contraste
                message_text = self.font.render(self.message, True, (255, 255, 255))  # Texto branco
                text_rect = message_text.get_rect(center=(self.WINDOW_WIDTH // 2, 30))  # Centralizado no topo
                
                # Desenha o fundo e o texto na tela
                self.screen.blit(message_surface, (0, 10))  # Fundo ligeiramente abaixo do topo
                self.screen.blit(message_text, text_rect)    # Texto sobre o fundo
    
        # Atualiza a tela inteira com tudo o que foi desenhado
        # Isso é essencial para que as alterações sejam visíveis ao jogador
        pg.display.flip()

    def _draw_invulnerability_aura(self):
        """
        Desenha um efeito visual ao redor do jogador quando ele está invencível.
        
        Este método cria um efeito de aura pulsante que indica visualmente ao jogador
        que ele está temporariamente protegido contra danos. A intensidade e a
        transparência da aura diminuem conforme o tempo de invencibilidade se esgota.
        """
        # Verificação de segurança: garante que o jogador existe e está no estado de invencibilidade
        if not self.player or not self.player.is_invulnerable: 
            return  # Sai do método se não houver jogador ou se ele não estiver invencível
            
        # Verifica se o tempo de invencibilidade já expirou
        current_time = pg.time.get_ticks()
        if current_time > self.player.invulnerable_until:
            self.player.is_invulnerable = False  # Desativa a invencibilidade
            return  # Sai do método se o tempo de invencibilidade acabou
            
        # Calcula o tempo restante de invencibilidade como um valor entre 0.0 e 1.0
        # Onde 1.0 é o início da invencibilidade e 0.0 é o fim
        time_left = (self.player.invulnerable_until - current_time) / settings.PLAYER_INVULNERABILITY_DURATION
        
        # Cria um efeito de pulsação suave usando a função seno
        # Multiplicador 0.01 controla a velocidade da pulsação
        # O resultado é um valor entre 0.7 e 1.0 que varia ao longo do tempo
        pulse = abs(math.sin(current_time * 0.01)) * 0.3 + 0.7
        
        # Define a transparência base com base no tempo restante de invencibilidade
        # A aura fica mais transparente conforme o tempo de invencibilidade se esgota
        base_alpha = int(150 * time_left)  # 150 é a transparência máxima (quando time_left = 1.0)
        
        # Define o raio base da aura como 70% da largura do sprite do jogador
        # Isso garante que a aura seja proporcional ao tamanho do personagem
        base_radius = int(self.player.rect.width * 0.7)
        
        # Desenha 3 círculos concêntricos para criar um efeito de aura mais rico
        # Cada iteração desenha um círculo ligeiramente maior e mais transparente
        for i in range(3):
            # Calcula a transparência para este círculo específico
            # Círculos mais externos são mais transparentes (reduz 30 de alpha por camada)
            # Garante que o valor de alpha permaneça entre 0 e 255
            alpha = min(max(0, base_alpha - (i * 30)), 255)
            
            # Calcula o raio deste círculo específico
            # Círculos mais externos são maiores (aumenta o raio em 10 pixels por camada)
            # Multiplica pelo fator de pulsação para criar o efeito de pulsação
            radius = int(base_radius + (10 * (i + 1)) * pulse)
            
            # Define a cor da aura (vermelho claro) com a transparência calculada
            # O formato é (R, G, B, A) onde A é o canal alpha (transparência)
            color = (255, 100, 100, alpha)
            
            # Apenas desenha o círculo se ainda houver transparência
            if alpha > 0:
                # Cria uma nova superfície com canal alpha para o círculo
                # O tamanho é o diâmetro do círculo (raio * 2)
                aura_surface = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
                
                # Desenha um círculo na superfície
                # Parâmetros: superfície, cor, posição (centro), raio, espessura da borda
                pg.draw.circle(aura_surface, color, (radius, radius), radius, 3)
                
                # Posiciona a superfície do círculo centralizada sobre o jogador
                # A posição é ajustada para que o centro do círculo fique no centro do jogador
                self.screen.blit(aura_surface, aura_surface.get_rect(center=self.player.rect.center))
    
    def update_hud(self):
        """
        Atualiza as informações exibidas no HUD (Heads-Up Display).
        
        Este método é responsável por coletar todos os dados do jogo que precisam
        ser exibidos na interface do usuário, como pontuação, vidas, nível atual,
        itens coletados, etc., e enviá-los para o objeto HUD para renderização.
        
        O HUD é atualizado a cada frame para refletir as mudanças no estado do jogo.
        """
        # Verificação de segurança: garante que o HUD foi inicializado
        if not hasattr(self, 'hud'):
            return  # Sai do método se o HUD não estiver disponível
        
        # Obtém o número atual de vidas do jogador
        # Usa verificação de segurança para evitar erros se o jogador não existir
        current_lives = self.player.lives if hasattr(self, 'player') and self.player else 0
        
        # Inicializa listas vazias para armazenar informações sobre as poções:
        # - required_potions: lista de poções necessárias para completar o nível atual
        # - collected_potions: lista de poções já coletadas pelo jogador
        required_potions = []
        collected_potions = []
        
        # Obtém as informações de poções do gerenciador de níveis, se disponível
        if hasattr(self, 'level_manager'):
            required_potions = self.level_manager.required_potions  # Poções necessárias para completar o nível
            collected_potions = self.level_manager.collected_potions  # Poções já coletadas
        
        # Atualiza o HUD com todas as informações relevantes
        self.hud.update(
            score=self.score,                # Pontuação atual
            lives=current_lives,             # Número de vidas restantes
            level=self.level,                # Nível atual
            combo=self.current_combo,        # Combo atual
            highest_combo=self.highest_combo, # Maior combo alcançado
            required_potions=required_potions, # Poções necessárias
            collected_potions=collected_potions # Poções coletadas
        )
    
    def show_message(self, message, duration=2000):
        """
        Exibe uma mensagem na tela por um período de tempo.
        
        Args:
            message (str): A mensagem a ser exibida
            duration (int): Duração em milissegundos (padrão: 2000ms)
        """
        if not hasattr(self, 'message') or not hasattr(self, 'message_end_time') or pg.time.get_ticks() < self.message_end_time:
            self.message = message
            self.message_start_time = pg.time.get_ticks()
            self.message_end_time = self.message_start_time + duration
    
    def _play_background_music(self, music_type='game'):
        """
        Controla a reprodução da música de fundo do jogo.
        
        Gerencia a transição suave entre diferentes faixas musicais
        dependendo do estado atual do jogo (menu ou jogo em si).
        
        Args:
            music_type (str): Tipo de música a ser reproduzida.
                            - 'menu': Música do menu principal
                            - 'game': Música durante o jogo
        """
        # Verifica se o som está habilitado
        if not self.sound_enabled:
            return
            
        # Mapeamento dos arquivos de música para cada tipo
        music_files = {
            'menu': 'The Magic Flute.wav',  # Música mais calma para o menu
            'game': 'Background Music 2.mp3'  # Música mais dinâmica para o jogo
        }
        
        # Obtém o nome do arquivo de música correspondente ao tipo solicitado
        music_file = music_files.get(music_type)
        if not music_file:
            print(f"[ERRO] Tipo de música inválido: {music_type}")
            return
            
        # Monta o caminho completo para o arquivo de música
        music_path = os.path.join(settings.ASSETS_DIR, 'sounds', 'background_music', music_file)
        
        # Verifica se o arquivo de música existe no sistema de arquivos
        if not os.path.exists(music_path):
            print(f"[AVISO] Arquivo de música não encontrado: {music_path}")
            return
            
        try:
            # Interrompe a música atual com um fadeout suave de 500ms
            if pg.mixer.music.get_busy():
                pg.mixer.music.fadeout(500)  # Fade out suave
                pg.time.delay(500)  # Aguarda o fadeout terminar
                
            # Configura e toca a música
            pg.mixer.music.load(music_path)
            volume = 0.5 if music_type == 'menu' else 0.7  # Ajusta o volume conforme necessário
            pg.mixer.music.set_volume(volume * self.music_volume)
            pg.mixer.music.play(-1)  # -1 para loop infinito
            print(f"Tocando música: {music_file}")
            
        except Exception as e:
            print(f"Erro ao reproduzir {music_file}: {e}")

    def _play_sound(self, sound_type):
        """
        Reproduz um efeito sonoro do jogo.
        
        Args:
            sound_type (str): Nome do som a ser reproduzido (deve estar no dicionário self.sounds)
        """
        # Verifica se o som está habilitado e se o dicionário de sons existe
        if not self.sound_enabled or not hasattr(self, 'sounds'): 
            return
            
        try:
            # Obtém o som do dicionário e o reproduz
            sound = self.sounds.get(sound_type)
            if sound:
                sound.set_volume(self.sfx_volume)  # Ajusta o volume
                sound.play()  # Toca o som
        except Exception as e:
            print(f"[ERRO] Falha ao reproduzir som '{sound_type}': {e}")

    def add_score(self, points):
        """
        Adiciona pontos à pontuação atual do jogador.
        
        Args:
            points (int): Quantidade de pontos a serem adicionados (pode ser negativo)
        """
        self.score += points
        
        # Atualiza o high score se necessário
        if self.score > self.high_score:
            self.high_score = self.score

    def _load_high_score(self):
        """
        Carrega a maior pontuação do jogador atual a partir do banco de dados.
        
        Returns:
            int: A maior pontuação do jogador ou 0 se não houver registro
        """
        # Verifica se há um jogador ativo
        if hasattr(self, 'active_player_id') and self.active_player_id:
            # Obtém os dados do jogador do banco de dados
            player = db.get_player(self.active_player_id)
            # Retorna a melhor pontuação se existir
            if player and 'best_score' in player:
                return player['best_score']
        # Retorna 0 se não houver jogador ou pontuação
        return 0

    def _save_high_score(self):
        """
        Método mantido apenas para compatibilidade com versões anteriores.
        
        Nota: A persistência do high score agora é gerenciada diretamente
        pelo banco de dados através do método _load_high_score().
        """
        # Este método não faz mais nada, pois a lógica foi movida para o banco de dados
        pass

        # Tenta carregar a imagem de fundo
        try:
            bg_path = os.path.join(settings.ASSETS_DIR, 'images', 'menu', 'image_fx.jpg')
            background = pg.image.load(bg_path).convert()
            background = pg.transform.scale(background, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        except FileNotFoundError:
            print("Aviso: Imagem de fundo de game over não encontrada. Usando fundo preto.")
            background = None
        except Exception as e:
            print(f"Erro ao carregar imagem de fundo: {e}")
            background = None
    
    def show_game_over_screen(self, stats):
        """Mostra a tela de game over com as estatísticas."""
        # Configurações de cor
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        
        # Tenta carregar a imagem de fundo
        background = None
        possible_bg_paths = [
            os.path.join(settings.ASSETS_DIR, 'images', 'menu', 'Image_fx.jpg'),
            os.path.join(settings.ASSETS_DIR, 'images', 'menu', 'image_fx.jpg'),
            os.path.join(settings.ASSETS_DIR, 'images', 'background', 'menu', 'Image_fx.jpg'),
            os.path.join(settings.ASSETS_DIR, 'images', 'background', 'menu', 'image_fx.jpg')
        ]
        
        for bg_path in possible_bg_paths:
            try:
                if os.path.exists(bg_path):
                    background = pg.image.load(bg_path).convert()
                    background = pg.transform.scale(background, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
                    print(f"Imagem de fundo carregada: {bg_path}")
                    break
            except Exception as e:
                print(f"Erro ao carregar imagem de fundo {bg_path}: {e}")
        else:
            print("Nenhuma imagem de fundo encontrada, usando fundo preto")
            background = None
        
        # Textos a serem exibidos
        title = self.big_font.render("FIM DE JOGO", True, RED)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 80))
        
        # Lista de estatísticas para exibir
        stats_texts = [
            f"Pontuação: {stats['score']}",
            f"Tempo de Jogo: {stats['time_played']}",
            f"Nível Alcançado: {stats['level']}",
            f"Ingredientes Coletados: {stats['ingredients_collected']}",
            f"Inimigos Derrotados: {stats['enemies_defeated']}",
            f"Poções Criadas: {stats['potions_created']}",
            f"Maior Combo: {stats['highest_combo']}"
        ]
        
        # Loop principal da tela de game over
        waiting = True
        while waiting and self.running:
            # Processa eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN or event.key == pg.K_ESCAPE or event.key == pg.K_SPACE:
                        waiting = False
            
            # Desenha o fundo
            if background:
                self.screen.blit(background, (0, 0))
            else:
                self.screen.fill(BLACK)
            
            # Desenha o título
            self.screen.blit(title, title_rect)
            
            # Desenha as estatísticas
            for i, text in enumerate(stats_texts):
                text_surface = self.font.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 180 + i * 40))
                self.screen.blit(text_surface, text_rect)
            
            # Instrução para continuar
            continue_text = self.small_font.render("Pressione ENTER, ESPAÇO ou ESC para voltar ao menu", True, WHITE)
            continue_rect = continue_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 50))
            self.screen.blit(continue_text, continue_rect)
            
            # Atualiza a tela
            pg.display.flip()
            self.clock.tick(60)
        
        # Volta para o menu principal após sair da tela de game over
        self.state = "MENU"
    
    def _handle_wrong_sequence(self, level_complete):
        """
        Lida com a coleta de itens na ordem errada.
        
        Args:
            level_complete (bool): Indica se o nível foi concluído (com falha)
        """
        print("[ERRO] Ordem incorreta! Vidas restantes:", self.player.lives if hasattr(self, 'player') and self.player else 'N/A')
        self.current_combo = 0  # Reseta o combo
        
        # Toca som de erro
        if hasattr(self, 'sounds') and 'error' in self.sounds:
            self.sounds['error'].play()
            
        # Se o nível foi concluído com falha (sem vidas restantes)
        if level_complete and hasattr(self, 'player') and self.player:
            self.player.lives = 0
            self.game_over()
    
    def game_over(self):
        """Lida com o fim de jogo, mostrando estatísticas e opções."""
        # Se o jogo já acabou, não faz nada
        if getattr(self, 'is_game_over', False):
            return
            
        print("\n=== GAME OVER ===")
        print(f"Jogador ID: {getattr(self, 'active_player_id', 'Nenhum')}")
        print(f"Score: {self.score}")
        
        try:
            # Marca que o jogo acabou para evitar processamento duplicado
            self.is_game_over = True
            
            # Calcula o tempo de jogo em segundos
            if hasattr(self, 'game_start_time') and self.game_start_time > 0:
                # Usa pg.time.get_ticks() para consistência com o resto do jogo
                # Converte de milissegundos para segundos
                game_time_sec = int((pg.time.get_ticks() - self.game_start_time) / 1000)
            else:
                game_time_sec = 0
            
            # Salva o score se houver um jogador ativo
            if hasattr(self, 'active_player_id') and self.active_player_id:
                try:
                    if hasattr(self, 'db') and hasattr(self.db, 'add_score'):
                        print("Salvando pontuação...")
                        print(f"Dados: player_id={self.active_player_id}, score={self.score}, level={self.level}, game_time={game_time_sec}")
                        
                        # Salva a pontuação no banco de dados
                        score_id = self.db.add_score(
                            player_id=self.active_player_id,
                            score=self.score,
                            level=self.level,
                            game_time=game_time_sec
                        )
                        if score_id:
                            print(f"Pontuação salva com sucesso! ID: {score_id}")
                        else:
                            print("Falha ao salvar pontuação no banco de dados")
                except Exception as e:
                    print(f"Erro ao salvar pontuação: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Nenhum jogador ativo, pontuação não salva")
            
            # Formata o tempo para exibição (MM:SS)
            minutes = int(game_time_sec // 60)
            seconds = int(game_time_sec % 60)
            
            # Prepara os dados do jogo para a tela de game over
            stats = {
                'score': self.score,
                'high_score': max(self.score, self.high_score),
                'ingredients_collected': int(getattr(self, 'ingredients_collected', 0)),
                'enemies_defeated': int(getattr(self, 'enemies_defeated', 0)),
                'potions_created': int(getattr(self, 'potions_created', 0)),
                'highest_combo': int(getattr(self, 'highest_combo', 0)),
                'level': int(getattr(self, 'level', 1)),
                'time_played': f"{minutes:02d}:{seconds:02d}"
            }
            
            # Muda o estado para GAME_OVER
            self.state = "GAME_OVER"
            
            # Mostra a tela de game over
            self.show_game_over_screen(stats)
            
        except Exception as e:
            print(f"Erro em game_over: {e}")
            import traceback
            traceback.print_exc()
            # Em caso de erro, tenta voltar para o menu de qualquer forma
            self.state = "MENU"

    def change_state(self, new_state):
        self.state = new_state

    def cleanup_game(self):
        """Limpa o estado do jogo ao retornar para o menu."""
        # Limpa todos os sprites e grupos
        self.all_sprites.empty()
        self.projectiles.empty()
        self.items.empty()
        
        # Reseta o jogador
        self.player = None
        
        # Reseta o estado do jogo
        self.score = 0
        self.level = 1
        self.is_game_over = False
        self.level_complete = False
        
        # Para a música do jogo e volta para a música do menu
        self._play_background_music('menu')

    def quit(self):
        """Encerra o jogo de forma limpa."""
        self.running = False
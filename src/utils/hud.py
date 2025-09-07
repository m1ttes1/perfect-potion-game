# src/utils/hud.py
import pygame as pg
import os
from src import settings

# Cores do tema vampiro
BLOOD_RED = (136, 8, 8)
GOLD = (218, 165, 32)
PALE_SILVER = (200, 200, 200)

class HUD:
    # responsável por desenhar as informações essenciais na tela
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pg.font.Font(None, 42)
        self.small_font = pg.font.Font(None, 28)
        self.potion_size = 50 # tamanho das imagens de poções no HUD
        self.heart_image = self._load_heart_image()
        self.potion_images = self._load_potion_images()
        
    def _load_potion_images(self):
        """
        Carrega as imagens das poções que serão exibidas no HUD.
        
        Returns:
            dict: Dicionário com as imagens das poções carregadas
        """
        potion_images = {}
        
        potion_dir = os.path.join(settings.ASSETS_DIR, 'items', 'potions')
        try:
            # carrega todos os ficheiros .png da pasta de poções
            potion_files = [f for f in os.listdir(potion_dir) if f.endswith('.png')]
            for filename in potion_files:
                path = os.path.join(potion_dir, filename)
                img = pg.image.load(path).convert_alpha()
                img_scaled = pg.transform.scale(img, (self.potion_size, self.potion_size))
                potion_name = os.path.splitext(filename)[0] # usa o nome do ficheiro sem .png como chave
                potion_images[potion_name] = img_scaled
        except Exception as e:
            print(f"Erro ao carregar imagens de poções para o HUD: {e}")
        return potion_images

    def _load_heart_image(self):
        # Cria um coração estilizado programaticamente
        size = 35
        heart = pg.Surface((size, size), pg.SRCALPHA)
        
        # Cor do coração (vermelho)
        color = (255, 50, 50)
        
        # Desenha o coração usando polígonos
        center_x, center_y = size // 2, size // 2
        
        # Desenha um coração estilizado
        points = [
            (center_x, center_y - 8),  # Topo
            (center_x + 10, center_y - 3),  # Direita superior
            (center_x + 6, center_y + 10),  # Direita inferior
            (center_x, center_y + 6),  # Fundo
            (center_x - 6, center_y + 10),  # Esquerda inferior
            (center_x - 10, center_y - 3),  # Esquerda superior
        ]
        
        pg.draw.polygon(heart, color, points)
        
        # Adiciona um brilho
        highlight = (255, 200, 200, 150)
        highlight_points = [
            (center_x, center_y - 6),
            (center_x + 4, center_y - 2),
            (center_x + 2, center_y + 4),
            (center_x - 2, center_y + 2),
        ]
        pg.draw.polygon(heart, highlight, highlight_points)
        
        return heart

    def _draw_empty_heart(self, position):
        # desenha um coração vazio ou escurecido para representar vida perdida
        empty_heart_surf = self.heart_image.copy()
        # escurece a imagem do coração
        empty_heart_surf.fill((50, 50, 50, 200), None, pg.BLEND_RGBA_MULT)
        self.screen.blit(empty_heart_surf, position)

    def draw(self):
        # Configurações de layout
        padding = 20
        screen_width = settings.WINDOW_WIDTH
        screen_height = settings.WINDOW_HEIGHT
        
        # --- 1. BARRA SUPERIOR ---
        # Fundo semi-transparente para melhorar a legibilidade
        top_bar = pg.Surface((screen_width, 60), pg.SRCALPHA)
        top_bar.fill((0, 0, 0, 150))
        self.screen.blit(top_bar, (0, 0))
        
        # --- 2. PONTUAÇÃO E NÍVEL (Esquerda) ---
        score = getattr(self.game, 'score', 0)
        score_text = self.font.render(f"PONTOS: {score}", True, settings.WHITE)
        self.screen.blit(score_text, (padding, 15))
        
        level = getattr(self.game, 'level', 1)
        level_text = self.small_font.render(f"NÍVEL: {level}", True, settings.WHITE)
        self.screen.blit(level_text, (padding, 35))
        
        # --- 3. VIDAS (Centro) ---
        if hasattr(self.game, 'player') and self.game.player is not None:
            lives = getattr(self.game.player, 'lives', 0)
            heart_size = 30
            heart_spacing = 5
            total_hearts_width = (settings.PLAYER_START_LIVES * (heart_size + heart_spacing)) - heart_spacing
            start_x = (screen_width - total_hearts_width) // 2
            
            for i in range(settings.PLAYER_START_LIVES):
                pos = (start_x + i * (heart_size + heart_spacing), 15)
                if i < lives:
                    heart_img = pg.transform.scale(self.heart_image, (heart_size, heart_size))
                    self.screen.blit(heart_img, pos)
                else:
                    empty_heart = pg.Surface((heart_size, heart_size), pg.SRCALPHA)
                    empty_heart.fill((50, 50, 50, 150))
                    self.screen.blit(empty_heart, pos)
        
        # --- 4. COMBO (Direita) ---
        current_combo = getattr(self.game, 'current_combo', 0)
        highest_combo = getattr(self.game, 'highest_combo', 0)
        
        if current_combo > 1:
            combo = current_combo  # For backward compatibility
            combo_text = f"{combo}x COMBO!"
            combo_color = (255, 215, 0)  # Dourado
            combo_font = pg.font.Font(None, 36)
            combo_surf = combo_font.render(combo_text, True, combo_color)
            combo_rect = combo_surf.get_rect(
                topright=(screen_width - padding, 10)
            )
            self.screen.blit(combo_surf, combo_rect)
            
            if highest_combo > 1 and highest_combo > combo:
                best_text = f"(Recorde: {highest_combo}x)"
                best_surf = self.small_font.render(best_text, True, settings.LIGHT_GRAY)
                best_rect = best_surf.get_rect(
                    topright=(screen_width - padding, 40)
                )
                self.screen.blit(best_surf, best_rect)
        
        # --- 5. POÇÕES NECESSÁRIAS (Parte de Baixo) ---
        if hasattr(self.game, 'level_manager') and hasattr(self.game.level_manager, 'required_potions'):
            lm = self.game.level_manager
            if hasattr(lm, 'collected_potions') and hasattr(lm, 'required_potions') and lm.required_potions:
                # Barra de fundo para as poções
                potion_bar_height = 80
                potion_bar = pg.Surface((screen_width, potion_bar_height), pg.SRCALPHA)
                potion_bar.fill((0, 0, 0, 0))
                self.screen.blit(potion_bar, (0, screen_height - potion_bar_height))
                
                # Título
                # title_text = self.small_font.render("POÇÕES:", True, (255, 255, 255))
                # title_rect = title_text.get_rect(center=(screen_width//2, screen_height - potion_bar_height + 15))
                # self.screen.blit(title_text, title_rect)
                
                # Desenha as poções necessárias
                potion_size = 40
                spacing = 10
                total_width = len(lm.required_potions) * (potion_size + spacing) - spacing
                start_x = (screen_width - total_width) // 2
                
                for i, potion_name in enumerate(lm.required_potions):
                    is_collected = i < len(lm.collected_potions)
                    x_pos = start_x + i * (potion_size + spacing)
                    y_pos = screen_height - potion_bar_height + 30
                    
                    # Tenta carregar a imagem da poção
                    potion_img = self.potion_images.get(os.path.splitext(potion_name)[0])
                    
                    if potion_img:
                        # Escala a imagem para o tamanho desejado
                        potion_img = pg.transform.scale(potion_img, (potion_size, potion_size))
                        
                        # Se não foi coletada, deixa mais escura
                        if not is_collected:
                            potion_img = potion_img.copy()
                            potion_img.fill((100, 100, 100, 180), None, pg.BLEND_RGBA_MULT)
                        
                        self.screen.blit(potion_img, (x_pos, y_pos))
                        
                        # Número da ordem (1, 2, 3...)
                        order_text = self.small_font.render(str(i+1), True, settings.WHITE)
                        order_rect = order_text.get_rect(center=(x_pos + potion_size//2, y_pos - 15))
                        self.screen.blit(order_text, order_rect)
                        
                        # Marcação de concluído
                        if is_collected:
                            check = pg.Surface((potion_size, potion_size), pg.SRCALPHA)
                            pg.draw.circle(check, (0, 255, 0, 150), 
                                         (potion_size//2, potion_size//2), 
                                         potion_size//2 - 5, 3)
                            pg.draw.line(check, (0, 255, 0), 
                                        (potion_size//4, potion_size//2),
                                        (potion_size//2, potion_size*3//4), 3)
                            pg.draw.line(check, (0, 255, 0), 
                                        (potion_size//2, potion_size*3//4),
                                        (potion_size*3//4, potion_size//4), 3)
                            self.screen.blit(check, (x_pos, y_pos))

    def _draw_potion_sequence(self):
        # desenha a sequência de poções necessárias para o nível
        lm = self.game.level_manager
        if not hasattr(lm, 'required_potions') or not lm.required_potions: return
            
        padding = 10
        
        # calcula a largura total da caixa de objetivos para a poder centralizar
        box_width = len(lm.required_potions) * (self.potion_size + padding) + padding
        box_height = self.potion_size + 40
        box_x = (settings.WINDOW_WIDTH - box_width) // 2
        box_y = settings.WINDOW_HEIGHT - box_height - 10

        # desenha um fundo semi-transparente para a lista de objetivos
        bg_surface = pg.Surface((box_width, box_height), pg.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        self.screen.blit(bg_surface, (box_x, box_y))
        
        # desenha o título "Receita:"
        title = self.small_font.render("Receita:", True, settings.WHITE)
        self.screen.blit(title, (box_x + padding, box_y + 5))
        
        # desenha as imagens das poções do objetivo
        start_x = box_x + padding
        start_y = box_y + 35
        for i, potion_name in enumerate(lm.required_potions):
            is_collected = i < len(lm.collected_potions)
            
            potion_img = self.potion_images.get(os.path.splitext(potion_name)[0])
            if potion_img:
                # deixa a imagem mais escura/transparente se ainda não foi coletada
                if not is_collected:
                    potion_img = potion_img.copy()
                    potion_img.set_alpha(100)
                
                x_pos = start_x + i * (self.potion_size + padding)
                self.screen.blit(potion_img, (x_pos, start_y))

    def update(self, score=None, lives=None, level=None, combo=None, highest_combo=None, time_elapsed=None, current_ingredients=None, required_ingredients=None, required_potions=None, collected_potions=None):
    #hud

        # Atualiza as referências no jogo
        if score is not None:
            self.game.score = score
        # Não atualiza as vidas do jogador aqui, apenas exibe o valor atual
        if level is not None:
            self.game.level = level
        if combo is not None:
            self.game.current_combo = combo
        if highest_combo is not None:
            self.game.highest_combo = highest_combo
            
        # Atualiza as poções necessárias e coletadas no level_manager
        if hasattr(self.game, 'level_manager'):
            if required_potions is not None:
                self.game.level_manager.required_potions = required_potions
                
                # Se temos novas poções necessárias, carregamos suas imagens
                if isinstance(required_potions, list) and len(required_potions) > 0:
                    for potion_file in required_potions:
                        if not potion_file:
                            continue
                        try:
                            # Remove a extensão do arquivo se existir
                            potion_name = os.path.splitext(os.path.basename(potion_file))[0]
                            
                            # Verifica se já temos essa poção carregada
                            if potion_name not in self.potion_images:
                                # Tenta carregar a imagem da poção
                                potion_path = os.path.join(settings.ASSETS_DIR, 'items', 'potions', f"{potion_name}.png")
                                if os.path.exists(potion_path):
                                    img = pg.image.load(potion_path).convert_alpha()
                                    img_scaled = pg.transform.scale(img, (self.potion_size, self.potion_size))
                                    self.potion_images[potion_name] = img_scaled
                                else:
                                    print(f"Aviso: Imagem da poção não encontrada: {potion_path}")
                        except Exception as e:
                            print(f"Erro ao carregar imagem da poção {potion_file}: {e}")
            
            if collected_potions is not None:
                self.game.level_manager.collected_potions = collected_potions

    def update_level(self, level):
        """Atualiza a exibição do nível atual no HUD"""
        self.level = level
        # O HUD será atualizado no próximo frame pelo método draw()
# Tela de splash do jogo

import pygame as pg
import os
import src.settings as settings

class SplashScreen:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.running = False
        self.load_assets()
        
    def load_assets(self):
        """Carrega os recursos visuais da tela de splash"""
        try:
            # Carrega a imagem de fundo do splash
            splash_path = os.path.join(settings.ASSETS_DIR, 'images', 'menu', 'press-start.png')
            if os.path.exists(splash_path):
                self.background = pg.image.load(splash_path).convert()
                # Redimensiona para cobrir a tela mantendo a proporção
                bg_ratio = self.background.get_width() / self.background.get_height()
                screen_ratio = settings.WINDOW_WIDTH / settings.WINDOW_HEIGHT
                
                if bg_ratio > screen_ratio:
                    new_width = int(settings.WINDOW_HEIGHT * bg_ratio)
                    self.background = pg.transform.scale(
                        self.background,
                        (new_width, settings.WINDOW_HEIGHT)
                    )
                    self.bg_x = (new_width - settings.WINDOW_WIDTH) // 2
                    self.bg_y = 0
                else:
                    new_height = int(settings.WINDOW_WIDTH / bg_ratio)
                    self.background = pg.transform.scale(
                        self.background,
                        (settings.WINDOW_WIDTH, new_height)
                    )
                    self.bg_x = 0
                    self.bg_y = (new_height - settings.WINDOW_HEIGHT) // 2
            else:
                self.background = None
                print("Aviso: Imagem de splash não encontrada.")
                
            # Configuração do texto "Pressione Start"
            self.font = pg.font.Font(None, 36)
            self.blink_speed = 0.8  # segundos
            self.blink_timer = 0
            self.show_text = True
            
        except Exception as e:
            print(f"Erro ao carregar assets da tela de splash: {e}")
            self.background = None
    
    def run(self):
        """Executa o loop principal da tela de splash"""
        self.running = True
        while self.running:
            result = self.handle_events()
            if result:
                return result
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)
        return "QUIT"
    
    def handle_events(self):
        """Lida com os eventos de entrada"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                self.game.running = False
                return "QUIT"
            elif event.type in (pg.KEYDOWN, pg.MOUSEBUTTONDOWN):
                self.running = False
                return "MENU"
    
    def update(self):
        """Atualiza o estado da tela de splash"""
        # Piscar o texto "Pressione Start"
        self.blink_timer += 1 / settings.FPS
        if self.blink_timer >= self.blink_speed:
            self.blink_timer = 0
            self.show_text = not self.show_text
    
    def draw(self):
        """Desenha a tela de splash"""
        # Desenha o fundo
        if self.background:
            self.screen.blit(self.background, (-self.bg_x, -self.bg_y))
        else:
            self.screen.fill((0, 0, 0))
        
        # Desenha o texto "Pressione Start" piscando
        if self.show_text:
            text = "Pressione Start"
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 100)
            )
            
            # Desenha o texto com sombra para melhor visibilidade
            shadow_rect = text_rect.move(2, 2)
            shadow_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow_surface, shadow_rect)
            self.screen.blit(text_surface, text_rect)
        
        pg.display.flip()

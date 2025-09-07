"""
Módulo options_menu - Menu de opções do jogo.
"""
import pygame as pg

class OptionsMenu:
    """
    Menu de opções do jogo, permitindo ajustar volume e outras configurações.
    """
    
    def __init__(self, game):
        """
        Inicializa o menu de opções.
        
        Args:
            game: Referência para a instância principal do jogo.
        """
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.done = False
        
        # Configurações de fonte
        self.title_font = pg.font.Font(None, 64)
        self.option_font = pg.font.Font(None, 36)
        self.small_font = pg.font.Font(None, 24)
        
        # Cores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.HOVER_COLOR = (200, 200, 0)  # Amarelo para hover
        self.SELECTED_COLOR = (0, 255, 0)  # Verde para selecionado
        
        # Opções de volume
        self.music_volume = game.music_volume  # Volume da música (0.0 a 1.0)
        self.sfx_volume = game.sfx_volume      # Volume dos efeitos sonoros (0.0 a 1.0)
        
        # Retângulos para as barras de volume
        self.music_volume_rect = pg.Rect(
            self.screen.get_width() // 2 - 100,
            200,
            200,
            20
        )
        
        self.sfx_volume_rect = pg.Rect(
            self.screen.get_width() // 2 - 100,
            300,
            200,
            20
        )
        
        # Qual controle de volume está sendo ajustado
        self.adjusting_music_volume = False
        self.adjusting_sfx_volume = False
        
        # Botão de voltar
        self.back_rect = pg.Rect(
            self.screen.get_width() // 2 - 100,
            400,
            200,
            50
        )
        
        # Aplica os volumes iniciais
        self._apply_volume_settings()
    
    def _apply_volume_settings(self):
        """Aplica as configurações de volume ao jogo."""
        # Atualiza os volumes no jogo
        self.game.music_volume = self.music_volume
        self.game.sfx_volume = self.sfx_volume
        
        # Aplica o volume à música de fundo
        if hasattr(self.game, '_play_background_music'):
            self.game._play_background_music('menu' if self.game.state == 'MENU' else 'game')
    
    def handle_events(self) -> bool:
        """
        Processa os eventos do menu de opções.
        
        Returns:
            bool: True se o jogo deve continuar rodando, False para sair.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
                
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.done = True
                    return True
                
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo do mouse
                    mouse_pos = pg.mouse.get_pos()
                    
                    # Verifica clique nas barras de volume
                    if self.music_volume_rect.collidepoint(mouse_pos):
                        self.adjusting_music_volume = True
                        self.music_volume = (mouse_pos[0] - self.music_volume_rect.x) / self.music_volume_rect.width
                        self.music_volume = max(0.0, min(1.0, self.music_volume))
                        self._apply_volume_settings()
                        
                    elif self.sfx_volume_rect.collidepoint(mouse_pos):
                        self.adjusting_sfx_volume = True
                        self.sfx_volume = (mouse_pos[0] - self.sfx_volume_rect.x) / self.sfx_volume_rect.width
                        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume))
                        self._apply_volume_settings()
                        
                    # Verifica clique no botão de voltar
                    elif self.back_rect.collidepoint(mouse_pos):
                        self.done = True
                        return True
            
            elif event.type == pg.MOUSEBUTTONUP:
                # Para de ajustar os volumes quando o botão do mouse é solto
                self.adjusting_music_volume = False
                self.adjusting_sfx_volume = False
                
            elif event.type == pg.MOUSEMOTION:
                if event.buttons[0]:  # Se o botão esquerdo estiver pressionado
                    mouse_pos = event.pos
                    
                    # Atualiza o volume da música ao arrastar
                    if self.adjusting_music_volume or self.music_volume_rect.collidepoint(mouse_pos):
                        self.music_volume = (mouse_pos[0] - self.music_volume_rect.x) / self.music_volume_rect.width
                        self.music_volume = max(0.0, min(1.0, self.music_volume))
                        self._apply_volume_settings()
                    
                    # Atualiza o volume dos efeitos sonoros ao arrastar
                    elif self.adjusting_sfx_volume or self.sfx_volume_rect.collidepoint(mouse_pos):
                        self.sfx_volume = (mouse_pos[0] - self.sfx_volume_rect.x) / self.sfx_volume_rect.width
                        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume))
                        self._apply_volume_settings()
                        
                        # Toca um som de teste quando ajustando o volume dos efeitos
                        if self.adjusting_sfx_volume and hasattr(self.game, '_play_sound'):
                            self.game._play_sound('collect')
        
        return True
    
    def update(self):
        """Atualiza o estado do menu."""
        pass
    
    def draw(self):
        """Desenha o menu de opções na tela."""
        self.screen.fill(self.BLACK)
        
        # Título
        title = self.title_font.render("Opções", True, self.WHITE)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Volume da Música
        music_text = self.option_font.render("Volume da Música:", True, self.WHITE)
        self.screen.blit(music_text, (self.music_volume_rect.x, self.music_volume_rect.y - 40))
        
        # Barra de volume da música
        pg.draw.rect(self.screen, (100, 100, 100), self.music_volume_rect)  # Fundo cinza
        music_filled_width = int(self.music_volume_rect.width * self.music_volume)
        music_filled_rect = pg.Rect(
            self.music_volume_rect.x,
            self.music_volume_rect.y,
            music_filled_width,
            self.music_volume_rect.height
        )
        pg.draw.rect(self.screen, self.HOVER_COLOR, music_filled_rect)  # Preenchimento amarelo
        pg.draw.rect(self.screen, self.WHITE, self.music_volume_rect, 2)  # Borda branca
        
        # Valor do volume da música em porcentagem
        music_volume_percent = int(self.music_volume * 100)
        music_volume_value = self.small_font.render(f"{music_volume_percent}%", True, self.WHITE)
        self.screen.blit(music_volume_value, (self.music_volume_rect.right + 10, self.music_volume_rect.y - 2))
        
        # Volume dos Efeitos Sonoros
        sfx_text = self.option_font.render("Volume dos Efeitos:", True, self.WHITE)
        self.screen.blit(sfx_text, (self.sfx_volume_rect.x, self.sfx_volume_rect.y - 40))
        
        # Barra de volume dos efeitos sonoros
        pg.draw.rect(self.screen, (100, 100, 100), self.sfx_volume_rect)  # Fundo cinza
        sfx_filled_width = int(self.sfx_volume_rect.width * self.sfx_volume)
        sfx_filled_rect = pg.Rect(
            self.sfx_volume_rect.x,
            self.sfx_volume_rect.y,
            sfx_filled_width,
            self.sfx_volume_rect.height
        )
        pg.draw.rect(self.screen, self.HOVER_COLOR, sfx_filled_rect)  # Preenchimento amarelo
        pg.draw.rect(self.screen, self.WHITE, self.sfx_volume_rect, 2)  # Borda branca
        
        # Valor do volume dos efeitos em porcentagem
        sfx_volume_percent = int(self.sfx_volume * 100)
        sfx_volume_value = self.small_font.render(f"{sfx_volume_percent}%", True, self.WHITE)
        self.screen.blit(sfx_volume_value, (self.sfx_volume_rect.right + 10, self.sfx_volume_rect.y - 2))
        
        # Botão de voltar
        pg.draw.rect(self.screen, self.HOVER_COLOR, self.back_rect, 0, 5)
        back_text = self.option_font.render("Voltar", True, self.BLACK)
        back_text_rect = back_text.get_rect(center=self.back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Instruções
        instructions = [
            "Clique e arraste nas barras para ajustar os volumes",
            "Clique no volume dos efeitos para testar o som",
            "ESC ou Voltar: Retorna ao menu principal"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, (180, 180, 180))
            self.screen.blit(
                inst_text,
                (self.screen.get_width() // 2 - inst_text.get_width() // 2, 500 + i * 30)
            )
    
    def run(self) -> bool:
        """
        Executa o loop principal do menu de opções.
        
        Returns:
            bool: True se o jogo deve continuar rodando, False para sair.
        """
        self.done = False
        
        while not self.done:
            # Processa eventos
            if not self.handle_events():
                return False
            
            # Atualiza o estado
            self.update()
            
            # Desenha o menu
            self.draw()
            
            # Atualiza a tela
            pg.display.flip()
            
            # Controla a taxa de quadros
            self.clock.tick(60)
        
        return True

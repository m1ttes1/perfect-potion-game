import pygame as pg
import os
from datetime import datetime
import src.settings as settings
from src.data.db import db

class RankingScreen:
    """
     Tela de ranking que exibe as melhores pontuações.
    """
    
    def __init__(self, game):
        """
        Inicializa a tela de ranking.
        
        Args:
            game: Referência ao jogo principal
        """
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        
        # Configurações de fonte
        self.title_font = pg.font.Font(None, 72)
        self.header_font = pg.font.Font(None, 36)
        self.item_font = pg.font.Font(None, 30)
        self.small_font = pg.font.Font(None, 24)
        
        # Cores do tema
        self.COLOR_BG = (20, 0, 40)  # Roxo muito escuro
        self.COLOR_ACCENT = (180, 0, 180)  # Roxo mais claro
        self.COLOR_HIGHLIGHT = (255, 215, 0)  # Dourado para itens selecionados
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_PANEL = (30, 0, 50, 200)  # Roxo semi-transparente
        
        # Configurações do painel principal
        self.panel_rect = pg.Rect(
            settings.WINDOW_WIDTH * 0.1,  # 10% da largura
            settings.WINDOW_HEIGHT * 0.2,  # 20% da altura
            settings.WINDOW_WIDTH * 0.8,   # 80% da largura
            settings.WINDOW_HEIGHT * 0.6   # 60% da altura
        )
        
        # Botão de voltar
        self.back_button = pg.Rect(
            settings.WINDOW_WIDTH // 2 - 100,
            settings.WINDOW_HEIGHT - 100,
            200, 50
        )
        
        # Configurações da tabela
        self.table_margin = 30
        self.row_height = 40
        self.header_height = 50
        
        # Posições das colunas (em % da largura do painel)
        self.column_positions = [
            0.05,  # Posição
            0.25,  # Jogador
            0.55,  # Pontos
            0.75,  # Nível
            0.9    # Data
        ]
        
        # Efeitos visuais
        self.scroll_y = 0
        self.max_scroll = 0
    
    def show(self):
        """Mostra a tela de ranking."""
        running = True
        clock = pg.time.Clock()
        
        while running and self.game.running:
            # Processa eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.running = False
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_RETURN:
                        return True
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Botão esquerdo do mouse
                        mouse_pos = pg.mouse.get_pos()
                        if self.back_button.collidepoint(mouse_pos):
                            return True
            
            # Desenha a tela
            self._draw()
            pg.display.flip()
            clock.tick(settings.FPS)
        
        return False
    
    def _draw(self):
        """Desenha a tela de ranking."""
        # Fundo com gradiente
        self.screen.fill(self.COLOR_BG)
        
        # Desenha um gradiente sutil
        gradient = pg.Surface((self.screen.get_width(), self.screen.get_height()), pg.SRCALPHA)
        for y in range(self.screen.get_height()):
            alpha = int(50 * (1 - abs(y - self.screen.get_height()//2) / (self.screen.get_height()//2)))
            pg.draw.line(gradient, (*self.COLOR_ACCENT, alpha//2), (0, y), (self.screen.get_width(), y))
        self.screen.blit(gradient, (0, 0))
        
        # Título com efeito de brilho
        title_surface = self.title_font.render("MELHORES PONTUAÇÕES", True, self.COLOR_HIGHLIGHT)
        title_rect = title_surface.get_rect(center=(settings.WINDOW_WIDTH // 2, 80))
        
        # Sombra do título
        shadow = self.title_font.render("MELHORES PONTUAÇÕES", True, (0, 0, 0, 150))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title_surface, title_rect)
        
        # Linha decorativa abaixo do título
        pg.draw.line(
            self.screen, 
            self.COLOR_ACCENT,
            (settings.WINDOW_WIDTH // 2 - 250, title_rect.bottom + 10),
            (settings.WINDOW_WIDTH // 2 + 250, title_rect.bottom + 10),
            3
        )
        
        # Desenha o painel principal
        panel = pg.Surface((self.panel_rect.width, self.panel_rect.height), pg.SRCALPHA)
        panel.fill(self.COLOR_PANEL)
        
        # Borda decorativa
        pg.draw.rect(panel, self.COLOR_ACCENT, (0, 0, self.panel_rect.width, self.panel_rect.height), 2, border_radius=10)
        
        # Cabeçalho da tabela
        headers = ["POSIÇÃO", "JOGADOR", "PONTOS", "NÍVEL", "DATA"]
        header_y = 20
        
        # Desenha cabeçalhos
        for i, header in enumerate(headers):
            x_pos = int(self.panel_rect.width * self.column_positions[i])
            text = self.header_font.render(header, True, self.COLOR_HIGHLIGHT)
            text_rect = text.get_rect(
                x=x_pos,
                y=header_y,
                height=self.header_height
            )
            
            # Centraliza verticalmente
            text_rect.centery = header_y + self.header_height // 2
            panel.blit(text, text_rect)
        
        # Linha divisória
        pg.draw.line(
            panel, 
            self.COLOR_ACCENT, 
            (20, header_y + self.header_height), 
            (self.panel_rect.width - 20, header_y + self.header_height), 
            2
        )
        
        # Área de rolagem para as pontuações
        scores_area = pg.Rect(
            0, 
            header_y + self.header_height + 10,
            self.panel_rect.width - 10,
            self.panel_rect.height - (header_y + self.header_height + 20)
        )
        
        # Cria uma superfície para o conteúdo rolável
        content_height = 0
        try:
            # Obtém as melhores pontuações do banco de dados
            top_scores = db.get_high_scores(20)  # Aumentei para 20 itens
            
            if not top_scores:
                # Mensagem quando não há pontuações
                no_scores = self.item_font.render("Nenhuma pontuação registrada ainda!", True, self.COLOR_TEXT)
                panel.blit(no_scores, (self.panel_rect.width // 2 - no_scores.get_width() // 2, 150))
            else:
                # Calcula a altura total do conteúdo
                content_height = len(top_scores) * (self.row_height + 5)
                
                # Cria uma superfície para o conteúdo rolável
                content_surface = pg.Surface((scores_area.width - 20, content_height), pg.SRCALPHA)
                
                # Desenha as pontuações
                for i, score in enumerate(top_scores):
                    y = i * (self.row_height + 5)
                    
                    # Destaque a pontuação atual (se aplicável)
                    is_current = (hasattr(self.game, 'active_player_id') and 
                                hasattr(self.game, 'score') and
                                score.get('player_id') == self.game.active_player_id and
                                score.get('score') == self.game.score)
                    
                    # Cor do texto
                    color = self.COLOR_HIGHLIGHT if is_current else self.COLOR_TEXT
                    
                    # Fundo para o item atual
                    if is_current:
                        pg.draw.rect(content_surface, (*self.COLOR_ACCENT, 50), 
                                   (10, y, scores_area.width - 30, self.row_height), 0, 5)
                    
                    # Posição com medalhas para os 3 primeiros
                    if i < 3:
                        medal_colors = [(255, 215, 0), (200, 200, 200), (205, 127, 50)]  # Ouro, Prata, Bronze
                        pg.draw.circle(content_surface, medal_colors[i], 
                                     (int(self.panel_rect.width * self.column_positions[0]) - 15, 
                                      y + self.row_height // 2), 12)
                        pos_text = self.item_font.render(f"{i+1}", True, (0, 0, 0))
                        content_surface.blit(pos_text, 
                                          (int(self.panel_rect.width * self.column_positions[0]) - 20, 
                                           y + (self.row_height - pos_text.get_height()) // 2 - 2))
                    else:
                        pos_text = self.item_font.render(f"{i+1}.", True, color)
                        content_surface.blit(pos_text, 
                                          (int(self.panel_rect.width * self.column_positions[0]) - 20, 
                                           y + (self.row_height - pos_text.get_height()) // 2))
                    
                    # Nome do jogador
                    player_name = score.get('name', 'Desconhecido')
                    name_text = self.item_font.render(player_name, True, color)
                    content_surface.blit(name_text, 
                                      (int(self.panel_rect.width * self.column_positions[1]), 
                                       y + (self.row_height - name_text.get_height()) // 2))
                    
                    # Pontuação
                    score_text = self.item_font.render(f"{score.get('score', 0):,}".replace(",", "."), True, color)
                    content_surface.blit(score_text, 
                                      (int(self.panel_rect.width * self.column_positions[2]) - score_text.get_width()//2, 
                                       y + (self.row_height - score_text.get_height()) // 2))
                    
                    # Nível
                    level_text = self.item_font.render(f"{score.get('level', 1)}", True, color)
                    content_surface.blit(level_text, 
                                      (int(self.panel_rect.width * self.column_positions[3]) - level_text.get_width()//2, 
                                       y + (self.row_height - level_text.get_height()) // 2))
                    
                    # Data formatada
                    created_at = score.get('created_at', '')
                    if created_at:
                        try:
                            date_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                            date_str = date_obj.strftime('%d/%m/%y')
                        except (ValueError, TypeError):
                            date_str = created_at[:10]
                    else:
                        date_str = "-"
                        
                    date_text = self.small_font.render(date_str, True, color)
                    content_surface.blit(date_text, 
                                      (int(self.panel_rect.width * self.column_positions[4]) - date_text.get_width(), 
                                       y + (self.row_height - date_text.get_height()) // 2))
                
                # Aplica a superfície de conteúdo ao painel com recorte
                panel.blit(content_surface, (10, scores_area.y), (0, 0, scores_area.width, scores_area.height))
                
        except Exception as e:
            print(f"Erro ao carregar ranking: {e}")
            error_text = self.item_font.render("Erro ao carregar o ranking.", True, (255, 100, 100))
            panel.blit(error_text, (self.panel_rect.width // 2 - error_text.get_width() // 2, 150))
        
        # Aplica o painel à tela
        self.screen.blit(panel, self.panel_rect)
        
        # Botão de voltar estilizado
        mouse_pos = pg.mouse.get_pos()
        is_hovered = self.back_button.collidepoint(mouse_pos)
        
        # Fundo do botão com gradiente de hover
        button_surface = pg.Surface((self.back_button.width, self.back_button.height), pg.SRCALPHA)
        button_color = (100, 0, 150, 200) if not is_hovered else (150, 0, 200, 200)
        pg.draw.rect(button_surface, button_color, (0, 0, self.back_button.width, self.back_button.height), 0, 25)
        
        # Borda do botão
        border_color = self.COLOR_ACCENT if is_hovered else (100, 0, 150)
        pg.draw.rect(button_surface, border_color, (0, 0, self.back_button.width, self.back_button.height), 2, 25)
        
        # Aplica o botão à tela
        self.screen.blit(button_surface, self.back_button)
        
        # Texto do botão
        back_text = self.header_font.render("VOLTAR", True, self.COLOR_TEXT)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Instrução
        instr_text = self.small_font.render("Pressione ESC, ENTER ou clique em VOLTAR", True, (200, 200, 200))
        self.screen.blit(instr_text, (settings.WINDOW_WIDTH // 2 - instr_text.get_width() // 2, 
                                     settings.WINDOW_HEIGHT - 40))

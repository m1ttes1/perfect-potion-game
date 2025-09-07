"""
Módulo player_menu - Menu para seleção ou criação de jogadores.
"""
import pygame as pg
from ..database import db  # Importa a instância do banco de dados

class PlayerMenu:
    """
    Menu para seleção ou criação de jogadores.
    """
    
    def __init__(self, game):
        """
        Inicializa o menu de seleção de jogador.
        
        Args:
            game: Referência para a instância principal do jogo.
        """
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.done = False
        self.selected_player_id = None
        self.player_name = ""
        self.input_active = False
        
        # Configurações de fonte
        self.title_font = pg.font.Font(None, 72)
        self.option_font = pg.font.Font(None, 42)
        self.small_font = pg.font.Font(None, 28)
        
        # Cores do tema
        self.COLOR_BG = (20, 0, 40)  # Roxo muito escuro
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_ACCENT = (180, 0, 180)  # Roxo mais claro
        self.COLOR_HIGHLIGHT = (255, 215, 0)  # Dourado para itens selecionados
        self.COLOR_INPUT_BG = (40, 10, 50)  # Fundo do campo de entrada
        self.COLOR_INPUT_TEXT = (255, 255, 255)
        self.COLOR_BUTTON = (100, 0, 150)
        self.COLOR_BUTTON_HOVER = (150, 0, 200)
        
        # Carrega a lista de jogadores recentes
        self.recent_players = db.get_recent_players(limit=5)
        self.selected_option = 0  # Opção selecionada no menu
        
        # Configura os retângulos dos elementos da UI
        screen_width, screen_height = self.screen.get_size()
        
        # Área principal do painel
        panel_width = screen_width * 0.6
        panel_height = screen_height * 0.6
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Área dos jogadores recentes
        self.player_list_rect = pg.Rect(
            panel_x + 20,
            panel_y + 100,
            panel_width - 40,
            panel_height - 180
        )
        
        # Área de criação de novo jogador (barra inferior)
        self.new_player_rect = pg.Rect(
            panel_x + 40,
            panel_y + panel_height - 60,
            panel_width - 80,
            50
        )
        
        # Campo de entrada de texto
        input_height = 40
        self.input_rect = pg.Rect(
            self.new_player_rect.x,
            self.new_player_rect.y,
            self.new_player_rect.width - 120,
            input_height
        )
        
        # Botão de confirmação
        self.confirm_rect = pg.Rect(
            self.input_rect.right + 10,
            self.new_player_rect.y,
            100,
            input_height
        )
        
        # Efeitos visuais
        self.hover_alpha = 0
        self.max_hover_alpha = 100
    
    def _draw_player_list(self):
        """Desenha a lista de jogadores recentes."""
        # Fundo do painel principal
        main_panel = pg.Surface(
            (self.player_list_rect.width + 40, self.player_list_rect.height + 120), 
            pg.SRCALPHA
        )
        main_panel.fill((30, 0, 50, 220))  # Roxo semi-transparente
        
        # Borda decorativa
        pg.draw.rect(main_panel, self.COLOR_ACCENT, 
                    (0, 0, main_panel.get_width(), main_panel.get_height()), 2, border_radius=10)
        
        # Título do painel
        title = self.title_font.render("SELECIONE SEU PERFIL", True, self.COLOR_HIGHLIGHT)
        title_rect = title.get_rect(centerx=main_panel.get_width()//2, y=30)
        
        # Sombra do título
        shadow = self.title_font.render("SELECIONE SEU PERFIL", True, (0, 0, 0, 150))
        main_panel.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        main_panel.blit(title, title_rect)
        
        # Painel interno para a lista de jogadores
        panel = pg.Surface(
            (self.player_list_rect.width, self.player_list_rect.height - 20), 
            pg.SRCALPHA
        )
        
        # Fundo da lista
        pg.draw.rect(panel, (40, 10, 60, 180), 
                    (0, 0, panel.get_width(), panel.get_height()), 
                    border_radius=8)
        
        # Título da lista
        subtitle = self.option_font.render("Jogadores Recentes", True, self.COLOR_TEXT)
        panel.blit(subtitle, (20, 20))
        
        # Linha decorativa abaixo do título
        pg.draw.line(panel, self.COLOR_ACCENT, 
                    (20, 60), 
                    (panel.get_width() - 20, 60), 
                    2)
        
        # Aplica o painel ao painel principal
        main_panel.blit(panel, (20, 100))
        
        # Ajusta a posição do retângulo da lista
        list_rect = self.player_list_rect.copy()
        list_rect.y = 100
        list_rect.height -= 20
        
        # Desenha a lista de jogadores
        list_y = 80  # Ajuste para compensar o título e a linha
        for i, player in enumerate(self.recent_players):
            # Cor do item (selecionado ou não)
            is_selected = i == self.selected_option
            color = self.COLOR_HIGHLIGHT if is_selected else self.COLOR_TEXT
            
            # Retângulo do item
            item_rect = pg.Rect(20, list_y + i * 60, self.player_list_rect.width - 40, 55)
            
            # Efeito de hover/seleção
            mouse_pos = pg.mouse.get_pos()
            is_hovered = item_rect.collidepoint(
                mouse_pos[0] - (self.player_list_rect.x + 20), 
                mouse_pos[1] - (self.player_list_rect.y + 100)  # Ajuste para a posição correta
            )
            
            # Fundo do item (hover/selecionado)
            if is_hovered or is_selected:
                hover_color = (*self.COLOR_ACCENT, 80) if is_hovered else (*self.COLOR_ACCENT, 50)
                pg.draw.rect(panel, hover_color, item_rect, 0, 5)
            
            # Borda sutil
            pg.draw.rect(panel, self.COLOR_ACCENT, item_rect, 1, 5)
            
            # Ícone do jogador (círculo com iniciais)
            initials = ''.join([name[0].upper() for name in player['name'].split()[:2]])
            if not initials:
                initials = "??"
            
            # Desenha o círculo com as iniciais
            icon_rect = pg.Rect(
                item_rect.x + 10, 
                item_rect.centery - 20, 
                40, 40
            )
            pg.draw.circle(panel, self.COLOR_ACCENT, icon_rect.center, 20)
            
            # Texto das iniciais
            initials_surf = self.option_font.render(initials, True, (255, 255, 255))
            panel.blit(initials_surf, (
                icon_rect.centerx - initials_surf.get_width() // 2,
                icon_rect.centery - initials_surf.get_height() // 2
            ))
            
            # Nome do jogador
            name = self.option_font.render(player['name'], True, color)
            panel.blit(name, (item_rect.x + 60, item_rect.y + 10))
            
            # Pontuação
            score = self.small_font.render(
                f"Melhor pontuação: {player.get('best_score', 0):,} pts".replace(",", "."), 
                True, 
                (180, 180, 180)
            )
            panel.blit(score, (item_rect.x + 62, item_rect.y + 35))
        
        # Aplica o painel à tela
        self.screen.blit(main_panel, (self.player_list_rect.x - 20, self.player_list_rect.y - 80))
    
    def _draw_new_player_panel(self):
        """Desenha o painel de criação de novo jogador."""
        # Fundo do painel
        panel = pg.Surface((self.new_player_rect.width, self.new_player_rect.height), pg.SRCALPHA)
        
        # Texto de instrução
        instruction = self.option_font.render("Novo Jogador:", True, self.COLOR_TEXT)
        panel.blit(instruction, (10, 10))
        
        # Campo de entrada
        pg.draw.rect(panel, self.COLOR_INPUT_BG, 
                    (0, 0, self.new_player_rect.width, self.new_player_rect.height), 0, 25)
        
        # Texto do campo de entrada
        if self.input_active or self.player_name:
            if self.input_active:
                # Pisca o cursor quando ativo
                if pg.time.get_ticks() // 500 % 2 == 0:
                    text = f"{self.player_name}_"
                else:
                    text = self.player_name
            else:
                text = self.player_name
            
            text_surface = self.option_font.render(text, True, self.COLOR_INPUT_TEXT)
            # Corta o texto se for muito grande
            if text_surface.get_width() > self.input_rect.width - 30:
                # Usa uma fonte menor para o texto cortado
                temp_surface = self.small_font.render(text, True, self.COLOR_INPUT_TEXT)
                if temp_surface.get_width() > self.input_rect.width - 30:
                    # Se ainda for muito grande, corta e adiciona "..."
                    temp_text = "..." + text[-(len(text)//2):]
                    temp_surface = self.small_font.render(temp_text, True, self.COLOR_INPUT_TEXT)
                panel.blit(temp_surface, (15, 15))
            else:
                panel.blit(text_surface, (15, 10))
        else:
            placeholder = self.small_font.render("Digite seu nome...", True, (150, 150, 150))
            panel.blit(placeholder, (15, 15))
        
        # Botão de confirmação (agora dentro do painel)
        button_rect = pg.Rect(
            self.input_rect.width - 110, 5, 100, 40
        )
        
        # Verifica se o mouse está sobre o botão
        mouse_pos = pg.mouse.get_pos()
        button_screen_rect = pg.Rect(
            self.new_player_rect.x + button_rect.x,
            self.new_player_rect.y + button_rect.y,
            button_rect.width,
            button_rect.height
        )
        is_hovered = button_screen_rect.collidepoint(mouse_pos)
        
        # Desenha o botão
        button_color = self.COLOR_BUTTON_HOVER if is_hovered else self.COLOR_BUTTON
        pg.draw.rect(panel, button_color, button_rect, 0, 20)
        
        # Borda do botão
        pg.draw.rect(panel, self.COLOR_ACCENT, button_rect, 2, 20)
        
        # Texto do botão
        button_text = self.small_font.render("CRIAR", True, self.COLOR_TEXT)
        panel.blit(button_text, (
            button_rect.centerx - button_text.get_width() // 2,
            button_rect.centery - button_text.get_height() // 2
        ))
        
        # Aplica o painel à tela
        self.screen.blit(panel, self.new_player_rect)
        
        # Atualiza o retângulo do botão para detecção de clique
        self.confirm_rect = button_screen_rect
    
    def handle_events(self) -> bool:
        """
        Processa os eventos do menu de seleção de jogador.
        
        Returns:
            bool: True se o jogo deve continuar rodando, False para sair.
        """
        mouse_pos = pg.mouse.get_pos()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
                
            if event.type == pg.KEYDOWN:
                if self.input_active:
                    # Lida com entrada de texto
                    if event.key == pg.K_RETURN:
                        self._create_or_select_player()
                    elif event.key == pg.K_ESCAPE:
                        self.input_active = False
                        self.player_name = ""
                    elif event.key == pg.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        # Limita o tamanho do nome e aceita apenas caracteres alfanuméricos e espaços
                        if len(self.player_name) < 20 and event.unicode.isprintable():
                            self.player_name += event.unicode
                else:
                    # Navegação com teclado
                    if event.key == pg.K_UP:
                        self.selected_option = max(0, self.selected_option - 1)
                    elif event.key == pg.K_DOWN:
                        self.selected_option = min(len(self.recent_players) - 1, self.selected_option + 1)
                    elif event.key == pg.K_RETURN and self.selected_option >= 0:
                        self.selected_player_id = self.recent_players[self.selected_option]['id']
                        self.done = True
                    elif event.key == pg.K_ESCAPE:
                        self.done = True
                        return True
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo do mouse
                    # Verifica clique nos jogadores recentes
                    for i, player in enumerate(self.recent_players):
                        item_rect = pg.Rect(
                            self.player_list_rect.x + 20,
                            self.player_list_rect.y + 70 + i * 50,
                            self.player_list_rect.width - 40,
                            45
                        )
                        if item_rect.collidepoint(mouse_pos):
                            self.selected_player_id = player['id']
                            self.done = True
                            break
                    
                    # Verifica clique no campo de texto
                    if self.input_rect.collidepoint(mouse_pos):
                        self.input_active = True
                    # Verifica clique no botão de confirmação
                    elif self.confirm_rect.collidepoint(mouse_pos) and self.player_name.strip():
                        self._create_or_select_player()
                    else:
                        self.input_active = False
            
            # Atualiza o estado do mouse para hover
            self._update_hover_effects(mouse_pos)
        
        return True
    
    def _update_hover_effects(self, mouse_pos):
        """Atualiza os efeitos de hover nos elementos interativos."""
        # Atualiza o hover nos itens da lista de jogadores
        for i, _ in enumerate(self.recent_players):
            item_rect = pg.Rect(
                self.player_list_rect.x + 20,
                self.player_list_rect.y + 70 + i * 50,
                self.player_list_rect.width - 40,
                45
            )
            if item_rect.collidepoint(mouse_pos):
                self.selected_option = i
                break
        else:
            if not self.input_rect.collidepoint(mouse_pos) and not self.confirm_rect.collidepoint(mouse_pos):
                self.selected_option = -1
    
    def _create_or_select_player(self):
        """Cria um novo jogador ou seleciona um existente com base no nome digitado."""
        player_name = self.player_name.strip()
        if not player_name:
            return
        
        # Verifica se já existe um jogador com esse nome
        existing_player = db.get_player_by_name(player_name)
        
        if existing_player:
            # Jogador existente
            self.selected_player_id = existing_player['id']
        else:
            # Cria um novo jogador
            try:
                self.selected_player_id = db.create_player(player_name)
            except Exception as e:
                print(f"Erro ao criar jogador: {e}")
                return
        
        # Atualiza a lista de jogadores recentes
        db.update_last_played(self.selected_player_id)
        self.recent_players = db.get_recent_players(limit=5)
        self.done = True
    
    def update(self):
        """Atualiza o estado do menu."""
        pass  # Nada a fazer por enquanto
    
    def run(self):
        """
        Executa o loop principal do menu de seleção de jogador.
        
        Returns:
            bool: True se um jogador foi selecionado, False caso contrário.
        """
        running = True
        while running and not self.done:
            # Processa eventos
            running = self.handle_events()
            
            # Atualiza o estado
            self.update()
            
            # Desenha o menu
            self.draw()
            
            # Atualiza a tela
            pg.display.flip()
            
            # Controla a taxa de quadros
            self.clock.tick(60)
        
        # Retorna True se um jogador foi selecionado, False caso contrário
        return self.selected_player_id is not None
    
    def draw(self):
        """Desenha o menu de seleção de jogador."""
        # Fundo com gradiente
        self.screen.fill(self.COLOR_BG)
        
        # Desenha um gradiente sutil
        gradient = pg.Surface((self.screen.get_width(), self.screen.get_height()), pg.SRCALPHA)
        for y in range(self.screen.get_height()):
            alpha = int(50 * (1 - abs(y - self.screen.get_height()//2) / (self.screen.get_height()//2)))
            pg.draw.line(gradient, (*self.COLOR_ACCENT, alpha//2), (0, y), (self.screen.get_width(), y))
        self.screen.blit(gradient, (0, 0))
        
        # Desenha o painel de jogadores recentes (que agora inclui o título principal)
        self._draw_player_list()
        
        # Desenha o painel de novo jogador (barra inferior)
        self._draw_new_player_panel()
        
        # Lista de jogadores recentes
        subtitle = self.option_font.render("Jogadores Recentes:", True, self.WHITE)
        self.screen.blit(subtitle, (self.screen.get_width() // 2 - 150, 160))
        
        for i, player in enumerate(self.recent_players):
            # Destaque para o item selecionado
            color = self.SELECTED_COLOR if i == self.selected_option else self.WHITE
            
            # Formata a informação do jogador
            player_text = f"{player['name']} (Melhor: {player.get('best_score', 0)})"
            text_surface = self.option_font.render(player_text, True, color)
            
            # Posiciona o texto
            text_rect = text_surface.get_rect(topleft=(self.screen.get_width() // 2 - 140, 200 + i * 40))
            self.screen.blit(text_surface, text_rect)
            
            # Desenha um retângulo de seleção se estiver selecionado
            if i == self.selected_option and not self.input_active:
                pg.draw.rect(
                    self.screen, 
                    self.HOVER_COLOR, 
                    (text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10),
                    2
                )
        
        # Opção para novo jogador
        new_player_y = 200 + len(self.recent_players) * 40 + 20
        
        # Campo de entrada de texto
        pg.draw.rect(self.screen, self.INPUT_BG, self.input_rect, 0, 5)
        pg.draw.rect(self.screen, self.WHITE if self.input_active else (100, 100, 100), self.input_rect, 2, 5)
        
        # Texto de placeholder ou nome digitado
        if not self.player_name and not self.input_active:
            placeholder = self.small_font.render("Digite um nome para novo jogador...", True, (150, 150, 150))
            self.screen.blit(placeholder, (self.input_rect.x + 10, self.input_rect.y + 10))
        else:
            name_surface = self.option_font.render(self.player_name, True, self.INPUT_TEXT)
            self.screen.blit(name_surface, (self.input_rect.x + 10, self.input_rect.y + 5))
        
        # Botão de confirmação
        confirm_color = self.HOVER_COLOR if self.player_name.strip() else (100, 100, 100)
        pg.draw.rect(self.screen, confirm_color if self.player_name.strip() else (50, 50, 50), self.confirm_rect, 0, 5)
        confirm_text = self.option_font.render("Confirmar", True, self.BLACK if self.player_name.strip() else (100, 100, 100))
        confirm_text_rect = confirm_text.get_rect(center=self.confirm_rect.center)
        self.screen.blit(confirm_text, confirm_text_rect)
        
        # Instruções
        instructions = [
            "Setas para Navegar | ENTER: Selecionar | ESC: Voltar",
            "Digite um nome para criar um novo jogador ou selecione um existente."
        ]
        
        for i, line in enumerate(instructions):
            inst_surface = self.small_font.render(line, True, (150, 150, 150))
            self.screen.blit(inst_surface, (self.screen.get_width() // 2 - inst_surface.get_width() // 2, 550 + i * 25))

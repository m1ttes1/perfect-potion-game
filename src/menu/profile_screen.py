import pygame as pg
from src.data.db import db

class ProfileScreen:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        
        # Configurações de fonte
        self.title_font = pg.font.Font(None, 48)  # Reduzido de 72 para 48
        self.option_font = pg.font.Font(None, 36)  # Reduzido de 42 para 36
        self.small_font = pg.font.Font(None, 24)   # Reduzido de 28 para 24
        self.input_font = pg.font.Font(None, 30)   # Nova fonte para o campo de entrada
        
        # Cores do tema
        self.COLOR_BG = (20, 0, 40)  # Roxo muito escuro
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_ACCENT = (180, 0, 180)  # Roxo mais claro
        self.COLOR_HIGHLIGHT = (255, 215, 0)  # Dourado para itens selecionados
        self.COLOR_INPUT_BG = (40, 10, 50)  # Fundo do campo de entrada
        self.COLOR_INPUT_TEXT = (255, 255, 255)
        self.COLOR_BUTTON = (100, 0, 150)
        self.COLOR_BUTTON_HOVER = (150, 0, 200)
        
        self.profiles = []
        self.selected_profile = 0
        self.input_text = ""
        self.input_active = False
        self.load_profiles()
        
        # Configurações de layout
        self.panel_width = self.screen.get_width() * 0.6
        self.panel_height = self.screen.get_height() * 0.7
        self.panel_x = (self.screen.get_width() - self.panel_width) // 2
        self.panel_y = (self.screen.get_height() - self.panel_height) // 2
        
        # Área da lista de perfis
        self.list_rect = pg.Rect(
            self.panel_x + 40,
            self.panel_y + 120,
            self.panel_width - 80,
            self.panel_height - 220
        )
        
        # Área de criação de novo perfil
        self.input_rect = pg.Rect(
            self.panel_x + 40,
            self.panel_y + self.panel_height - 80,
            self.panel_width - 200,
            50
        )
        
        # Botão de criar
        self.create_button = pg.Rect(
            self.panel_x + self.panel_width - 140,
            self.panel_y + self.panel_height - 80,
            100,
            50
        )
        
        # Botão de voltar (menor)
        self.back_button = pg.Rect(
            self.screen.get_width() // 2 - 60,  # Largura reduzida
            self.panel_y + self.panel_height + 20,
            120,  # Largura reduzida de 200 para 120
            40    # Altura reduzida de 50 para 40
        )

    def load_profiles(self):
        """Carrega os perfis salvos do banco de dados."""
        try:
            self.profiles = db.get_players()
            print(f"Perfis carregados: {self.profiles}")
        except Exception as e:
            print(f"Erro ao carregar perfis: {e}")
            self.profiles = []

    def run(self):
        """Executa a tela de seleção de perfil"""
        running = True
        clock = pg.time.Clock()
        
        # Carrega os perfis novamente para garantir que temos os dados mais recentes
        self.load_profiles()
        
        while running and self.game.running:
            mouse_pos = pg.mouse.get_pos()
            mouse_clicked = False
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.running = False
                    return False
                    
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self.input_active:
                            self.input_active = False
                            self.input_text = ""
                        else:
                            return False  # Retorna False para indicar que nenhum perfil foi selecionado
                    
                    # Navegação pelo teclado
                    if not self.input_active:
                        if event.key == pg.K_UP:
                            self.selected_profile = max(0, self.selected_profile - 1)
                        elif event.key == pg.K_DOWN:
                            self.selected_profile = min(len(self.profiles) - 1, self.selected_profile + 1)
                        elif event.key == pg.K_RETURN:
                            if 0 <= self.selected_profile < len(self.profiles):
                                return self._select_profile(self.profiles[self.selected_profile])
                    
                    # Entrada de texto para novo perfil
                    if self.input_active:
                        if event.key == pg.K_RETURN and self.input_text.strip():
                            self._create_profile()
                        elif event.key == pg.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif len(self.input_text) < 15 and event.unicode.isprintable():
                            self.input_text += event.unicode
                
                # Clique do mouse
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Botão esquerdo
                        mouse_clicked = True
                        
                        # Verifica clique no campo de entrada
                        if self.input_rect.collidepoint(event.pos):
                            self.input_active = True
                        else:
                            self.input_active = False
                            
                        # Verifica clique no botão de criar
                        if self.create_button.collidepoint(event.pos) and self.input_text.strip():
                            self._create_profile()
                            
                        # Verifica clique no botão de voltar
                        if self.back_button.collidepoint(event.pos):
                            return False  # Retorna False para indicar que nenhum perfil foi selecionado
                            
                        # Verifica clique nos itens da lista
                        for i, profile in enumerate(self.profiles):
                            item_rect = pg.Rect(
                                self.list_rect.x,
                                self.list_rect.y + i * 60,
                                self.list_rect.width,
                                55
                            )
                            if item_rect.collidepoint(event.pos):
                                return self._select_profile(profile)
            
            # Desenha a tela
            self._draw()
            pg.display.flip()
            clock.tick(60)
        
        return False
    
    def _select_profile(self, profile):
        """Seleciona um perfil existente"""
        self.game.active_player_id = profile['id']
        self.game.active_player_name = profile['name']
        self.game.score = 0
        return True
    
    def _create_profile(self):
        """Cria um novo perfil"""
        if self.input_text.strip():
            self.create_new_profile(self.input_text.strip())
            self.input_text = ""
            self.input_active = False
            self.load_profiles()
            # Seleciona o último perfil adicionado
            if self.profiles:
                self.selected_profile = len(self.profiles) - 1
                
    def create_new_profile(self, name):
        """Cria um novo perfil de jogador"""
        try:
            player_id = db.create_player(name)
            if player_id is not None:
                self.game.active_player_id = player_id
                self.game.active_player_name = name
                self.load_profiles()
                return True
            print(f"Erro: Já existe um jogador com o nome '{name}'")
            return False
        except Exception as e:
            print(f"Erro ao criar perfil: {e}")
            return False
            
    def _draw(self):
        """Desenha a tela de seleção de perfil"""
        # Fundo com gradiente
        self.screen.fill(self.COLOR_BG)
        
        # Desenha um gradiente sutil
        gradient = pg.Surface((self.screen.get_width(), self.screen.get_height()), pg.SRCALPHA)
        for y in range(self.screen.get_height()):
            alpha = int(50 * (1 - abs(y - self.screen.get_height()//2) / (self.screen.get_height()//2)))
            pg.draw.line(gradient, (*self.COLOR_ACCENT, alpha//2), (0, y), (self.screen.get_width(), y))
        self.screen.blit(gradient, (0, 0))
        
        # Painel principal
        panel = pg.Surface((self.panel_width, self.panel_height), pg.SRCALPHA)
        panel.fill((30, 0, 50, 220))  # Roxo semi-transparente
        
        # Borda decorativa
        pg.draw.rect(panel, self.COLOR_ACCENT, (0, 0, self.panel_width, self.panel_height), 2, border_radius=10)
        
        # Título com lógica para ajustar o tamanho se necessário
        title_text = "SELECIONE UM PERFIL"
        title_font_size = 48
        title_font = pg.font.Font(None, title_font_size)
        
        # Reduz o tamanho da fonte até caber no painel
        while True:
            title_surface = title_font.render(title_text, True, self.COLOR_HIGHLIGHT)
            if title_surface.get_width() < self.panel_width - 40 or title_font_size <= 24:
                break
            title_font_size -= 2
            title_font = pg.font.Font(None, title_font_size)
        
        title_rect = title_surface.get_rect(centerx=self.panel_width//2, y=20)  # Ajustado o posicionamento vertical
        
        # Sombra do título
        shadow = title_font.render(title_text, True, (0, 0, 0, 150))
        panel.blit(shadow, (title_rect.x + 2, title_rect.y + 2))
        panel.blit(title_surface, title_rect)
        
        # Painel da lista de perfis
        list_panel = pg.Surface((self.list_rect.width, self.list_rect.height), pg.SRCALPHA)
        pg.draw.rect(list_panel, (40, 10, 60, 180), (0, 0, self.list_rect.width, self.list_rect.height), 0, 8)
        
        # Cabeçalho da lista
        header = self.option_font.render("Jogadores Salvos", True, self.COLOR_TEXT)
        list_panel.blit(header, (20, 10))
        
        # Linha decorativa
        pg.draw.line(list_panel, self.COLOR_ACCENT, (20, 50), (self.list_rect.width - 20, 50), 2)
        
        # Lista de perfis
        if not self.profiles:
            no_profiles = self.small_font.render("Nenhum perfil encontrado. Crie um novo abaixo!", True, (180, 180, 180))
            list_panel.blit(no_profiles, (self.list_rect.width//2 - no_profiles.get_width()//2, 100))
        else:
            for i, profile in enumerate(self.profiles):
                item_rect = pg.Rect(10, 60 + i * 60, self.list_rect.width - 20, 55)
                is_selected = (i == self.selected_profile)
                mouse_pos = pg.mouse.get_pos()
                is_hovered = item_rect.collidepoint(
                    mouse_pos[0] - self.list_rect.x - self.panel_x - 40,
                    mouse_pos[1] - self.list_rect.y - self.panel_y - 120
                )
                
                # Fundo do item (hover/selecionado)
                if is_selected or is_hovered:
                    color = (*self.COLOR_ACCENT, 80) if is_hovered else (*self.COLOR_ACCENT, 50)
                    pg.draw.rect(list_panel, color, item_rect, 0, 5)
                
                # Borda sutil
                pg.draw.rect(list_panel, self.COLOR_ACCENT, item_rect, 1, 5)
                
                # Ícone do jogador (círculo com iniciais)
                initials = ''.join([name[0].upper() for name in profile['name'].split()[:2]])
                if not initials:
                    initials = "??"
                
                # Desenha o círculo com as iniciais
                icon_rect = pg.Rect(
                    item_rect.x + 10, 
                    item_rect.centery - 20, 
                    40, 40
                )
                pg.draw.circle(list_panel, self.COLOR_ACCENT, (icon_rect.x + 20, icon_rect.y + 20), 20)
                
                # Texto das iniciais
                initials_surf = self.option_font.render(initials, True, (255, 255, 255))
                list_panel.blit(initials_surf, (icon_rect.x + 20 - initials_surf.get_width()//2,
                                             icon_rect.y + 20 - initials_surf.get_height()//2))
                
                # Nome do jogador
                name = self.option_font.render(profile['name'], True, 
                                            self.COLOR_HIGHLIGHT if is_selected else self.COLOR_TEXT)
                list_panel.blit(name, (item_rect.x + 60, item_rect.y + 10))
                
                # Melhor pontuação
                score = profile.get('best_score', 0) or 0
                score_text = self.small_font.render(
                    f"Melhor pontuação: {int(score):,}".replace(",", "."), 
                    True, 
                    (180, 180, 180)
                )
                list_panel.blit(score_text, (item_rect.x + 62, item_rect.y + 35))
        
        # Aplica o painel da lista ao painel principal
        panel.blit(list_panel, (40, 120))
        
        # Área de criação de novo perfil
        create_panel = pg.Surface((self.panel_width - 40, 80), pg.SRCALPHA)
        
        # Título menor para criar novo perfil
        create_title = self.small_font.render("Criar Novo Perfil:", True, self.COLOR_TEXT)
        create_panel.blit(create_title, (10, 5))  # Ajustado o posicionamento vertical
        
        # Campo de entrada
        pg.draw.rect(create_panel, self.COLOR_INPUT_BG, 
                    (0, 40, self.input_rect.width, 50), 0, 25)
        
        # Texto do campo de entrada
        if self.input_text or self.input_active:
            if self.input_active and pg.time.get_ticks() // 500 % 2 == 0:
                display_text = self.input_text + "_"
            else:
                display_text = self.input_text
                
            text_surface = self.option_font.render(display_text, True, self.COLOR_INPUT_TEXT)
            if text_surface.get_width() > self.input_rect.width - 30:
                # Usa uma fonte menor para o texto cortado
                temp_surface = self.small_font.render(display_text, True, self.COLOR_INPUT_TEXT)
                if temp_surface.get_width() > self.input_rect.width - 30:
                    # Se ainda for muito grande, corta e adiciona "..."
                    temp_text = "..." + display_text[-(len(display_text)//2):]
                    temp_surface = self.small_font.render(temp_text, True, self.COLOR_INPUT_TEXT)
                create_panel.blit(temp_surface, (15, 55))
            else:
                create_panel.blit(text_surface, (15, 50))
        else:
            placeholder = self.small_font.render("Digite seu nome...", True, (150, 150, 150))
            create_panel.blit(placeholder, (15, 55))
        
        # Botão de criar
        is_hovered = self.create_button.collidepoint(pg.mouse.get_pos())
        button_color = self.COLOR_BUTTON_HOVER if is_hovered else self.COLOR_BUTTON
        pg.draw.rect(create_panel, button_color, 
                    (self.create_button.x - self.panel_x - 40, 40, 100, 50), 0, 25)
        
        # Borda do botão
        pg.draw.rect(create_panel, self.COLOR_ACCENT, 
                    (self.create_button.x - self.panel_x - 40, 40, 100, 50), 2, 25)
        
        # Texto do botão
        button_text = self.small_font.render("CRIAR", True, self.COLOR_TEXT)
        create_panel.blit(button_text, (
            self.create_button.x - self.panel_x - 40 + 50 - button_text.get_width()//2,
            40 + 25 - button_text.get_height()//2
        ))
        
        # Aplica o painel de criação ao painel principal
        panel.blit(create_panel, (0, self.panel_height - 100))
        
        # Aplica o painel principal à tela
        self.screen.blit(panel, (self.panel_x, self.panel_y))
        
        # Botão de voltar
        is_hovered = self.back_button.collidepoint(pg.mouse.get_pos())
        button_color = self.COLOR_BUTTON_HOVER if is_hovered else self.COLOR_BUTTON
        
        # Fundo do botão com gradiente de hover
        button_surface = pg.Surface((self.back_button.width, self.back_button.height), pg.SRCALPHA)
        pg.draw.rect(button_surface, button_color, (0, 0, self.back_button.width, self.back_button.height), 0, 25)
        
        # Borda do botão
        border_color = self.COLOR_ACCENT if is_hovered else (100, 0, 150)
        pg.draw.rect(button_surface, border_color, (0, 0, self.back_button.width, self.back_button.height), 2, 25)
        
        # Aplica o botão à tela
        self.screen.blit(button_surface, self.back_button)
        
        # Texto do botão de voltar menor
        back_text = self.small_font.render("VOLTAR", True, self.COLOR_TEXT)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Instruções com fonte menor
        instr_font = pg.font.Font(None, 20)  # Fonte menor para as instruções
        instr_text = instr_font.render("Pressione ESC ou clique em VOLTAR para retornar", True, (180, 180, 180))
        self.screen.blit(instr_text, (self.screen.get_width() // 2 - instr_text.get_width() // 2, 
                                     self.screen.get_height() - 25))  # Ajustado o posicionamento

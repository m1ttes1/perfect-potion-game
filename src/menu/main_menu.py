import pygame as pg
import sys
import os
import src.settings as settings
from src.menu.profile_screen import ProfileScreen


class MainMenu:
    # a classe que gere o menu principal do jogo
    def __init__(self, game):
        # guarda as referências principais do jogo
        self.game = game
        self.screen = game.screen
        self.clock = game.clock

        # variável para controlar para qual ecrã vamos a seguir
        self.next_state = None

        # carrega a fonte que vamos usar nos textos
        self.font = pg.font.Font(None, 50)  # fonte principal para os botões
        self.font_title = pg.font.Font(None, 80)  # fonte maior para o título
        self.small_font = pg.font.Font(None, 30)  # fonte menor para informações adicionais

        # cores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.HOVER_COLOR = (200, 200, 0)  # amarelo para a opção selecionada
        self.PLAYER_COLOR = (100, 255, 100)  # verde para o jogador atual

        # opções do menu e qual está selecionada
        self.options = ["Novo Jogo", "Trocar Jogador", "Ranking", "Sair"]
        self.selected_option = 0

        # carrega os assets visuais do menu
        self._load_assets()

    def _load_assets(self):
        # Cores do tema vampírico
        self.COLOR_BG = (10, 0, 10)  # Preto arroxeado
        self.COLOR_TEXT = (200, 0, 0)  # Vermelho sangue
        self.COLOR_HIGHLIGHT = (255, 40, 40)  # Vermelho mais brilhante
        self.COLOR_ACCENT = (100, 0, 0)  # Vermelho escuro
        
        # Carrega a fonte personalizada ou usa a padrão
        try:
            # Tenta carregar uma fonte gótica se disponível
            font_path = os.path.join(settings.ASSETS_DIR, 'fonts', 'MedievalSharp-Regular.ttf')
            if os.path.exists(font_path):
                self.title_font = pg.font.Font(font_path, 72)
                self.font = pg.font.Font(font_path, 42)
                self.small_font = pg.font.Font(font_path, 28)
            else:
                print("Aviso: Fonte personalizada não encontrada, usando fonte padrão")
                self.title_font = pg.font.SysFont('timesnewroman', 72, bold=True)
                self.font = pg.font.SysFont('timesnewroman', 42)
                self.small_font = pg.font.SysFont('timesnewroman', 28)
        except Exception as e:
            print(f"Erro ao carregar fontes: {e}")
            self.title_font = pg.font.SysFont('timesnewroman', 72, bold=True)
            self.font = pg.font.SysFont('timesnewroman', 42)
            self.small_font = pg.font.SysFont('timesnewroman', 28)
        
        # Carrega a imagem de fundo
        bg_paths = [
            os.path.join(settings.ASSETS_DIR, 'images', 'menu', 'menu_background.jpg'),
        ]
        
        self.background = None
        for bg_path in bg_paths:
            try:
                if os.path.exists(bg_path):
                    print(f"Carregando fundo: {bg_path}")
                    self.background = pg.image.load(bg_path).convert()
                    # Ajusta o tamanho para cobrir a tela mantendo a proporção
                    bg_ratio = self.background.get_width() / self.background.get_height()
                    screen_ratio = settings.WINDOW_WIDTH / settings.WINDOW_HEIGHT
                    
                    if bg_ratio > screen_ratio:
                        new_width = int(settings.WINDOW_HEIGHT * bg_ratio)
                        self.background = pg.transform.smoothscale(
                            self.background, 
                            (new_width, settings.WINDOW_HEIGHT)
                        )
                        self.bg_x = (new_width - settings.WINDOW_WIDTH) // 2
                        self.bg_y = 0
                    else:
                        new_height = int(settings.WINDOW_WIDTH / bg_ratio)
                        self.background = pg.transform.smoothscale(
                            self.background,
                            (settings.WINDOW_WIDTH, new_height)
                        )
                        self.bg_x = 0
                        self.bg_y = (new_height - settings.WINDOW_HEIGHT) // 2
                    
                    # Escurece a imagem de fundo para melhor contraste
                    darken = pg.Surface((self.background.get_width(), self.background.get_height()))
                    darken.fill((20, 0, 20))  # Tom roxo escuro
                    self.background.blit(darken, (0, 0), special_flags=pg.BLEND_MULT)
                    break  # Sai do loop se conseguir carregar a imagem
                else:
                    print(f"Aviso: Imagem de fundo não encontrada em {bg_path}")
            except Exception as e:
                print(f"Erro ao carregar o fundo {bg_path}: {e}")
        
        if self.background is None:
            print("Erro: Não foi possível carregar nenhuma imagem de fundo")
            # Cria um fundo preto simples
            self.background = pg.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
            self.background.fill((0, 0, 0))
            self.bg_x = 0
            self.bg_y = 0

    def run(self):
        # executa o loop principal do menu
        running = True
        while running:
            self.clock.tick(settings.FPS)
            
            # Processa eventos
            should_continue = self.handle_events()
            if not should_continue:
                return "QUIT"
                
            # Desenha o menu
            self.draw()
            
            # Se next_state foi definido, sai do loop
            if self.next_state is not None:
                return self.next_state
                
        return "QUIT"  # Se sair do loop sem definir next_state, sai do jogo

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pg.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pg.K_RETURN:
                    if self.options[self.selected_option] == "Novo Jogo":
                        if not self.game.active_player_id:
                            # Se não houver jogador ativo, mostra a tela de seleção de perfil
                            profile_screen = ProfileScreen(self.game)
                            if not profile_screen.run():
                                return  # Usuário cancelou
                        self.next_state = "GAME"
                    elif self.options[self.selected_option] == "Trocar Jogador":
                        profile_screen = ProfileScreen(self.game)
                        profile_screen.run()  # Não precisa verificar o retorno, apenas atualiza o jogador
                    elif self.options[self.selected_option] == "Ranking":
                        from src.menu.ranking_screen import RankingScreen
                        ranking_screen = RankingScreen(self.game)
                        ranking_screen.show()
                    elif self.options[self.selected_option] == "Sair":
                        pg.quit()
                        sys.exit()
        return True

    def draw(self):
        # Preenche o fundo com a cor de fundo
        self.screen.fill(self.COLOR_BG)
        
        # Desenha a imagem de fundo se existir
        if hasattr(self, 'background'):
            self.screen.blit(self.background, (-self.bg_x, -self.bg_y))
        
        # Desenha uma sobreposição com cor temática para melhorar a legibilidade
        overlay = pg.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        overlay.set_alpha(150)  # Ajuste de opacidade para melhor contraste
        # Cor roxa escura com um toque de azul para combinar com o tema de poções
        overlay.fill((30, 0, 40))  # Roxo muito escuro
        self.screen.blit(overlay, (0, 0))
        
        # Adiciona um leve gradiente para o centro
        gradient = pg.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pg.SRCALPHA)
        for y in range(settings.WINDOW_HEIGHT):
            # Gradiente que fica mais transparente no centro
            alpha = int(50 * (1 - abs(y - settings.WINDOW_HEIGHT//2) / (settings.WINDOW_HEIGHT//2)))
            pg.draw.line(gradient, (80, 0, 100, alpha), (0, y), (settings.WINDOW_WIDTH, y))
        self.screen.blit(gradient, (0, 0))
        
        # Desenha o título do jogo com estilo vampírico
        title_surface = self.title_font.render("PERFECT POTION", True, self.COLOR_TEXT)
        title_rect = title_surface.get_rect(centerx=settings.WINDOW_WIDTH//2, top=80)
        
        # Adiciona um efeito de sombra ao título
        shadow = self.title_font.render("PERFECT POTION", True, (20, 0, 0))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title_surface, title_rect)
        
        # Adiciona um sublinhado decorativo
        pg.draw.line(
            self.screen, 
            self.COLOR_ACCENT, 
            (settings.WINDOW_WIDTH//2 - 150, title_rect.bottom + 10), 
            (settings.WINDOW_WIDTH//2 + 150, title_rect.bottom + 10), 
            3
        )
        
        # Mostra o jogador atual
        if hasattr(self.game, 'active_player_name') and self.game.active_player_name:
            # Fundo para o nome do jogador
            player_bg = pg.Surface((250, 40))
            player_bg.set_alpha(180)
            player_bg.fill((20, 0, 20))
            self.screen.blit(player_bg, (settings.WINDOW_WIDTH - 270, 10))
            
            # Ícone de jogador (um círculo simples)
            pg.draw.circle(
                self.screen, 
                self.COLOR_HIGHLIGHT, 
                (settings.WINDOW_WIDTH - 250, 30), 
                12, 
                2
            )
            
            # Texto do jogador
            player_text = self.small_font.render(
                f"{self.game.active_player_name}", 
                True, 
                self.COLOR_HIGHLIGHT
            )
            player_rect = player_text.get_rect(
                midleft=(settings.WINDOW_WIDTH - 230, 30)
            )
            
            # Sombra do texto
            shadow = self.small_font.render(
                f"{self.game.active_player_name}", 
                True, 
                (20, 0, 0)
            )
            self.screen.blit(shadow, (player_rect.x + 1, player_rect.y + 1))
            self.screen.blit(player_text, player_rect)
        
        # Desenha as opções do menu com estilo
        option_y = 250
        for i, option in enumerate(self.options):
            # Define as cores baseado na seleção
            if i == self.selected_option:
                color = self.COLOR_HIGHLIGHT
                # Adiciona um marcador de seleção com mais espaçamento
                selector = self.font.render(">>", True, self.COLOR_HIGHLIGHT)
                self.screen.blit(selector, (settings.WINDOW_WIDTH//2 - 150, option_y - 5))  # Aumentado de 120 para 150
                selector = self.font.render("<<", True, self.COLOR_HIGHLIGHT)
                self.screen.blit(selector, (settings.WINDOW_WIDTH//2 + 120, option_y - 5))  # Aumentado de 100 para 120
            else:
                color = self.COLOR_TEXT
            
            # Renderiza o texto da opção com sombra
            text_shadow = self.font.render(option, True, (20, 0, 0))
            text_surface = self.font.render(option, True, color)
            
            # Posiciona o texto no centro da tela
            text_rect = text_surface.get_rect(
                centerx=settings.WINDOW_WIDTH//2,
                top=option_y
            )
            
            # Desenha a sombra e depois o texto
            self.screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
            self.screen.blit(text_surface, text_rect)
            
            option_y += 60  # Espaçamento entre as opções
            
        # Mostra instruções de controle com estilo
        controls_text = "[↑↓] Navegar    [ENTER] Selecionar    [ESC] Sair"
        controls = self.small_font.render(controls_text, True, (100, 0, 0))
        controls_rect = controls.get_rect(
            centerx=settings.WINDOW_WIDTH//2,
            bottom=settings.WINDOW_HEIGHT - 30
        )
        
        # Fundo para os controles
        controls_bg = pg.Surface((controls_rect.width + 40, controls_rect.height + 10))
        controls_bg.set_alpha(150)
        controls_bg.fill((10, 0, 10))
        self.screen.blit(
            controls_bg, 
            (controls_rect.x - 20, controls_rect.y - 5)
        )
        
        # Borda decorativa
        pg.draw.rect(
            self.screen, 
            self.COLOR_ACCENT, 
            (controls_rect.x - 20, controls_rect.y - 5, 
             controls_rect.width + 40, controls_rect.height + 10),
            1
        )
        
        # Texto dos controles
        self.screen.blit(controls, controls_rect)
        
        # Versão do jogo
        version = self.small_font.render("v1.0", True, (80, 0, 0))
        self.screen.blit(version, (20, settings.WINDOW_HEIGHT - 40))

        # Atualiza a tela
        pg.display.flip()
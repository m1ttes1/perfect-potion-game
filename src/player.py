"""
Módulo player - Contém a classe Alchemist que representa o personagem do jogador.
"""
import os
import pygame as pg
from src import settings
from src.projectile import Projectile


class Alchemist(pg.sprite.Sprite):
    """
    Classe que representa o personagem principal do jogo, o Alquimista.
    
    Atributos:
        idle_frames (list): Lista de superfícies para a animação de parado.
        running_frames (list): Lista de superfícies para a animação de corrida.
        image (pygame.Surface): Imagem atual do personagem.
        rect (pygame.Rect): Retângulo que define a posição e tamanho do personagem.
        speed (int): Velocidade de movimento do personagem.
        lives (int): Número de vidas restantes.
        is_invulnerable (bool): Indica se o jogador está em estado de invencibilidade.
        invulnerable_until (int): Timestamp até quando o jogador está invencível.
    """
    
    def __init__(self, game, initial_pos):
        """
        Inicializa o personagem do jogador.
        
        Args:
            game: Referência para a instância principal do jogo.
            initial_pos (tuple): Posição inicial (x, y) do personagem.
        """
        super().__init__()
        
        if not isinstance(initial_pos, (tuple, list)) or len(initial_pos) != 2:
            raise ValueError("A posição inicial deve ser uma tupla (x, y)")
            
        self.game = game
        self.lives = settings.PLAYER_START_LIVES
        self.is_invulnerable = False
        self.invulnerable_until = 0
        
        # Configurações de animação
        self.idle_frames = []
        self.running_frames = []
        self._load_animations()
        
        # Controle de animação
        self.idle_frame_index = 0
        self.running_frame_index = 0
        self.last_update_time = pg.time.get_ticks()
        self.animation_speed = 100  # ms por frame
        
        # Estado e direção
        self.is_running = False
        self.direction = 'right'
        self.shoot_direction = pg.math.Vector2(1, 0)
        
        # Controle de tiro
        self.shoot_delay = settings.PLAYER_SHOOT_DELAY
        self.last_shot_time = 0
        
        # Configuração inicial
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect(center=initial_pos)
        self.speed = settings.PLAYER_SPEED

    def take_damage(self, amount=1):
        """
        Aplica dano ao jogador se não estiver invulnerável
        """
        current_time = pg.time.get_ticks()
        
        # Verifica se está invulnerável
        if self.is_invulnerable and current_time < self.invulnerable_until:
            print("Jogador invulnerável - dano ignorado!")  # Debug
            return False  # Não causou dano
        
        # Aplica o dano
        self.lives -= amount
        print(f"Dano aplicado! Vidas restantes: {self.lives}")  # Debug
        
        # Ativa invulnerabilidade
        self.is_invulnerable = True
        self.invulnerable_until = current_time + settings.PLAYER_INVULNERABILITY_DURATION
        print(f"Invulnerabilidade ativada até: {self.invulnerable_until}")  # Debug
        
        # Garante que o jogador não fique com vidas negativas
        if self.lives < 0:
            self.lives = 0
            
        # Atualiza o HUD imediatamente
        if hasattr(self, 'game') and hasattr(self.game, 'update_hud'):
            self.game.update_hud()
            
        return True  # Causou dano
    
    def _activate_invulnerability(self):
        """Ativa o estado de invencibilidade temporária."""
        self.is_invulnerable = True
        self.invulnerable_until = pg.time.get_ticks() + settings.PLAYER_INVULNERABILITY_DURATION
    
    def _update_invulnerability(self):
        """Atualiza o estado de invencibilidade."""
        if self.is_invulnerable and pg.time.get_ticks() > self.invulnerable_until:
            self.is_invulnerable = False
    
    def die(self):
        """Lida com a morte do jogador."""
        # Aqui você pode adicionar lógica de game over
        print("Jogador morreu!")
        # Exemplo: self.game.game_over()
    
    def shoot(self):
        """Dispara um projétil na direção atual do jogador."""
        now = pg.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            
            # Cria o projétil na posição do jogador
            projectile = Projectile(
                self.rect.center,  # posição inicial
                self.shoot_direction  # direção do tiro
            )
            
            # Adiciona o projétil aos grupos apropriados
            self.game.all_sprites.add(projectile)
            self.game.projectiles.add(projectile)
            
            # Toca o som de tiro, se disponível
            if hasattr(self.game, 'shoot_sound') and self.game.shoot_sound:
                self.game.shoot_sound.play()
    
    def update(self, keys):
        """
        Atualiza o jogador a cada frame
        """
        # ... código existente do movimento ...
        
        # 🛡️ VERIFICA SE A INVULNERABILIDADE EXPIROU
        if hasattr(self, 'invulnerable_until'):
            current_time = pg.time.get_ticks()
            if self.invulnerable_until <= current_time:
                self.is_invulnerable = False
                print("Invulnerabilidade expirou!")  # Debug
        
        # ... resto do código ...

    def _handle_movement(self, keys):
        """Lida com o movimento do jogador baseado nas teclas pressionadas."""
        # Reseta o estado de movimento
        self.is_running = False
        
        # Movimento horizontal
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rect.x -= self.speed
            self.direction = 'left'
            self.shoot_direction = pg.math.Vector2(-1, 0)
            self.is_running = True
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rect.x += self.speed
            self.direction = 'right'
            self.shoot_direction = pg.math.Vector2(1, 0)
            self.is_running = True
            
        # Movimento vertical (opcional)
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.rect.y -= self.speed
            self.shoot_direction = pg.math.Vector2(0, -1)
            self.is_running = True
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.rect.y += self.speed
            self.shoot_direction = pg.math.Vector2(0, 1)
            self.is_running = True
    
    def _keep_in_bounds(self):
        """Mantém o jogador dentro dos limites da tela."""
        # Limita o jogador à área da tela
        self.rect.x = max(0, min(self.rect.x, settings.WINDOW_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, settings.WINDOW_HEIGHT - self.rect.height))
    
    def _update_animation(self):
        """Atualiza a animação do personagem com base no estado atual."""
        now = pg.time.get_ticks()
        
        # Atualiza o frame da animação se passou tempo suficiente
        if now - self.last_update_time > self.animation_speed:
            self.last_update_time = now
            
            # Seleciona a lista de frames apropriada
            if self.is_running:
                frames = self.running_frames
                frame_index = self.running_frame_index = (self.running_frame_index + 1) % len(frames)
            else:
                frames = self.idle_frames
                frame_index = self.idle_frame_index = (self.idle_frame_index + 1) % len(frames)
            
            # Atualiza a imagem atual
            self.image = frames[frame_index]
            
            # Inverte a imagem se estiver virado para a esquerda
            if self.direction == 'left':
                self.image = pg.transform.flip(self.image, True, False)
    
    def _load_animations(self):
        """Carrega e prepara as animações do personagem."""
        base_path = os.path.join(settings.ASSETS_DIR, settings.IMAGES_DIR, 'player', 'dark_oracle_3')
        player_width = 80

        # Carrega os frames da animação 'Idle'
        idle_path = os.path.join(base_path, 'Idle')
        for i in range(2):
            filename = f'0_Dark_Oracle_Idle_00{i}.png'
            img = pg.image.load(os.path.join(idle_path, filename)).convert_alpha()
            original_width, original_height = img.get_size()
            aspect_ratio = original_height / original_width
            scaled_height = int(player_width * aspect_ratio)
            self.idle_frames.append(pg.transform.scale(img, (player_width, scaled_height)))

        # carrega os frames da animação 'Running'
        running_path = os.path.join(base_path, 'Running')
        for i in range(12):
            filename = f'0_Dark_Oracle_Running_0{i:02}.png'
            img = pg.image.load(os.path.join(running_path, filename)).convert_alpha()
            original_width, original_height = img.get_size()
            aspect_ratio = original_height / original_width
            scaled_height = int(player_width * aspect_ratio)
            self.running_frames.append(pg.transform.scale(img, (player_width, scaled_height)))

    def update(self, keys):
        # a função de update principal, chama os métodos de ajuda para organização
        self._handle_input(keys)
        self._animate()
        self._check_boundaries()

    def _handle_input(self, keys):
        # lida com o movimento e atualiza o estado do jogador
        self.is_running = False
        move_vector = pg.math.Vector2(0, 0)

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            move_vector.x = -1
            self.direction = 'left'
            self.is_running = True
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            move_vector.x = 1
            self.direction = 'right'
            self.is_running = True
        if keys[pg.K_UP] or keys[pg.K_w]:
            move_vector.y = -1
            self.is_running = True
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            move_vector.y = 1
            self.is_running = True

        # se houver movimento, atualiza a posição e a direção do tiro
        if move_vector.length() > 0:
            move_vector.normalize_ip()  # normaliza para evitar movimento diagonal mais rápido
            self.rect.move_ip(move_vector * self.speed)
            self.shoot_direction = move_vector

    def shoot(self):
        # cria um projétil se o cooldown já passou
        now = pg.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now

            # Toca o som de tiro, se disponível
            if hasattr(self.game, 'shoot_sound') and self.game.shoot_sound:
                self.game.shoot_sound.play()

            projectile = Projectile(self.rect.center, self.shoot_direction)
            self.game.all_sprites.add(projectile)
            self.game.projectiles.add(projectile)

    def _animate(self):
        # lida com o loop da animação e o espelhamento da imagem
        now = pg.time.get_ticks()
        if now - self.last_update_time > self.animation_speed:
            self.last_update_time = now
            if self.is_running:
                self.running_frame_index = (self.running_frame_index + 1) % len(self.running_frames)
                new_image = self.running_frames[self.running_frame_index]
            else:
                self.idle_frame_index = (self.idle_frame_index + 1) % len(self.idle_frames)
                new_image = self.idle_frames[self.idle_frame_index]

            # espelha a imagem baseado na direção
            if self.direction == 'left':
                self.image = pg.transform.flip(new_image, True, False)
            else:
                self.image = new_image

    def _check_boundaries(self):
        # mantém o jogador dentro dos limites da tela/arena
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > settings.WINDOW_WIDTH: self.rect.right = settings.WINDOW_WIDTH
        if self.rect.top < settings.ARENA_FLOOR_Y: self.rect.top = settings.ARENA_FLOOR_Y
        if self.rect.bottom > settings.WINDOW_HEIGHT: self.rect.bottom = settings.WINDOW_HEIGHT
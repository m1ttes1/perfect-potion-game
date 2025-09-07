"""
Classe base para todos os itens do jogo (poções, bombas, etc).
"""
import os
import random
import pygame as pg
from abc import ABC, abstractmethod
from src import settings


class Item(pg.sprite.Sprite, ABC):
    """
    Classe base para todos os itens que aparecem na tela.
    
    Controla movimento, colisão e comportamento básico dos itens.
    """
    
    def __init__(self, image):
        """
        Prepara o item para aparecer no jogo.
        
        Args:
            image: Imagem do item (deve ser uma superfície Pygame)
        """
        super().__init__()
        
        if not isinstance(image, pg.Surface):
            raise ValueError("A imagem fornecida deve ser uma superfície Pygame")
            
        self.image = image
        self.rect = self.image.get_rect()
        self.collected = False
        
        # Cria uma máscara para colisão mais precisa
        self.mask = pg.mask.from_surface(self.image)
        
        # Velocidade será ajustada pelo spawner
        self.speed_x = random.randrange(settings.ITEM_SPEED_MIN, settings.ITEM_SPEED_MAX)
    
    def update(self, *args, **kwargs):
        """
        Atualiza a posição do item a cada frame.
        
        Movimenta o item na tela e verifica se saiu dos limites.
        """
        # Movimento horizontal
        self.rect.x += self.speed_x
        
        # Verifica se saiu da tela
        self._check_offscreen()
    
    def _check_offscreen(self):
        """
        Verifica se o item saiu da tela e remove se necessário.
        
        Checa os lados e a parte de baixo da tela.
        """
        offscreen = False
        
        # Verifica se saiu pelos lados
        if (self.speed_x > 0 and self.rect.left > settings.WINDOW_WIDTH) or \
           (self.speed_x < 0 and self.rect.right < 0):
            offscreen = True
            
        # Verifica se saiu por baixo
        if hasattr(self, 'speed_y') and self.speed_y > 0 and self.rect.top > settings.WINDOW_HEIGHT:
            offscreen = True
            
        if offscreen:
            self.kill()
    
    def _add_colored_border(self, border_color, border_width=1):
        """
        Desenha uma borda ao redor do item.
        
        Usado para destacar itens especiais ou perigosos.
        
        Args:
            border_color: Cor da borda (R,G,B) ou (R,G,B,A)
            border_width: Espessura da borda em pixels
        """
        # Cria uma cópia da imagem original
        original = self.image.copy()
        
        # Adiciona um canal alpha se não existir
        if original.get_bytesize() == 3:
            original = original.convert_alpha()
        
        # Cria uma superfície para a borda
        border_surface = pg.Surface(original.get_size(), pg.SRCALPHA)
        
        # Ajusta a opacidade da cor da borda
        if len(border_color) == 3:
            border_color = (*border_color, 100)  # Adiciona transparência
        else:
            border_color = (*border_color[:3], 100)  # Ajusta transparência
        
        # Desenha um retângulo vazado para criar a borda
        pg.draw.rect(border_surface, border_color, 
                    border_surface.get_rect(), 
                    border_width, 
                    border_radius=3)  # Cantos levemente arredondados
        
        # Combina a borda com a imagem original
        final_image = original.copy()
        final_image.blit(border_surface, (0, 0))
        
        # Atualiza a imagem mantendo a posição
        old_center = self.rect.center
        self.image = final_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center
    
    @abstractmethod
    def on_collect(self, player):
        """
        Chamado quando o jogador pega este item.
        
        Cada tipo de item implementa seu próprio comportamento.
        
        Args:
            player: Referência ao jogador que pegou o item
            
        Returns:
            int: Pontos ganhos ou perdidos
        """
        pass
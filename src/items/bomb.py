# src/items/bomb.py
import pygame as pg
import os
import random
from .base_item import Item


class Bomb(Item):
    """
    Item perigoso que explode quando coletado.
    Causa dano ao jogador e pode afetar outros itens próximos.
    """
    
    def __init__(self, game=None):
        """
        Cria uma nova bomba na tela.
        
        Args:
            game: Referência ao jogo principal (opcional)
        """
        print("\n--- Iniciando Bomb.__init__ ---")
        
        # Tenta carregar a imagem da bomba
        try:
            bomb_files = [
                'Icon41.png',
                'bomb.png'
            ]
            
            image_loaded = False
            
            # Procura a imagem em várias pastas diferentes
            base_paths = [
                os.path.join('assets', 'items', 'bombs'),  # Relativo ao diretório de trabalho
                os.path.join('..', '..', '..', 'assets', 'items', 'bombs'),  # Relativo ao arquivo
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'items', 'bombs')  # Caminho absoluto
            ]
            
            for base_path in base_paths:
                if image_loaded:
                    break
                    
                for bomb_file in bomb_files:
                    try:
                        image_path = os.path.join(base_path, bomb_file)
                        abs_path = os.path.abspath(image_path)
                        print(f"Tentando carregar: {abs_path}")
                        
                        if os.path.exists(abs_path):
                            print(f"Arquivo encontrado em: {abs_path}")
                            original_image = pg.image.load(abs_path).convert_alpha()
                            self.image = pg.transform.scale(original_image, (40, 40))
                            print("Imagem da bomba carregada com sucesso!")
                            image_loaded = True
                            break
                        else:
                            print(f"Arquivo não encontrado em: {abs_path}")
                    except Exception as e:
                        print(f"Erro ao carregar {bomb_file}: {e}")
            
            if not image_loaded:
                raise FileNotFoundError("Nenhuma imagem de bomba encontrada")
                
        except Exception as e:
            print(f"Erro ao carregar imagem da bomba: {e}")
            print("Usando placeholder...")
            # Cria um placeholder se não conseguir carregar a imagem
            self.image = pg.Surface((40, 40), pg.SRCALPHA)
            pg.draw.circle(self.image, (255, 0, 0), (20, 20), 18)  # Círculo vermelho
            pg.draw.circle(self.image, (128, 0, 0), (20, 20), 15)  # Círculo vermelho mais escuro dentro
        
        # Chama o __init__ da classe mãe (Item), que já configura a posição corretamente
        super().__init__(self.image)
        
        # Borda laranja para mostrar que é perigoso
        self._add_colored_border((255, 100, 0), 4)  # Laranja-avermelhado mais chamativo
        
        self.explosion_radius = 150  # Raio da explosão em pixels
        self.damage = 2  # Dano causado pela bomba
        
        # A posição é definida pelo spawner, não mude aqui
        print(f"Bomb criado na posição: ({self.rect.x}, {self.rect.y})")
        print("--- Fim do Bomb.__init__ ---\n")
    
    def on_collect(self, player):
        """
        Chamado quando o jogador pega a bomba.
        Faz a bomba explodir e causa dano.
        
        Args:
            player: Referência ao jogador que pegou a bomba
            
        Returns:
            int: Pontos perdidos (número negativo)
        """
        print("BOOM! A bomba explodiu!")
        
        # Marca como pego e tira da tela
        self.collected = True
        self.kill()  # Remove a bomba do grupo de sprites
        
        return -10  # Retorna pontuação negativa (penalidade por coletar uma bomba)
import pygame as pg
import os
import random
from .base_item import Item
from src import settings
from src.data.potions import POTION_DATA


class Hazard(Item):
    """
    Item perigoso que causa dano ao jogador.
    Aparece como uma poção vermelha e tira vida quando coletado.
    """

    def __init__(self, game=None, potion_file_name=None):
        """
        Cria um novo perigo no jogo.
        
        Args:
            game: Referência para o jogo principal
            potion_file_name: Nome do arquivo da poção (se não informado, pega uma aleatória)
        """
        print("\n--- Iniciando Hazard.__init__ ---")

        # Se não informou uma poção específica, pega uma aleatória das ruins
        if potion_file_name is None:
            bad_potions = [k for k, v in POTION_DATA.items() if v['type'] == 'bad']
            if not bad_potions:
                potion_file_name = 'potion_7.png'  # Fallback
            else:
                potion_file_name = random.choice(bad_potions)

        self.potion_file_name = potion_file_name

        # Primeiro tenta carregar a imagem específica solicitada
        try:
            image_loaded = False

            # Tenta achar a imagem em pastas diferentes
            base_paths = [
                os.path.join('assets', 'items', 'potions'),  
                os.path.join('..', '..', '..', 'assets', 'items', 'potions'),  
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'items', 'potions')
                # Caminho absoluto
            ]

            # Primeiro tenta carregar a poção que foi pedida
            for base_path in base_paths:
                try:
                    image_path = os.path.join(base_path, self.potion_file_name)
                    abs_path = os.path.abspath(image_path)
                    print(f"Tentando carregar poção específica: {abs_path}")

                    if os.path.exists(abs_path):
                        print(f"Arquivo encontrado em: {abs_path}")
                        original_image = pg.image.load(abs_path).convert_alpha()
                        self.image = pg.transform.scale(original_image, (40, 40))
                        print(f"Imagem do perigo carregada: {self.potion_file_name}")
                        image_loaded = True
                        break
                    else:
                        print(f"Arquivo não encontrado em: {abs_path}")
                except Exception as e:
                    print(f"Erro ao carregar {self.potion_file_name}: {e}")

            # Se não achou a poção certa, tenta qualquer uma ruim
            if not image_loaded:
                print("Tentando carregar qualquer poção ruim disponível...")
                bad_potions_files = [k for k, v in POTION_DATA.items() if v['type'] == 'bad']

                for base_path in base_paths:
                    if image_loaded:
                        break

                    for potion_file in bad_potions_files:
                        try:
                            image_path = os.path.join(base_path, potion_file)
                            abs_path = os.path.abspath(image_path)
                            print(f"Tentando carregar: {abs_path}")

                            if os.path.exists(abs_path):
                                print(f"Arquivo encontrado em: {abs_path}")
                                original_image = pg.image.load(abs_path).convert_alpha()
                                self.image = pg.transform.scale(original_image, (40, 40))
                                self.potion_file_name = potion_file  # Atualiza o nome
                                print(f"Imagem do perigo carregada: {potion_file}")
                                image_loaded = True
                                break
                            else:
                                print(f"Arquivo não encontrado em: {abs_path}")
                        except Exception as e:
                            print(f"Erro ao carregar {potion_file}: {e}")

            if not image_loaded:
                raise FileNotFoundError("Nenhuma imagem de perigo encontrada")

        except Exception as e:
            print(f"Erro ao carregar imagem do perigo: {e}")
            print("Usando placeholder...")
            # Se não achou nenhuma imagem, cria um quadrado vermelho como fallback
            self.image = pg.Surface((40, 40), pg.SRCALPHA)
            pg.draw.line(self.image, (255, 0, 0), (5, 5), (35, 35), 4)  # Linha diagonal 1
            pg.draw.line(self.image, (255, 0, 0), (35, 5), (5, 35), 4)  # Linha diagonal 2

        # Chama o __init__ da classe mãe (Item), que já configura a posição corretamente
        super().__init__(self.image)
        
        # Adiciona borda vermelha para itens perigosos
        self._add_colored_border(settings.RED, 3)
        
        self.damage = 1  # Quantidade de dano que este item causa

        # NÃO sobrescreva as posições aqui - deixe o base_item.py cuidar disso
        print(f"Hazard criado: {self.potion_file_name} na posição: ({self.rect.x}, {self.rect.y})")
        print("--- Fim do Hazard.__init__ ---\n")

    def on_collect(self, player):
        """
        Chamado quando o jogador pega este item perigoso.
        
        Args:
            player: Referência ao jogador que pegou o item
            
        Returns:
            int: Pontos perdidos (número negativo)
        """
        print(f"Perigo coletado: {self.potion_file_name}! O jogador sofreu {self.damage} de dano!")

        # Marca como pego e tira da tela
        self.collected = True
        self.kill()  # Remove o item do grupo de sprites

        # Retorna pontos negativos (o jogador perde pontos)
        return -5
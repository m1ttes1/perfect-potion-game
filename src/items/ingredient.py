import pygame as pg
import os
import random
from .base_item import Item
from src import settings
from src.data.potions import POTION_DATA


class Ingredient(Item):
    """
    Item que o jogador deve coletar para fazer poções.
    Aparece como uma poção colorida e dá pontos quando pego.
    """

    def __init__(self, game=None, potion_file_name=None):
        """
        Cria um novo ingrediente na tela.
        
        Args:
            game: Referência para o jogo principal (opcional)
            potion_file_name: Nome do arquivo da poção (se não informado, pega uma aleatória)
        """
        print("\n--- Iniciando Ingredient.__init__ ---")

        # Se não informou uma poção específica, pega uma aleatória das boas
        if potion_file_name is None:
            good_potions = [k for k, v in POTION_DATA.items() if v['type'] == 'good']
            if not good_potions:
                potion_file_name = 'potion_1.png'  # Fallback
            else:
                potion_file_name = random.choice(good_potions)

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
                        print(f"Imagem do ingrediente carregada: {self.potion_file_name}")
                        image_loaded = True
                        break
                    else:
                        print(f"Arquivo não encontrado em: {abs_path}")
                except Exception as e:
                    print(f"Erro ao carregar {self.potion_file_name}: {e}")

            # Se não achou a poção certa, tenta qualquer uma boa
            if not image_loaded:
                print("Tentando carregar qualquer poção boa disponível...")
                good_potions_files = [k for k, v in POTION_DATA.items() if v['type'] == 'good']

                for base_path in base_paths:
                    if image_loaded:
                        break

                    for potion_file in good_potions_files:
                        try:
                            image_path = os.path.join(base_path, potion_file)
                            abs_path = os.path.abspath(image_path)
                            print(f"Tentando carregar: {abs_path}")

                            if os.path.exists(abs_path):
                                print(f"Arquivo encontrado em: {abs_path}")
                                original_image = pg.image.load(abs_path).convert_alpha()
                                self.image = pg.transform.scale(original_image, (40, 40))
                                self.potion_file_name = potion_file  # Atualiza o nome
                                print(f"Imagem do ingrediente carregada: {potion_file}")
                                image_loaded = True
                                break
                            else:
                                print(f"Arquivo não encontrado em: {abs_path}")
                        except Exception as e:
                            print(f"Erro ao carregar {potion_file}: {e}")

            if not image_loaded:
                raise FileNotFoundError("Nenhuma imagem de ingrediente encontrada")

        except Exception as e:
            print(f"Erro ao carregar imagem do ingrediente: {e}")
            print("Usando placeholder...")
            # Se não achou nenhuma imagem, cria um círculo verde como fallback
            self.image = pg.Surface((40, 40), pg.SRCALPHA)
            pg.draw.circle(self.image, (0, 255, 0), (20, 20), 18)  # Círculo verde
            pg.draw.circle(self.image, (0, 200, 0), (20, 20), 15)  # Círculo verde mais escuro dentro

        # Chama o __init__ da classe mãe (Item), que já configura a posição corretamente
        super().__init__(self.image)

        # Borda verde para mostrar que é um item bom
        self._add_colored_border(settings.GREEN, 3)

        # Configura o tipo e efeito do ingrediente
        self.type = "good"
        self.effect = "restores health"

        # NÃO sobrescreva as posições aqui - deixe o base_item.py cuidar disso
        print(f"Ingredient criado: {self.potion_file_name} na posição: ({self.rect.x}, {self.rect.y})")
        print("--- Fim do Ingredient.__init__ ---\n")

    def on_collect(self, player):
        """
        Chamado quando o jogador pega este ingrediente.
        
        Args:
            player: Referência ao jogador que pegou o item
            
        Returns:
            int: Pontos ganhos (número positivo)
        """
        print(f"Ingrediente coletado: {self.potion_file_name}! Jogador ganhou pontos!")

        # Marca como pego e tira da tela
        self.collected = True
        self.kill()  # Remove o item do grupo de sprites

        return 10  # Retorna pontuação positiva
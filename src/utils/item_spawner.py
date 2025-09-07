import pygame as pg
import random
from src.items.ingredient import Ingredient
from src.items.hazard import Hazard
from src.items.bomb import Bomb
from src import settings
from src.data.potions import POTION_DATA  # ← IMPORTAÇÃO ADICIONADA


class ItemSpawner:
    """
    Responsável por gerar itens aleatórios no jogo
    (ingredientes, perigos, bombas) dentro da área de spawn definida.
    """

    def __init__(self, game):
        self.game = game
        self.last_spawn_time = 0  # Controla o tempo do último spawn
        self.spawn_delay = 2000   # 2 segundos entre spawns (em ms)

    def spawn_item(self):
        """
        Cria múltiplos itens aleatórios de uma vez, baseado nas configurações.
        Gera entre 2 a 4 itens por chamada para um jogo mais dinâmico.
        """
        current_time = pg.time.get_ticks()
        
        # Verifica se já passou tempo suficiente desde o último spawn
        if current_time - self.last_spawn_time < self.spawn_delay:
            return
            
        # Atualiza o tempo do último spawn
        self.last_spawn_time = current_time
        
        # Gera entre 2 a 4 itens por chamada
        num_items = random.randint(2, 4)
        
        # Prepara a lista de tipos de itens baseado nos pesos
        item_types = []
        for item_type, weight in settings.ITEM_SPAWN_WEIGHTS.items():
            item_types.extend([item_type] * weight)

        # Tenta criar até num_items itens, respeitando o limite máximo
        for _ in range(num_items):
            # Verifica se ainda pode adicionar mais itens
            if len(self.game.items) >= settings.MAX_ITEMS_ON_SCREEN:
                break
                
            chosen_type = random.choice(item_types)
            new_item = None
            
            try:
                if chosen_type == 'ingredient':
                    # Filtra poções boas do POTION_DATA
                    good_potions = [k for k, v in POTION_DATA.items() if v['type'] == 'good']
                    if good_potions:
                        chosen_potion = random.choice(good_potions)
                        new_item = Ingredient(self.game, chosen_potion)
                    else:
                        new_item = Ingredient(self.game)  # Fallback

                elif chosen_type == 'hazard':
                    # Filtra poções ruins do POTION_DATA
                    bad_potions = [k for k, v in POTION_DATA.items() if v['type'] == 'bad']
                    if bad_potions:
                        chosen_potion = random.choice(bad_potions)
                        new_item = Hazard(self.game, chosen_potion)
                    else:
                        new_item = Hazard(self.game)  # Fallback

                elif chosen_type == 'bomb':
                    new_item = Bomb(self.game)

                if new_item:
                    # --- Configura a posição dentro da área de spawn ---
                    # Escolhe de qual lado o item vai aparecer (esquerda ou direita)
                    spawn_side = random.choice(['left', 'right'])
                    
                    # Adiciona variação na posição horizontal para evitar sobreposição
                    x_offset = random.randint(0, 50)
                    
                    if spawn_side == 'left':
                        # Aparece do lado esquerdo, se move para a direita
                        new_item.rect.x = settings.SPAWN_AREA_X - new_item.rect.width - x_offset
                        new_item.speed_x = random.randrange(settings.ITEM_SPEED_MIN, settings.ITEM_SPEED_MAX)
                    else:
                        # Aparece do lado direito, se move para a esquerda
                        new_item.rect.x = settings.SPAWN_AREA_X + settings.SPAWN_AREA_WIDTH + x_offset
                        new_item.speed_x = -random.randrange(settings.ITEM_SPEED_MIN, settings.ITEM_SPEED_MAX)

                    # Define a posição Y para aparecer apenas abaixo da área do jogador (390px)
                    # Adiciona mais variação na posição vertical
                    min_y = settings.ARENA_FLOOR_Y + 10  # 10px abaixo do chão da arena
                    max_y = settings.WINDOW_HEIGHT - new_item.rect.height - 10  # 10px de margem do fundo
                    
                    # Garante que max_y não seja menor que min_y
                    if max_y < min_y:
                        max_y = min_y
                        
                    # Se ainda assim estiver acima da área permitida, força para o mínimo
                    if min_y < settings.ARENA_FLOOR_Y:
                        min_y = settings.ARENA_FLOOR_Y
                        
                    # Distribui os itens verticalmente para evitar sobreposição
                    vertical_step = (max_y - min_y) / num_items
                    base_y = min_y + vertical_step * _
                    new_item.rect.y = int(random.uniform(base_y, min(base_y + vertical_step, max_y)))

                    # Adiciona um pouco de variação na velocidade para criar mais dinâmica
                    if random.random() > 0.5:  # 50% de chance de ajustar a velocidade
                        new_item.speed_x *= random.uniform(0.8, 1.2)

                    # Adiciona aos grupos
                    self.game.all_sprites.add(new_item)
                    self.game.items.add(new_item)

                    if settings.DEBUG:
                        item_name = getattr(new_item, 'potion_file_name', chosen_type)
                        print(f"Item criado: {chosen_type} ({item_name}) na posição ({new_item.rect.x}, {new_item.rect.y})")

            except Exception as e:
                print(f"Erro ao criar item {chosen_type}: {e}")

    def cleanup_off_screen_items(self):
        """
        Remove itens que saíram completamente da tela.

        Se não vai ficando muito pesado e acaba travando
        """
        margin = 100  # Margem além da tela para garantir que o item saiu completamente

        for item in list(self.game.items):  # Cria uma cópia da lista para iteração segura
            if (item.rect.right < -margin or
                    item.rect.left > self.game.WINDOW_WIDTH + margin or
                    item.rect.bottom < -margin or
                    item.rect.top > self.game.WINDOW_HEIGHT + margin):

                # Remove o item de todos os grupos
                item.kill()

                # Debug opcional
                if settings.DEBUG:
                    print(f"Item removido por sair da tela: {type(item).__name__}")
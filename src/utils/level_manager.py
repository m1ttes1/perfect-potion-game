import random
from typing import List, Dict, Tuple, Optional
import pygame as pg
from src.data.potions import good_potions, POTION_DATA

class LevelManager:
    """
    Gerencia as fases do jogo, implementando as regras de progressão:
    - Nível 1: Receitas com 2 ingredientes, 3 vidas
    - Nível 5: Receitas com 3 ingredientes
    - Nível 10: Receitas com 4 ingredientes
    - Erros só são contados quando o jogador pega um item fora de ordem
    - A cada nível, a velocidade dos itens aumenta
    """
    
    def __init__(self):
        self.current_level = 1
        self.required_potions: List[str] = []
        self.collected_potions: List[str] = []
        self.level_complete = False
        self.font = pg.font.Font(None, 30)
        self.base_speed = 1.0  # Velocidade base dos itens que caem
        self.level_speed_increase = 0.1  # Aumento de velocidade por nível
        
    def get_recipe_length(self, level: int) -> int:
        """Retorna o número de ingredientes necessários para o nível atual."""
        if level >= 10:
            return 4
        elif level >= 5:
            return 3
        else:
            return 2
            
    def get_fall_speed(self) -> float:
        """Retorna a velocidade de queda dos itens para o nível atual."""
        return self.base_speed + (self.current_level - 1) * self.level_speed_increase
    
    def generate_level_requirements(self, level: int) -> List[str]:
        """
        Gera uma lista de poções necessárias para completar o nível.
        """
        num_potions = self.get_recipe_length(level)
        
        # Usa todas as poções disponíveis
        available_potions = good_potions.copy()
        
        # Se não houver poções suficientes, repete algumas
        if len(available_potions) < num_potions:
            available_potions = available_potions * (num_potions // len(available_potions) + 1)
        
        # Escolhe poções aleatórias sem repetição
        required = random.sample(available_potions, min(num_potions, len(available_potions)))
        
        return required
    
    def start_level(self, level: int):
        """
        Inicia um novo nível com uma nova sequência de poções.
        """
        self.current_level = level
        self.required_potions = self.generate_level_requirements(level)
        self.collected_potions = []
        self.level_complete = False
        
        print(f"[NÍVEL {level}] Iniciando com {len(self.required_potions)} ingredientes")
        print(f"[NÍVEL {level}] Velocidade: {self.get_fall_speed():.1f}x")
    
    def register_potion_collected(self, potion_name: str) -> Tuple[bool, bool]:
        """
        Registra uma poção coletada e verifica se está na ordem correta.
        
        Retorna:
            (acertou, level_complete)
            - acertou: True se a poção está na ordem correta
            - level_complete: True se o nível foi completado
        """
        if self.level_complete or not self.required_potions:
            return False, False
            
        # Verifica se é a próxima poção correta
        next_required = self.required_potions[len(self.collected_potions)]
        
        if potion_name == next_required:
            # Acertou na ordem correta
            self.collected_potions.append(potion_name)
            
            # Verifica se completou o nível
            if len(self.collected_potions) == len(self.required_potions):
                self.level_complete = True
                return True, True  # Nível completo sem falha
                
            return True, False  # Item correto, mas nível não completo
        else:
            # Errou a ordem - apenas retorna que houve falha sem afetar vidas
            print("[ERRO] Ordem incorreta! Tente novamente.")
            return False, False
    
    def get_level_progress(self) -> Tuple[int, int]:
        """Retorna (poções coletadas, total de poções necessárias)."""
        return len(self.collected_potions), len(self.required_potions)
    
    # Removido métodos de gerenciamento de vidas, pois isso é responsabilidade do jogador
    
    def draw_requirements(self, screen, x: int, y: int):
        """Desenha os requisitos do nível na tela."""
        # Título
        title = self.font.render(f"Nível {self.current_level}", True, (255, 255, 255))
        screen.blit(title, (x, y))
        
        # O contador de vidas foi movido para o HUD do jogador
        
        # Poções necessárias
        for i, potion in enumerate(self.required_potions):
            color = (0, 255, 0) if i < len(self.collected_potions) else (255, 255, 255)
            potion_name = POTION_DATA.get(potion, {}).get('effect', f'Poção {i+1}')
            text = self.font.render(f"{i+1}. {potion_name}", True, color)
            screen.blit(text, (x, y + 70 + i * 25))

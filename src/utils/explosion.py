import pygame as pg
from src import settings

class Explosion:
    """
    Gerencia explosões no jogo:
    visual + efeito sonoro(tentei) + impacto nos itens.
    """

    def __init__(self, game, position, radius):
        self.game = game
        self.position = position
        self.radius = radius

    def explode(self):
        """
        Executa a explosão:
        - afeta itens próximos
        - cria efeito visual
        - toca som
        """
        self._damage_items()
        self._create_effect()
        self._play_sound()

    def _damage_items(self):
        """
        Verifica quais itens estão dentro do raio e aplica efeito.
        Ingredientes/Hazards/Bomb recebem score ou dano.
        """
        explosion_rect = pg.Rect(0, 0, self.radius*2, self.radius*2)
        explosion_rect.center = self.position
        affected_items = []

        for item in self.game.items:
            if explosion_rect.colliderect(item.rect):
                dx = item.rect.centerx - self.position[0]
                dy = item.rect.centery - self.position[1]
                distance = (dx*dx + dy*dy)**0.5
                affected_items.append((item, distance))

        affected_items.sort(key=lambda x: x[1])

        for item, distance in affected_items:
            if distance < self.radius:
                force = 1.0 - (distance/self.radius)

                if hasattr(item, 'on_explosion'):
                    item.on_explosion(force, self.position)

                if isinstance(item, settings.Ingredient):
                    self.game.add_score(settings.SCORE_INGREDIENT)
                    item.kill()
                elif isinstance(item, settings.Hazard):
                    self.game.add_score(settings.SCORE_HAZARD)
                    item.kill()
                elif hasattr(item, 'take_damage'):
                    item.take_damage(force*100)

    def _create_effect(self):
        """
        Desenha a explosão na tela com gradiente amarelo->vermelho.
        """
        size = self.radius * 2
        surf = pg.Surface((size, size), pg.SRCALPHA)
        for r in range(self.radius, 0, -2):
            alpha = int(200 * (r/self.radius))
            color = (255, int(255*(r/self.radius)), 0, alpha)
            pg.draw.circle(surf, color, (self.radius, self.radius), r, width=2)
        rect = surf.get_rect(center=self.position)
        self.game.screen.blit(surf, rect)
        pg.display.update(rect)

    def _play_sound(self):
        """
        Toca o som da explosão, se habilitado.
        """
        self.game._play_sound('explosion')

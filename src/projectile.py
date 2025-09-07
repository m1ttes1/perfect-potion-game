import pygame as pg
from src import settings
import os


class Projectile(pg.sprite.Sprite):
    # a classe que define um projétil direcional
    def __init__(self, pos, direction_vector):
        super().__init__()

        # carrega e redimensiona as imagens uma única vez
        self._load_images()

        # atributos de movimento
        self.pos = pg.math.Vector2(pos)
        self.direction = pg.math.Vector2(direction_vector).normalize()
        self.speed = 25

        # escolhe a imagem e o rect corretos para a direção inicial
        self._set_image_and_rect()

    def _load_images(self):
        # carrega e guarda todas as imagens de projétil necessárias
        base_path = os.path.join('assets', 'images', 'projectiles')
        projectile_width = 60

        # carrega a imagem original
        img_right_original = pg.image.load(os.path.join(base_path, '3.png')).convert_alpha()
        img_up_right_original = pg.image.load(os.path.join(base_path, '3_2.png')).convert_alpha()

        # redimensiona a imagem 'direita'
        w, h = img_right_original.get_size()
        h = int(projectile_width * (h / w))
        img_right = pg.transform.scale(img_right_original, (projectile_width, h))

        # redimensiona a imagem 'diagonal'
        w, h = img_up_right_original.get_size()
        h = int(projectile_width * (h / w))
        img_up_right = pg.transform.scale(img_up_right_original, (projectile_width, h))

        # guarda todas as 8 direções já redimensionadas
        self.images = {
            'right': img_right,
            'left': pg.transform.flip(img_right, True, False),
            'up': pg.transform.rotate(img_right, 90),
            'down': pg.transform.rotate(img_right, -90),
            'up_right': img_up_right,
            'up_left': pg.transform.flip(img_up_right, True, False),
            'down_right': pg.transform.rotate(img_up_right, -90),
            'down_left': pg.transform.rotate(pg.transform.flip(img_up_right, True, False), 90)
        }

    def _set_image_and_rect(self):
        # escolhe a imagem correta baseado no vetor de direção
        angle = self.direction.angle_to(pg.math.Vector2(1, 0))

        if -22.5 <= angle < 22.5:
            self.image = self.images['right']
        elif 22.5 <= angle < 67.5:
            self.image = self.images['down_right']
        elif 67.5 <= angle < 112.5:
            self.image = self.images['down']
        elif 112.5 <= angle < 157.5:
            self.image = self.images['down_left']
        elif angle >= 157.5 or angle < -157.5:
            self.image = self.images['left']
        elif -157.5 <= angle < -112.5:
            self.image = self.images['up_left']
        elif -112.5 <= angle < -67.5:
            self.image = self.images['up']
        elif -67.5 <= angle < -22.5:
            self.image = self.images['up_right']

        # cria o rect com a imagem correta
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, *args, **kwargs):

        # move o projétil baseado no vetor de direção
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        # remove o projétil se ele sair completamente da tela
        if not self.rect.colliderect(pg.Rect(0, 0, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)):
            self.kill()
# Função utilitária para carregar animações do jogo

import pygame as pg
import os

def load_animation_frames(base_path, folder_name, frame_count, scale_size):
    # Carrega uma sequência de frames de animação de uma pasta
    # Retorna uma lista de superfícies do Pygame já redimensionadas

    frames = []  # Lista que vai armazenar todos os frames carregados
    animation_path = os.path.join(base_path, folder_name)  # Caminho completo da pasta da animação

    # Definindo largura alvo para redimensionamento e mantendo proporção
    target_width, _ = scale_size  # só precisamos da largura para calcular altura proporcional

    for i in range(frame_count):
        # Gera nomes de arquivos como '0_Dark_Oracle_<folder_name>_000.png', '..._001.png', etc.
        filename_prefix = f'0_Dark_Oracle_{folder_name}_'
        filename = f'{filename_prefix}{i:03}.png'  # número com 3 dígitos
        img_path = os.path.join(animation_path, filename)  # caminho completo do arquivo

        try:
            # Carrega a imagem com transparência
            img = pg.image.load(img_path).convert_alpha()

            # Redimensiona mantendo proporção
            original_width, original_height = img.get_size()
            aspect_ratio = original_height / original_width
            target_height = int(target_width * aspect_ratio)

            # Adiciona o frame redimensionado à lista
            frames.append(pg.transform.scale(img, (target_width, target_height)))
        except pg.error:
            # Se não conseguir carregar, mostra aviso e continua
            print(f"Warning: Could not load image {img_path}")

    return frames  # Retorna todos os frames carregados

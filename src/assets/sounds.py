"""
Módulo de sons do jogo Perfect Potion.
Aqui tentei implementar uma interface para carregar e reproduzir efeitos sonoros.
"""
import os
import pygame as pg

# Dicionário para armazenar os sons carregados
sounds = {}

def load_sounds():
    """Carrega todos os efeitos sonoros do jogo."""
    try:
        # Inicializa o mixer de som do pygame
        pg.mixer.init()
        
        # Caminho para a pasta de sons
        sounds_dir = os.path.join('assets', 'sounds')
        
        # Verifica se a pasta de sons existe
        if not os.path.exists(sounds_dir):
            print(f"Aviso: Pasta de sons não encontrada em {sounds_dir}")
            return False
        
        # Carrega os sons (implemente conforme necessário)
        # Exemplo:
        # sounds['explosion'] = pg.mixer.Sound(os.path.join(sounds_dir, 'explosion.wav'))
        
        return True
    except Exception as e:
        print(f"Erro ao carregar sons: {e}")
        return False

# Inicializa os sons quando o módulo é importado
load_sounds()

def play_sound(sound_name, volume=0.5):
    """
    Reproduz um som do dicionário de sons.
    
    Args:
        sound_name (str): Nome do som a ser reproduzido
        volume (float): Volume do som (0.0 a 1.0)
    """
    if sound_name in sounds:
        try:
            sound = sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            print(f"Erro ao reproduzir som {sound_name}: {e}")
    else:
        print(f"Aviso: Som '{sound_name}' não encontrado")

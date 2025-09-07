# entrada principal do jogo. A sua única função é iniciar o jogo.
import sys
import os
import warnings

# Suprime avisos do pkg_resources
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

# Adiciona a pasta 'src' ao caminho de procura do Python
# Isto garante que os módulos dentro de 'src' possam ser importados em qualquer lugar
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(src_path))

# Agora que o caminho está configurado, podemos importar a classe Game
from src.game import Game

# Bloco principal que só executa quando este ficheiro é corrido diretamente
if __name__ == '__main__':
    try:
        game = Game()
        game.run()
    except Exception as e:
        # Se ocorrer um erro inesperado, imprime-o antes de fechar
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
        raise
    finally:
        # Garante que o Pygame seja encerrado corretamente
        import pygame as pg
        pg.quit()
        sys.exit()
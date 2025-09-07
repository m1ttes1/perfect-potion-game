# src/utils/gui_elements.py
import pygame as pg


def load_and_cut_sprite_sheet(sheet_path, x, y, width, height, scale=1):
    """
    Carrega um sprite sheet e recorta uma imagem específica.

    Args:
        sheet_path (str): Caminho para o ficheiro do sprite sheet.
        x (int): Coordenada X do canto superior esquerdo da imagem a recortar.
        y (int): Coordenada Y do canto superior esquerdo da imagem a recortar.
        width (int): Largura da imagem a recortar.
        height (int): Altura da imagem a recortar.
        scale (float): Fator de escala para a imagem recortada.

    Returns:
        pygame.Surface: A imagem recortada e escalada, ou None se houver erro.
    """
    try:
        sheet = pg.image.load(sheet_path).convert_alpha()

        # Cria uma nova superfície com o tamanho da imagem a recortar
        image = pg.Surface((width, height), pg.SRCALPHA, 32)

        # Copia a parte desejada do sprite sheet para a nova superfície
        image.blit(sheet, (0, 0), (x, y, width, height))

        # Escala a imagem, se um fator de escala for fornecido
        if scale != 1:
            image = pg.transform.scale(image, (int(width * scale), int(height * scale)))

        return image
    except pg.error as e:
        print(f"Erro ao carregar ou recortar sprite do sheet {sheet_path}: {e}")
        return None


# Exemplos de uso (remova depois de testar)
if __name__ == '__main__':
    # Inicializa o Pygame apenas para testar
    pg.init()
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("Teste de Sprite Sheet")

    # Caminho para o seu sprite sheet (ajuste se necessário)
    sprite_sheet_path = os.path.join('assets', 'images', 'gui', 'MediavelFree.png')

    # Exemplo: recortar o painel de madeira (ajustar as coordenadas reais)
    # Estas são coordenadas e tamanhos *aproximados* que vamos precisar de ajustar!
    # Olhe para o seu sprite sheet e conte os pixels.
    panel_x = 0
    panel_y = 0
    panel_width = 128
    panel_height = 80

    # Recorta o painel e escala-o
    wooden_panel = load_and_cut_sprite_sheet(sprite_sheet_path, panel_x, panel_y, panel_width, panel_height, scale=2)

    if wooden_panel:
        print("Painel de madeira carregado com sucesso!")
        screen.blit(wooden_panel, (100, 100))
        pg.display.flip()
        pg.time.wait(3000)  # Espera 3 segundos
    else:
        print("Falha ao carregar o painel.")

    pg.quit()
    sys.exit()
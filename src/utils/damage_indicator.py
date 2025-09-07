import pygame as pg

class DamageIndicator:
    """
    Exibe indicadores de dano flutuantes quando o jogador é atingido.
    """
    
    def __init__(self, text, position, color=(255, 50, 50), font_size=24, duration=1000):
        """
        Inicializa o indicador de dano.
        
        Args:
            text: Texto a ser exibido (ex: "-10")
            position: Tupla (x, y) da posição inicial
            color: Cor do texto no formato RGB
            font_size: Tamanho da fonte
            duration: Duração da animação em milissegundos
        """
        self.text = str(text)
        self.x, self.y = position
        self.color = color
        self.font = pg.font.Font(None, font_size)
        self.start_time = pg.time.get_ticks()
        self.duration = duration
        self.velocity = -1  # Velocidade de subida
        self.alpha = 255  # Para efeito de fade out
        
    def update(self):
        """Atualiza a posição e o estado do indicador."""
        # Move para cima
        self.y += self.velocity
        
        # Diminui a velocidade gradualmente
        if self.velocity < 0.5:
            self.velocity += 0.1
            
        # Efeito de fade out
        if self.get_elapsed_time() > self.duration / 2:
            self.alpha = max(0, 255 - ((self.get_elapsed_time() - (self.duration / 2)) / (self.duration / 2) * 255))
    
    def draw(self, surface):
        """Desenha o indicador na superfície fornecida."""
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(int(self.alpha))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        surface.blit(text_surface, text_rect)
    
    def is_expired(self):
        """Retorna True se o indicador deve ser removido."""
        return self.get_elapsed_time() >= self.duration
    
    def get_elapsed_time(self):
        """Retorna o tempo decorrido desde a criação do indicador em milissegundos."""
        return pg.time.get_ticks() - self.start_time

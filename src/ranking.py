"""
Módulo ranking - Gerencia o sistema de ranking do jogo.
"""
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from src import settings

class Ranking:
    """
    Classe que gerencia o ranking do jogo.
    Responsável por carregar, salvar e atualizar as pontuações.
    """

    def __init__(self):
        """
        Inicializa o sistema de ranking.
        Carrega o ranking do arquivo ou cria um novo se não existir.
        """
        self.ranking_file = os.path.join(settings.SAVE_DIR, settings.RANKING_FILE)
        self.ranking = self._load_ranking()

    def _load_ranking(self) -> List[Dict[str, Any]]:
        """
        Carrega o ranking do arquivo JSON.
        Se o arquivo não existir ou estiver corrompido, cria uma lista vazia.

        Returns:
            List[Dict[str, Any]]: Lista de entradas do ranking.
        """
        try:
            os.makedirs(settings.SAVE_DIR, exist_ok=True)
            if os.path.exists(self.ranking_file):
                with open(self.ranking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar ranking: {e}")
        return []

    def save_ranking(self) -> bool:
        """
        Salva o ranking no arquivo JSON.

        Returns:
            bool: True se o salvamento foi bem-sucedido, False se houve erro.
        """
        try:
            with open(self.ranking_file, 'w', encoding='utf-8') as f:
                json.dump(self.ranking, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"Erro ao salvar ranking: {e}")
            return False

    def add_score(self, player_name: str, score: int, game_time: float) -> None:
        """
        Adiciona uma nova pontuação ao ranking.
        Ordena o ranking e mantém apenas os melhores resultados.

        Args:
            player_name (str): Nome do jogador.
            score (int): Pontuação obtida.
            game_time (float): Tempo de jogo em segundos.
        """
        entry = {
            'player': player_name,
            'score': score,
            'time': game_time,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': time.time()
        }

        self.ranking.append(entry)
        # Ordena por pontuação (decrescente) e tempo (crescente)
        self.ranking.sort(key=lambda x: (-x['score'], x['time']))
        # Mantém apenas as melhores pontuações definidas em settings
        self.ranking = self.ranking[:settings.MAX_RANKING_ENTRIES]
        self.save_ranking()

    def get_ranking(self) -> List[Dict[str, Any]]:
        """
        Retorna o ranking completo.

        Returns:
            List[Dict[str, Any]]: Lista de todas as entradas do ranking.
        """
        return self.ranking

    def get_top_scores(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna as N melhores pontuações.

        Args:
            n (int): Quantidade de melhores pontuações a retornar.

        Returns:
            List[Dict[str, Any]]: Lista das N melhores entradas.
        """
        return self.ranking[:min(n, len(self.ranking))]

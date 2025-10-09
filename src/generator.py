"""Generador de estados resolubles para el juego Water Sort Puzzle."""

from __future__ import annotations

from typing import Optional

from .water_sort_game import GameState, WaterSortGame


class PuzzleGenerator:
    """Generador responsable de construir estados iniciales resolubles."""

    def __init__(self, game: WaterSortGame) -> None:
        """Inicializa el generador con la referencia al juego."""
        self.game: WaterSortGame = game

    def generate(self, seed: Optional[int] = None) -> GameState:
        """Produce un estado inicial resoluble para el puzzle."""
        raise NotImplementedError("Implementar generador de puzzles resolubles")


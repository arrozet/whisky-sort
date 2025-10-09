"""Interfaz gráfica para visualizar la resolución de Water Sort Puzzle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .water_sort_game import GameState, Move


@dataclass(frozen=True)
class VisualizationConfig:
    """Configuración para ajustar la visualización gráfica."""

    width: int
    height: int
    background_color: tuple[int, int, int]
    tube_color: tuple[int, int, int]
    frame_delay: float


class PuzzleVisualizer:
    """Visualiza el proceso de resolución del puzzle paso a paso."""

    def __init__(self, config: VisualizationConfig) -> None:
        """Inicializa el visualizador con los parámetros establecidos."""
        self.config: VisualizationConfig = config

    def setup(self) -> None:
        """Configura los recursos necesarios para la visualización."""
        raise NotImplementedError("Implementar preparación de la interfaz gráfica")

    def render_state(self, state: GameState) -> None:
        """Renderiza un estado específico del puzzle."""
        raise NotImplementedError("Implementar dibujado de tubos y colores")

    def play_solution(self, initial_state: GameState, moves: Sequence[Move]) -> None:
        """Reproduce la secuencia de movimientos que resuelve el puzzle."""
        raise NotImplementedError("Implementar reproducción animada de la solución")


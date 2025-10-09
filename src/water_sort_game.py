"""Definición de la lógica principal del juego Water Sort Puzzle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple


TubeState = Tuple[str, ...]
GameState = Tuple[TubeState, ...]


@dataclass(frozen=True)
class Move:
    """Representa un movimiento entre dos tubos."""

    source: int
    target: int


class WaterSortGame:
    """Clase que encapsula la lógica y las reglas del juego Water Sort Puzzle."""

    def __init__(self, num_tubes: int, num_colors: int, seed: Optional[int] = None) -> None:
        """Configura los parámetros del juego y prepara el estado inicial."""
        self.num_tubes: int = num_tubes
        self.num_colors: int = num_colors
        self.seed: Optional[int] = seed
        self.tube_capacity: int = 4
        # Comentario: Aquí se inicializarán los generadores y estructuras auxiliares.

    def get_initial_state(self) -> GameState:
        """Genera un estado inicial aleatorio pero resoluble."""
        raise NotImplementedError("Implementar generación de estado inicial")

    def get_valid_moves(self, state: GameState) -> Sequence[Move]:
        """Calcula todos los movimientos válidos disponibles para un estado dado."""
        raise NotImplementedError("Implementar cálculo de movimientos válidos")

    def apply_move(self, state: GameState, move: Move) -> GameState:
        """Aplica un movimiento sobre un estado y devuelve el nuevo estado resultante."""
        raise NotImplementedError("Implementar transición de estado tras un movimiento")

    def is_goal_state(self, state: GameState) -> bool:
        """Verifica si el estado proporcionado es un estado objetivo válido."""
        raise NotImplementedError("Implementar verificación de estado objetivo")

    def is_valid_state(self, state: GameState) -> bool:
        """Determina si un estado cumple con las restricciones básicas del juego."""
        raise NotImplementedError("Implementar validación estructural del estado")

    def iterate_colors(self, state: GameState) -> Iterable[str]:
        """Itera sobre todas las unidades de color presentes en un estado."""
        raise NotImplementedError("Implementar iteración de colores por estado")


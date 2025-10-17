"""Generador de estados resolubles para el juego Water Sort Puzzle."""

from __future__ import annotations

import random
from typing import Optional

from .water_sort_game import GameState, TubeState, WaterSortGame


class PuzzleGenerator:
    """Generador responsable de construir estados iniciales resolubles."""

    def __init__(self, game: WaterSortGame) -> None:
        """Inicializa el generador con la referencia al juego."""
        self.game: WaterSortGame = game

    def generate(self, seed: Optional[int] = None) -> GameState:
        """Produce un estado inicial resoluble para el puzzle.

        Genera un estado meta (tubos uniformes y vacíos restantes) y aplica
        una secuencia de movimientos aleatorios válidos para desordenarlo.
        Al derivar el estado a partir de uno objetivo mediante movimientos
        válidos, se garantiza la resolubilidad (basta con invertir la secuencia).

        Args:
            seed: Semilla opcional para el generador aleatorio determinista.

        Returns:
            Estado inicial resoluble como tupla inmutable de tuplas (tope en índice 0).
        """
        rng = random.Random(seed)
        extra_tubes: int = self.game.num_tubes - self.game.num_colors
        if extra_tubes < 0:
            raise ValueError("El número de tubos no puede ser menor que la cantidad de colores")

        required_empty: int = extra_tubes
        max_attempts: int = 512

        attempt: int = 0
        while attempt < max_attempts:
            attempt += 1
            state: GameState = self._build_random_state(rng, required_empty)

            if self.game.is_goal_state(state):
                continue

            if self._count_empty_tubes(state) != required_empty:
                continue

            if not self._has_mixed_tube(state):
                continue

            if not self.game.is_valid_state(state):
                continue

            if self._is_state_solvable(state):
                return state

        raise RuntimeError("No se pudo generar un estado resoluble tras múltiples intentos")

    def _build_random_state(self, rng: random.Random, empty_tubes: int) -> GameState:
        """Construye un estado aleatorio distribuyendo equitativamente los colores."""
        palette: list[str] = []

        for color in self._iterate_color_labels():
            palette.extend([color] * self.game.tube_capacity)

        rng.shuffle(palette)

        filled_tubes = self.game.num_tubes - empty_tubes
        tubes: list[TubeState] = []

        index: int = 0
        for _ in range(filled_tubes):
            slice_end = index + self.game.tube_capacity
            segment = tuple(palette[index:slice_end])
            tubes.append(segment)
            index = slice_end

        for _ in range(empty_tubes):
            tubes.append(tuple())

        rng.shuffle(tubes)
        return tuple(tubes)

    def _iterate_color_labels(self) -> list[str]:
        """Genera las etiquetas utilizadas para representar cada color."""
        return [f"C{index}" for index in range(self.game.num_colors)]

    def _count_empty_tubes(self, state: GameState) -> int:
        """Cuenta cuántos tubos están completamente vacíos en el estado."""
        return sum(1 for tube in state if not tube)

    def _has_mixed_tube(self, state: GameState) -> bool:
        """Indica si existe al menos un tubo con más de un color distinto."""
        for tube in state:
            if len(tube) > 1 and len(set(tube)) > 1:
                return True
        return False

    def _is_state_solvable(self, state: GameState) -> bool:
        """Valida mediante una búsqueda BFS que el estado sea resoluble."""
        from .search_solver import SearchResult, SearchSolver

        solver = SearchSolver(self.game)
        result: SearchResult = solver.bfs(state)
        return result.solution_depth >= 0
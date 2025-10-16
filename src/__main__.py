"""Punto de entrada principal para ejecutar el solver de Water Sort Puzzle."""

from __future__ import annotations

import argparse
from typing import Callable, Dict

from .generator import PuzzleGenerator
from .heuristics import heuristic3_blocks, heuristic1_color_entropy, heuristic2_completed_tubes
from .search_solver import SearchResult, SearchSolver
from .water_sort_game import WaterSortGame


def parse_arguments() -> argparse.Namespace:
    """Procesa los argumentos de la línea de comandos para configurar la ejecución."""
    raise NotImplementedError("Implementar parsing de argumentos de ejecución")


def build_solver(args: argparse.Namespace) -> SearchSolver:
    """Construye la instancia del solver basada en los argumentos proporcionados."""
    raise NotImplementedError("Implementar construcción de solver con configuraciones")


def run_solver(solver: SearchSolver, args: argparse.Namespace) -> SearchResult:
    """Ejecuta el solver y devuelve el resultado de la búsqueda."""
    raise NotImplementedError("Implementar ejecución de resolución del puzzle")


def main() -> None:
    game = WaterSortGame(num_tubes=6, num_colors=4, seed=42)
    generator = PuzzleGenerator(game)
    initial_state = generator.generate()

    # Verificar que es válido y NO es objetivo
    print(game.is_valid_state(initial_state))  # True
    print(game.is_goal_state(initial_state))   # False


if __name__ == "__main__":
    main()


"""Definiciones de heurísticas para el algoritmo de Water Sort Puzzle."""

from __future__ import annotations

from typing import Dict

from .water_sort_game import GameState


def heuristic_color_entropy(state: GameState) -> int:
    """Implementación de la heurística de entropía de colores."""
    raise NotImplementedError("Implementar cálculo de entropía de colores")


def heuristic_completed_tubes(state: GameState) -> int:
    """Implementación de la heurística basada en tubos completados."""
    raise NotImplementedError("Implementar evaluación de tubos completos")


def heuristic_blocks(state: GameState) -> int:
    """Implementación de la heurística basada en unidades bloqueadas."""
    raise NotImplementedError("Implementar conteo de unidades bloqueadas")


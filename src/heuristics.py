"""Definiciones de heurísticas para el algoritmo de Water Sort Puzzle."""

from __future__ import annotations

from typing import Dict

from .water_sort_game import GameState


def heuristic1_color_entropy(state: GameState) -> int:
    """Implementación de la heurística de entropía de colores.
    
    Penaliza la dispersión de colores en múltiples tubos.
    h₁(state) = Σᵢ (num_tubes_with_colorᵢ - 1) * dispersion_weightᵢ
    
    Args:
        state: Estado actual del juego (tupla de tubos).
    
    Returns:
        Valor heurístico que penaliza colores dispersos.
    """
    # Diccionario que mapea cada color a los tubos donde aparece (índice -> conteo)
    color_distribution: Dict[str, Dict[int, int]] = {}
    
    # Recorrer cada tubo y contar las unidades de cada color
    for tube_idx, tube in enumerate(state):
        for color in tube:
            if color not in color_distribution:
                color_distribution[color] = {}
            
            if tube_idx not in color_distribution[color]:
                color_distribution[color][tube_idx] = 0
            
            color_distribution[color][tube_idx] += 1
    
    heuristic_value: int = 0
    
    # Para cada color, calcular su contribución al valor heurístico
    for color, tube_counts in color_distribution.items():
        # Número de tubos que contienen este color
        num_tubes_with_color: int = len(tube_counts)
        
        # Si el color está en más de un tubo, penalizamos la dispersión
        if num_tubes_with_color > 1:
            # Encontrar el tubo "principal" (el que tiene más unidades de este color)
            max_count: int = max(tube_counts.values())
            
            # dispersion_weight = unidades que NO están en el tubo principal
            dispersion_weight: int = sum(tube_counts.values()) - max_count
            
            # Acumular penalización: (num_tubos - 1) * peso_dispersión
            heuristic_value += (num_tubes_with_color - 1) * dispersion_weight
    
    return heuristic_value


def heuristic2_completed_tubes(state: GameState) -> int:
    """Implementación de la heurística basada en tubos completados."""
    raise NotImplementedError("Implementar evaluación de tubos completos")


def heuristic3_blocks(state: GameState) -> int:
    """Implementación de la heurística basada en unidades bloqueadas."""
    raise NotImplementedError("Implementar conteo de unidades bloqueadas")


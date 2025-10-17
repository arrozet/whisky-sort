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
    """Implementación de la heurística basada en tubos completados.
    
    Recompensa tubos completados y penaliza colores mal ubicados.
    h₂(state) = (incomplete_tubes * 4) - well_placed_colors
    
    Args:
        state: Estado actual del juego (tupla de tubos).
    
    Returns:
        Valor heurístico que premia proximidad a la solución.
    """
    incomplete_tubes: int = 0
    well_placed_colors: int = 0
    
    # Analizar cada tubo del estado
    for tube in state:
        # Tubo vacío: no cuenta como incompleto
        if not tube:
            continue
        
        # Tubo lleno con un único color: completado (no cuenta como incompleto)
        if len(tube) == 4 and len(set(tube)) == 1:
            continue
        
        # Cualquier otro caso es un tubo incompleto
        incomplete_tubes += 1
        
        # Contar colores bien ubicados: unidades contiguas del mismo color desde el fondo
        if tube:
            # El color del fondo (última posición) es la referencia
            bottom_color: str = tube[-1]
            contiguous_count: int = 0
            
            # Recorrer desde el fondo hacia arriba contando colores iguales consecutivos
            for idx in range(len(tube) - 1, -1, -1):
                if tube[idx] == bottom_color:
                    contiguous_count += 1
                else:
                    # Encontramos un color diferente, paramos
                    break
            
            well_placed_colors += contiguous_count
    
    # Fórmula: penalización por tubos incompletos menos recompensa por colores bien ubicados
    return (incomplete_tubes * 4) - well_placed_colors


def heuristic3_blocks(state: GameState) -> int:
    """Implementación de la heurística basada en unidades bloqueadas.
    
    Penaliza tubos mezclados y unidades bloqueadas por colores distintos encima.
    h₃(state) = total_mixed_units + (2 * blocked_units)
    
    Args:
        state: Estado actual del juego (tupla de tubos).
    
    Returns:
        Valor heurístico que penaliza mezclas y bloqueos.
    """
    total_mixed_units: int = 0
    blocked_units: int = 0
    
    # Analizar cada tubo del estado
    for tube in state:
        # Tubos vacíos no contribuyen
        if not tube:
            continue
        
        # Verificar si el tubo tiene más de un color (está mezclado)
        unique_colors_in_tube = set(tube)
        
        if len(unique_colors_in_tube) > 1:
            # Todas las unidades en este tubo cuentan como mezcladas
            total_mixed_units += len(tube)
            
            # Contar unidades bloqueadas: se cuentan las unidades que están encima bloqueando
            # Nota: empezamos desde idx=1 porque la unidad en el tope (idx=0) nunca está bloqueada
            for idx in range(1, len(tube)):
                current_color = tube[idx]
                
                # Contar cuántas unidades de color diferente hay arriba bloqueando esta unidad
                blocking_units_count = 0
                for above_idx in range(idx):
                    if tube[above_idx] != current_color:
                        blocking_units_count += 1
                
                # Acumular el número de unidades bloqueantes (no solo si está o no bloqueada)
                blocked_units += blocking_units_count
    
    # Fórmula: mezclas + doble penalización por bloqueos
    return total_mixed_units + (2 * blocked_units)


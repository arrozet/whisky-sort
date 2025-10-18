"""Demo de visualización de solución paso a paso."""

from src.water_sort_game import WaterSortGame, GameState
from src.search_solver import SearchSolver
from src.heuristics import heuristic2_completed_tubes


def print_state(state: GameState):
    """Imprime un estado del juego de forma visual.
    
    En la representación interna: tube[0] es el TOPE, tube[-1] es el FONDO
    Visualmente: el líquido se acumula desde ABAJO (como un vaso real)
    """
    max_height = 4  # Capacidad fija de los tubos
    
    # Imprimir nivel por nivel desde arriba (espacios vacíos) hasta abajo (líquido)
    for visual_level in range(max_height):
        line = "   "
        for tube in state:
            # Calcular cuántos espacios vacíos hay arriba
            empty_spaces_above = max_height - len(tube)
            
            if visual_level < empty_spaces_above:
                # Este nivel está vacío (arriba del líquido)
                line += "[    ] "
            else:
                # Este nivel tiene líquido
                # El índice en el tubo: 0 (tope) está justo después de los espacios vacíos
                tube_index = visual_level - empty_spaces_above
                line += f"[{tube[tube_index]:^4}] "
        print(line)
    
    # Imprimir índices de los tubos
    indices = "   " + "".join(f"  T{i}   " for i in range(len(state)))
    print(indices)


def main():
    """Demostración de la visualización."""
    print("="*60)
    print("DEMO: Visualizacion de solucion con A* + H2")
    print("="*60)
    
    # Crear juego pequeño
    game = WaterSortGame(num_tubes=5, num_colors=3, seed=42)
    initial_state = game.get_initial_state()
    
    print("\nEstado Inicial:")
    print_state(initial_state)
    
    # Resolver con A* + H2 (heurística más prometedora - encuentra óptimo)
    solver = SearchSolver(game)
    print("\nResolviendo con A* + Heuristica 2 (Completed Tubes)...")
    result = solver.a_star(initial_state, heuristic2_completed_tubes)
    
    if result.solution_depth < 0:
        print("\nNo se encontro solucion.")
        return
    
    print(f"\nSolucion encontrada en {result.solution_depth} movimientos!")
    print(f"Nodos expandidos: {result.expanded_nodes}")
    print(f"Tiempo: {result.execution_time:.4f}s")
    
    # Mostrar paso a paso
    print("\n" + "="*60)
    print("PASOS DE LA SOLUCION")
    print("="*60)
    
    current_state = initial_state
    
    for i, move in enumerate(result.path, 1):
        print(f"\n--- Paso {i}: Mover de Tubo {move.source} a Tubo {move.target} ---")
        
        # Mostrar qué se mueve
        source_tube = current_state[move.source]
        if source_tube:
            color = source_tube[0]
            count = 1
            for j in range(1, len(source_tube)):
                if source_tube[j] == color:
                    count += 1
                else:
                    break
            print(f"Se mueven {count} unidad(es) de color {color}")
        
        # Aplicar movimiento
        current_state = game.apply_move(current_state, move)
        
        # Mostrar estado resultante
        print_state(current_state)
    
    print("\n" + "="*60)
    print("PUZZLE RESUELTO!")
    print("="*60)
    
    # Verificar que es estado objetivo
    if game.is_goal_state(current_state):
        print("\n[OK] Estado objetivo alcanzado correctamente.")
        print("\nEstado final:")
        for i, tube in enumerate(current_state):
            if tube:
                print(f"  Tubo {i}: {len(tube)} unidades de {tube[0]}")
            else:
                print(f"  Tubo {i}: [vacio]")


if __name__ == "__main__":
    main()


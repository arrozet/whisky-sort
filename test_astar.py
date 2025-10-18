"""Script de prueba para verificar la implementación de A*."""

from src.water_sort_game import WaterSortGame, GameState
from src.search_solver import SearchSolver, SearchResult
from src.heuristics import (
    heuristic1_color_entropy,
    heuristic2_completed_tubes,
    heuristic3_blocks
)


def print_state(state: GameState, title: str = "Estado"):
    """Imprime un estado del juego de forma visual.
    
    En la representación interna: tube[0] es el TOPE, tube[-1] es el FONDO
    Visualmente: el líquido se acumula desde ABAJO (como un vaso real)
    """
    print(f"\n{title}:")
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


def print_result(algorithm_name: str, result, show_path: bool = True):
    """Imprime los resultados de un algoritmo de búsqueda."""
    print(f"\n{'='*60}")
    print(f"Algoritmo: {algorithm_name}")
    print(f"{'='*60}")
    
    if result.solution_depth >= 0:
        print(f"[OK] Solucion encontrada!")
        print(f"   - Profundidad: {result.solution_depth}")
        print(f"   - Movimientos: {len(result.path)}")
        print(f"   - Nodos expandidos: {result.expanded_nodes}")
        print(f"   - Max. nodos en memoria: {result.max_frontier_size}")
        print(f"   - Tiempo de ejecucion: {result.execution_time:.4f}s")
        
        if show_path and result.path:
            print(f"\n   Secuencia de movimientos:")
            for i, move in enumerate(result.path, 1):
                print(f"      {i}. Tubo {move.source} -> Tubo {move.target}")
    else:
        print(f"[ERROR] No se encontro solucion")
        print(f"   - Nodos expandidos: {result.expanded_nodes}")
        print(f"   - Tiempo de ejecucion: {result.execution_time:.4f}s")


def visualize_solution(game: WaterSortGame, initial_state: GameState, result: SearchResult):
    """Visualiza paso a paso la solución del puzzle."""
    if result.solution_depth < 0:
        print("\nNo hay solucion para visualizar.")
        return
    
    print("\n" + "="*60)
    print("VISUALIZACION DE LA SOLUCION PASO A PASO")
    print("="*60)
    
    current_state = initial_state
    print_state(current_state, "Estado Inicial")
    
    for i, move in enumerate(result.path, 1):
        print(f"\n--- Movimiento {i}: Tubo {move.source} -> Tubo {move.target} ---")
        current_state = game.apply_move(current_state, move)
        print_state(current_state, f"Despues del movimiento {i}")
    
    print(f"\n{'='*60}")
    print("PUZZLE RESUELTO!")
    print(f"{'='*60}")


def main():
    """Función principal de prueba."""
    print("Prueba de A* con diferentes heuristicas")
    print("="*60)
    
    # Crear un juego pequeño para probar
    NUM_TUBOS = 5
    NUM_COLORES = 3
    SEED = 42
    
    print(f"\nConfigurando juego:")
    print(f"  - Tubos: {NUM_TUBOS}")
    print(f"  - Colores: {NUM_COLORES}")
    print(f"  - Semilla: {SEED}")
    
    game = WaterSortGame(num_tubes=NUM_TUBOS, num_colors=NUM_COLORES, seed=SEED)
    initial_state = game.get_initial_state()
    
    print(f"\nEstado inicial:")
    for i, tube in enumerate(initial_state):
        if tube:
            print(f"  Tubo {i}: {tube}")
        else:
            print(f"  Tubo {i}: [vacío]")
    
    # Crear el solver
    solver = SearchSolver(game)
    
    # Probar con BFS para comparación
    print("\n" + "="*60)
    print("Ejecutando BFS (para comparar)...")
    result_bfs = solver.bfs(initial_state)
    print_result("BFS", result_bfs)
    
    # Probar A* con heurística 1 (Color Entropy)
    print("\n" + "="*60)
    print("Ejecutando A* con Heurística 1 (Color Entropy)...")
    result_astar_h1 = solver.a_star(initial_state, heuristic1_color_entropy)
    print_result("A* + H1 (Color Entropy)", result_astar_h1)
    
    # Probar A* con heurística 2 (Completed Tubes)
    print("\n" + "="*60)
    print("Ejecutando A* con Heurística 2 (Completed Tubes)...")
    result_astar_h2 = solver.a_star(initial_state, heuristic2_completed_tubes)
    print_result("A* + H2 (Completed Tubes)", result_astar_h2)
    
    # Probar A* con heurística 3 (Blocks)
    print("\n" + "="*60)
    print("Ejecutando A* con Heurística 3 (Blocks)...")
    result_astar_h3 = solver.a_star(initial_state, heuristic3_blocks)
    print_result("A* + H3 (Blocks)", result_astar_h3)
    
    # Comparación final
    print("\n" + "="*60)
    print("COMPARACION DE ALGORITMOS")
    print("="*60)
    
    algorithms = [
        ("BFS", result_bfs),
        ("A* + H1", result_astar_h1),
        ("A* + H2", result_astar_h2),
        ("A* + H3", result_astar_h3),
    ]
    
    print(f"\n{'Algoritmo':<15} {'Profund.':<10} {'Nodos Exp.':<12} {'Max Mem.':<10} {'Tiempo (s)':<12}")
    print("-" * 60)
    
    for name, result in algorithms:
        if result.solution_depth >= 0:
            print(f"{name:<15} {result.solution_depth:<10} {result.expanded_nodes:<12} "
                  f"{result.max_frontier_size:<10} {result.execution_time:<12.4f}")
        else:
            print(f"{name:<15} {'N/A':<10} {result.expanded_nodes:<12} "
                  f"{result.max_frontier_size:<10} {result.execution_time:<12.4f}")
    
    # Visualizar la solución de la mejor heurística (H2 - solución óptima)
    print("\n" + "="*60)
    print("Desea ver la visualizacion paso a paso? (s/n): ", end="")
    response = input().strip().lower()
    
    if response in ['s', 'si', 'y', 'yes']:
        # Elegir la solución con menos movimientos
        best_result = min(
            [result_bfs, result_astar_h1, result_astar_h2, result_astar_h3],
            key=lambda r: r.solution_depth if r.solution_depth >= 0 else float('inf')
        )
        visualize_solution(game, initial_state, best_result)
    
    print("\nPruebas completadas!")


if __name__ == "__main__":
    main()


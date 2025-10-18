"""Script de prueba para verificar la implementación de IDA*."""

from src.water_sort_game import WaterSortGame, GameState
from src.search_solver import SearchSolver, SearchResult
from src.heuristics import (
    heuristic1_color_entropy,
    heuristic2_completed_tubes,
    heuristic3_blocks
)


def print_state(state: GameState, title: str = "Estado"):
    """Imprime un estado del juego de forma visual."""
    print(f"\n{title}:")
    max_height = 4
    
    for visual_level in range(max_height):
        line = "   "
        for tube in state:
            empty_spaces_above = max_height - len(tube)
            
            if visual_level < empty_spaces_above:
                line += "[    ] "
            else:
                tube_index = visual_level - empty_spaces_above
                line += f"[{tube[tube_index]:^4}] "
        print(line)
    
    indices = "   " + "".join(f"  T{i}   " for i in range(len(state)))
    print(indices)


def print_result(algorithm_name: str, result: SearchResult, show_path: bool = False):
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


def main():
    """Función principal de prueba."""
    print("Prueba de IDA* con diferentes heuristicas")
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
    
    print_state(initial_state, "Estado inicial")
    
    # Crear el solver
    solver = SearchSolver(game)
    
    # Probar IDA* con heurística 1 (Color Entropy)
    print("\n" + "="*60)
    print("Ejecutando IDA* con Heuristica 1 (Color Entropy)...")
    result_idastar_h1 = solver.ida_star(initial_state, heuristic1_color_entropy)
    print_result("IDA* + H1 (Color Entropy)", result_idastar_h1)
    
    # Probar IDA* con heurística 2 (Completed Tubes)
    print("\n" + "="*60)
    print("Ejecutando IDA* con Heuristica 2 (Completed Tubes)...")
    result_idastar_h2 = solver.ida_star(initial_state, heuristic2_completed_tubes)
    print_result("IDA* + H2 (Completed Tubes)", result_idastar_h2)
    
    # Probar IDA* con heurística 3 (Blocks)
    print("\n" + "="*60)
    print("Ejecutando IDA* con Heuristica 3 (Blocks)...")
    result_idastar_h3 = solver.ida_star(initial_state, heuristic3_blocks)
    print_result("IDA* + H3 (Blocks)", result_idastar_h3)
    
    # Comparación con A* para validar
    print("\n" + "="*60)
    print("Comparacion con A* (para validacion)")
    print("="*60)
    
    result_astar_h2 = solver.a_star(initial_state, heuristic2_completed_tubes)
    
    print(f"\n{'Algoritmo':<20} {'Profund.':<10} {'Nodos Exp.':<12} {'Max Mem.':<10} {'Tiempo (s)':<12}")
    print("-" * 65)
    
    algorithms = [
        ("A* + H1", solver.a_star(initial_state, heuristic1_color_entropy)),
        ("A* + H2", result_astar_h2),
        ("A* + H3", solver.a_star(initial_state, heuristic3_blocks)),
        ("IDA* + H1", result_idastar_h1),
        ("IDA* + H2", result_idastar_h2),
        ("IDA* + H3", result_idastar_h3),
    ]
    
    for name, result in algorithms:
        if result.solution_depth >= 0:
            print(f"{name:<20} {result.solution_depth:<10} {result.expanded_nodes:<12} "
                  f"{result.max_frontier_size:<10} {result.execution_time:<12.4f}")
        else:
            print(f"{name:<20} {'N/A':<10} {result.expanded_nodes:<12} "
                  f"{result.max_frontier_size:<10} {result.execution_time:<12.4f}")
    
    # Análisis
    print("\n" + "="*60)
    print("ANALISIS")
    print("="*60)
    print("\nCaracteristicas de IDA*:")
    print("  - Encuentra soluciones optimas (como A*)")
    print("  - Usa mucha menos memoria que A* (solo guarda el camino actual)")
    print("  - Puede expandir mas nodos que A* debido a reexpansiones")
    print("  - Ideal para problemas con memoria limitada")
    
    if result_astar_h2.solution_depth == result_idastar_h2.solution_depth:
        print(f"\n[OK] IDA* encontro la solucion optima ({result_idastar_h2.solution_depth} movimientos)")
    
    print("\nPruebas completadas!")


if __name__ == "__main__":
    main()


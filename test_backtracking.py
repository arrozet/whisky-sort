"""Script de prueba para verificar la implementación de Backtracking con Cota."""

from src.water_sort_game import WaterSortGame, GameState
from src.search_solver import SearchSolver, SearchResult
from src.heuristics import heuristic2_completed_tubes


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
        print(f"   - Max. profundidad alcanzada: {result.max_frontier_size}")
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
    print("Prueba de Backtracking con Cota")
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
    
    # Probar Backtracking sin heurística
    print("\n" + "="*60)
    print("Ejecutando Backtracking sin heuristica...")
    result_bt_no_h = solver.backtracking_with_bound(initial_state)
    print_result("Backtracking (sin heuristica)", result_bt_no_h)
    
    # Probar Backtracking con heurística H2
    print("\n" + "="*60)
    print("Ejecutando Backtracking con Heuristica 2 (Completed Tubes)...")
    result_bt_h2 = solver.backtracking_with_bound(initial_state, heuristic=heuristic2_completed_tubes)
    print_result("Backtracking + H2", result_bt_h2)
    
    # Probar con un límite de profundidad personalizado
    print("\n" + "="*60)
    print("Ejecutando Backtracking con limite de profundidad 15...")
    result_bt_limit = solver.backtracking_with_bound(initial_state, max_depth=15, heuristic=heuristic2_completed_tubes)
    print_result("Backtracking + H2 (limite 15)", result_bt_limit)
    
    # Comparación con otros algoritmos
    print("\n" + "="*60)
    print("Comparacion con otros algoritmos")
    print("="*60)
    
    result_bfs = solver.bfs(initial_state)
    result_dfs = solver.dfs(initial_state)
    result_astar = solver.a_star(initial_state, heuristic2_completed_tubes)
    
    print(f"\n{'Algoritmo':<25} {'Profund.':<10} {'Nodos Exp.':<12} {'Max Mem./Prof.':<15} {'Tiempo (s)':<12}")
    print("-" * 75)
    
    algorithms = [
        ("BFS", result_bfs),
        ("DFS", result_dfs),
        ("A* + H2", result_astar),
        ("BT (sin h)", result_bt_no_h),
        ("BT + H2", result_bt_h2),
        ("BT + H2 (limite 15)", result_bt_limit),
    ]
    
    for name, result in algorithms:
        if result.solution_depth >= 0:
            print(f"{name:<25} {result.solution_depth:<10} {result.expanded_nodes:<12} "
                  f"{result.max_frontier_size:<15} {result.execution_time:<12.4f}")
        else:
            print(f"{name:<25} {'N/A':<10} {result.expanded_nodes:<12} "
                  f"{result.max_frontier_size:<15} {result.execution_time:<12.4f}")
    
    # Análisis
    print("\n" + "="*60)
    print("ANALISIS")
    print("="*60)
    print("\nCaracteristicas de Backtracking con Cota:")
    print("  - Busca la mejor solucion (mas corta) dentro de la cota")
    print("  - La cota se actualiza cada vez que encuentra una solucion")
    print("  - Poda ramas que exceden la mejor solucion encontrada")
    print("  - Puede usar heuristica para mejorar la poda")
    print("  - Usa poco espacio (solo el camino actual)")
    
    if result_bt_h2.solution_depth >= 0:
        print(f"\n[OK] Backtracking + H2 encontro solucion en {result_bt_h2.solution_depth} movimientos")
        print(f"     Expandio {result_bt_h2.expanded_nodes} nodos en {result_bt_h2.execution_time:.4f}s")
    
    print("\nPruebas completadas!")


if __name__ == "__main__":
    main()


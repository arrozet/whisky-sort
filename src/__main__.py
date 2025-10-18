"""Punto de entrada principal para ejecutar el solver de Water Sort Puzzle."""

from __future__ import annotations

import argparse
import sys
from typing import Callable, Dict, Optional

from .generator import PuzzleGenerator
from .heuristics import heuristic3_blocks, heuristic1_color_entropy, heuristic2_completed_tubes
from .search_solver import CostHeuristic, SearchResult, SearchSolver
from .water_sort_game import GameState, Move, WaterSortGame


# Diccionario que mapea nombres de heurísticas a sus funciones
HEURISTICS: Dict[str, CostHeuristic] = {
    "h1": heuristic1_color_entropy,
    "entropy": heuristic1_color_entropy,
    "color_entropy": heuristic1_color_entropy,
    "h2": heuristic2_completed_tubes,
    "completed": heuristic2_completed_tubes,
    "completed_tubes": heuristic2_completed_tubes,
    "h3": heuristic3_blocks,
    "blocks": heuristic3_blocks,
}


def parse_arguments() -> argparse.Namespace:
    """Procesa los argumentos de la línea de comandos para configurar la ejecución.
    
    Returns:
        Namespace con los argumentos parseados y validados.
    """
    parser = argparse.ArgumentParser(
        description="Water Sort Puzzle Solver - Resuelve el puzzle usando algoritmos de búsqueda",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Resolver con BFS
  python -m src --algorithm bfs --tubes 5 --colors 3 --seed 42
  
  # Resolver con A* y heurística 2
  python -m src --algorithm astar --heuristic h2 --tubes 6 --colors 4
  
  # Resolver con DFS y límite de profundidad
  python -m src --algorithm dls --depth-limit 50 --tubes 5 --colors 3
  
  # Comparar todos los algoritmos
  python -m src --compare --tubes 5 --colors 3 --seed 100
        """
    )
    
    # Grupo: Configuración del juego
    game_group = parser.add_argument_group("Configuración del juego")
    game_group.add_argument(
        "--tubes", "-t",
        type=int,
        default=5,
        help="Número de tubos (por defecto: 5)"
    )
    game_group.add_argument(
        "--colors", "-c",
        type=int,
        default=3,
        help="Número de colores diferentes (por defecto: 3)"
    )
    game_group.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Semilla para generar el estado inicial (opcional)"
    )
    
    # Grupo: Algoritmo de búsqueda
    algo_group = parser.add_argument_group("Algoritmo de búsqueda")
    algo_group.add_argument(
        "--algorithm", "-a",
        type=str,
        choices=["bfs", "dfs", "dls", "astar", "a*", "idastar", "ida*", "backtracking", "bt"],
        default="bfs",
        help="Algoritmo a utilizar (por defecto: bfs)"
    )
    algo_group.add_argument(
        "--heuristic", "-H",
        type=str,
        choices=list(HEURISTICS.keys()),
        default="h2",
        help="Heurística para A* o IDA* (por defecto: h2)"
    )
    algo_group.add_argument(
        "--depth-limit",
        type=int,
        default=None,
        help="Límite de profundidad para DLS (por defecto: automático)"
    )
    
    # Grupo: Visualización y output
    output_group = parser.add_argument_group("Visualización y salida")
    output_group.add_argument(
        "--show-steps",
        action="store_true",
        help="Mostrar la secuencia de movimientos paso a paso"
    )
    output_group.add_argument(
        "--show-initial",
        action="store_true",
        default=True,
        help="Mostrar el estado inicial del puzzle"
    )
    output_group.add_argument(
        "--show-final",
        action="store_true",
        help="Mostrar el estado final del puzzle"
    )
    output_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar información detallada durante la ejecución"
    )
    output_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Mostrar solo los resultados finales"
    )
    
    # Grupo: Modos especiales
    special_group = parser.add_argument_group("Modos especiales")
    special_group.add_argument(
        "--compare",
        action="store_true",
        help="Comparar todos los algoritmos disponibles"
    )
    special_group.add_argument(
        "--benchmark",
        type=int,
        metavar="N",
        help="Ejecutar N veces y promediar resultados"
    )
    
    args = parser.parse_args()
    
    # Validaciones
    if args.colors > args.tubes - 2:
        parser.error(f"El número de colores ({args.colors}) debe ser menor o igual a tubes-2 ({args.tubes-2})")
    
    if args.colors < 1:
        parser.error("El número de colores debe ser al menos 1")
    
    if args.tubes < 3:
        parser.error("El número de tubos debe ser al menos 3")
    
    # Normalizar nombres de algoritmos
    if args.algorithm in ["a*"]:
        args.algorithm = "astar"
    elif args.algorithm in ["ida*"]:
        args.algorithm = "idastar"
    elif args.algorithm in ["bt"]:
        args.algorithm = "backtracking"
    
    return args


def build_game_and_solver(args: argparse.Namespace) -> tuple[WaterSortGame, SearchSolver, GameState]:
    """Construye las instancias del juego y solver basadas en los argumentos.
    
    Args:
        args: Argumentos parseados de la línea de comandos.
        
    Returns:
        Tupla con (juego, solver, estado_inicial)
    """
    # Crear instancia del juego
    game = WaterSortGame(
        num_tubes=args.tubes,
        num_colors=args.colors,
        seed=args.seed
    )
    
    # Generar estado inicial
    initial_state = game.get_initial_state()
    
    # Crear solver
    solver = SearchSolver(game)
    
    return game, solver, initial_state


def print_state(state: GameState, title: str = "Estado") -> None:
    """Imprime un estado del juego de forma visual.
    
    Args:
        state: Estado del juego a imprimir.
        title: Título a mostrar encima del estado.
    """
    print(f"\n{title}:")
    max_height = 4  # Capacidad fija de los tubos
    
    # Imprimir nivel por nivel desde arriba hasta abajo
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
    
    # Imprimir índices de los tubos
    indices = "   " + "".join(f"  T{i}   " for i in range(len(state)))
    print(indices)


def print_result(algorithm_name: str, result: SearchResult, verbose: bool = False) -> None:
    """Imprime los resultados de un algoritmo de búsqueda.
    
    Args:
        algorithm_name: Nombre del algoritmo ejecutado.
        result: Resultado de la búsqueda.
        verbose: Si True, muestra información adicional.
    """
    print(f"\n{'='*70}")
    print(f"Algoritmo: {algorithm_name}")
    print(f"{'='*70}")
    
    if result.solution_depth >= 0:
        print(f"[OK] Solucion encontrada!")
        print(f"  - Profundidad de la solucion: {result.solution_depth}")
        print(f"  - Movimientos en la solucion: {len(result.path)}")
        print(f"  - Nodos expandidos: {result.expanded_nodes}")
        print(f"  - Maximo de nodos en memoria: {result.max_frontier_size}")
        print(f"  - Tiempo de ejecucion: {result.execution_time:.4f} segundos")
        
        if verbose and result.path:
            print(f"\n  Secuencia de movimientos:")
            for i, move in enumerate(result.path, 1):
                print(f"    {i:2d}. Tubo {move.source} -> Tubo {move.target}")
    else:
        print(f"[ERROR] No se encontro solucion")
        print(f"  - Nodos expandidos: {result.expanded_nodes}")
        print(f"  - Tiempo de ejecucion: {result.execution_time:.4f} segundos")


def visualize_solution(game: WaterSortGame, initial_state: GameState, result: SearchResult) -> None:
    """Visualiza paso a paso la solución del puzzle.
    
    Args:
        game: Instancia del juego.
        initial_state: Estado inicial del puzzle.
        result: Resultado con la solución a visualizar.
    """
    if result.solution_depth < 0:
        print("\n[!] No hay solucion para visualizar.")
        return
    
    print("\n" + "="*70)
    print("VISUALIZACION DE LA SOLUCION PASO A PASO")
    print("="*70)
    
    current_state = initial_state
    print_state(current_state, "Estado Inicial")
    
    for i, move in enumerate(result.path, 1):
        # Mostrar información del movimiento
        source_tube = current_state[move.source]
        if source_tube:
            color = source_tube[0]
            count = 1
            for j in range(1, len(source_tube)):
                if source_tube[j] == color:
                    count += 1
                else:
                    break
            print(f"\n--- Paso {i}/{len(result.path)}: Tubo {move.source} -> Tubo {move.target} " +
                  f"(mover {count} unidad(es) de {color}) ---")
        
        # Aplicar movimiento
        current_state = game.apply_move(current_state, move)
        print_state(current_state, f"Después del paso {i}")
    
    print(f"\n{'='*70}")
    print("[OK] PUZZLE RESUELTO!")
    print(f"{'='*70}")


def run_single_algorithm(
    game: WaterSortGame,
    solver: SearchSolver,
    initial_state: GameState,
    args: argparse.Namespace
) -> SearchResult:
    """Ejecuta un único algoritmo y retorna el resultado.
    
    Args:
        game: Instancia del juego.
        solver: Instancia del solver.
        initial_state: Estado inicial del puzzle.
        args: Argumentos de configuración.
        
    Returns:
        Resultado de la búsqueda.
    """
    # Obtener heurística si es necesaria
    heuristic: Optional[CostHeuristic] = None
    if args.algorithm in ["astar", "idastar"]:
        heuristic = HEURISTICS[args.heuristic]
    elif args.algorithm == "backtracking" and args.heuristic:
        # Backtracking puede opcionalmente usar heurística
        heuristic = HEURISTICS[args.heuristic]
    
    # Ejecutar el algoritmo
    if not args.quiet:
        print(f"\n>> Ejecutando {args.algorithm.upper()}...")
        if heuristic:
            print(f"   Usando heurística: {args.heuristic}")
    
    if args.algorithm == "dls" and args.depth_limit:
        result = solver.depth_limited_search(initial_state, args.depth_limit)
    else:
        result = solver.solve(initial_state, args.algorithm, heuristic)
    
    return result


def run_comparison(
    game: WaterSortGame,
    solver: SearchSolver,
    initial_state: GameState,
    args: argparse.Namespace
) -> None:
    """Ejecuta y compara múltiples algoritmos.
    
    Args:
        game: Instancia del juego.
        solver: Instancia del solver.
        initial_state: Estado inicial del puzzle.
        args: Argumentos de configuración.
    """
    print("\n" + "="*70)
    print("COMPARACION DE ALGORITMOS")
    print("="*70)
    
    # Lista de algoritmos a comparar
    algorithms = [
        ("BFS", "bfs", None),
        ("DFS", "dfs", None),
        ("A* + H1", "astar", heuristic1_color_entropy),
        ("A* + H2", "astar", heuristic2_completed_tubes),
        ("A* + H3", "astar", heuristic3_blocks),
        ("IDA* + H1", "idastar", heuristic1_color_entropy),
        ("IDA* + H2", "idastar", heuristic2_completed_tubes),
        ("IDA* + H3", "idastar", heuristic3_blocks),
        ("BT (sin h)", "backtracking", None),
        ("BT + H2", "backtracking", heuristic2_completed_tubes),
    ]
    
    results = []
    
    for name, method, heuristic in algorithms:
        if not args.quiet:
            print(f"\n-> Ejecutando {name}...", end=" ", flush=True)
        
        try:
            result = solver.solve(initial_state, method, heuristic)
            results.append((name, result))
            if not args.quiet:
                if result.solution_depth >= 0:
                    print(f"[OK] (profundidad: {result.solution_depth})")
                else:
                    print("[X] (sin solucion)")
        except Exception as e:
            if not args.quiet:
                print(f"[X] Error: {e}")
            results.append((name, None))
    
    # Tabla comparativa
    print("\n" + "="*70)
    print("RESULTADOS COMPARATIVOS")
    print("="*70)
    print(f"\n{'Algoritmo':<15} {'Profund.':<10} {'Nodos Exp.':<13} {'Max Mem.':<11} {'Tiempo (s)':<12}")
    print("-" * 70)
    
    for name, result in results:
        if result and result.solution_depth >= 0:
            print(f"{name:<15} {result.solution_depth:<10} {result.expanded_nodes:<13} "
                  f"{result.max_frontier_size:<11} {result.execution_time:<12.4f}")
        elif result:
            print(f"{name:<15} {'N/A':<10} {result.expanded_nodes:<13} "
                  f"{result.max_frontier_size:<11} {result.execution_time:<12.4f}")
        else:
            print(f"{name:<15} {'ERROR':<10} {'-':<13} {'-':<11} {'-':<12}")
    
    # Identificar el mejor algoritmo
    valid_results = [(name, res) for name, res in results if res and res.solution_depth >= 0]
    if valid_results:
        best_name, best_result = min(valid_results, key=lambda x: (x[1].solution_depth, x[1].execution_time))
        print(f"\n[*] Mejor algoritmo: {best_name}")
        print(f"   (Profundidad: {best_result.solution_depth}, Tiempo: {best_result.execution_time:.4f}s)")


def main() -> None:
    """Función principal que orquesta la ejecución del programa."""
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Banner inicial
        if not args.quiet:
            print("\n" + "="*70)
            print("WATER SORT PUZZLE SOLVER")
            print("="*70)
            print(f"\nConfiguracion:")
            print(f"  - Tubos: {args.tubes}")
            print(f"  - Colores: {args.colors}")
            print(f"  - Semilla: {args.seed if args.seed else 'Aleatoria'}")
        
        # Construir juego y solver
        game, solver, initial_state = build_game_and_solver(args)
        
        # Mostrar estado inicial si se solicita
        if args.show_initial and not args.quiet:
            print_state(initial_state, "Estado Inicial")
            if args.verbose:
                print("\nDetalle de tubos:")
                for i, tube in enumerate(initial_state):
                    if tube:
                        print(f"  Tubo {i}: {tube}")
                    else:
                        print(f"  Tubo {i}: [vacío]")
        
        # Modo comparación
        if args.compare:
            run_comparison(game, solver, initial_state, args)
            return
        
        # Modo normal: ejecutar un solo algoritmo
        result = run_single_algorithm(game, solver, initial_state, args)
        
        # Mostrar resultado
        if not args.quiet:
            algo_name = args.algorithm.upper()
            if args.algorithm in ["astar", "idastar"]:
                algo_name += f" + {args.heuristic.upper()}"
            print_result(algo_name, result, verbose=args.verbose)
        else:
            # Modo quiet: solo estadísticas básicas
            if result.solution_depth >= 0:
                print(f"{args.algorithm},{result.solution_depth},{result.expanded_nodes},"
                      f"{result.max_frontier_size},{result.execution_time:.4f}")
            else:
                print(f"{args.algorithm},FAIL,{result.expanded_nodes},"
                      f"{result.max_frontier_size},{result.execution_time:.4f}")
        
        # Visualización paso a paso
        if args.show_steps and result.solution_depth >= 0:
            visualize_solution(game, initial_state, result)
        
        # Mostrar estado final
        if args.show_final and result.solution_depth >= 0:
            current_state = initial_state
            for move in result.path:
                current_state = game.apply_move(current_state, move)
            print_state(current_state, "Estado Final")
            
            if game.is_goal_state(current_state):
                print("\n[OK] Verificacion: El estado final es valido y resuelve el puzzle.")
        
        # Retornar código de salida apropiado
        sys.exit(0 if result.solution_depth >= 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n[!] Ejecucion interrumpida por el usuario.")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}", file=sys.stderr)
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


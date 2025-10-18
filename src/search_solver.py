"""Implementaciones de algoritmos de búsqueda para resolver Water Sort Puzzle."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Deque, Dict, Iterable, List, Optional, Protocol, Sequence, Set, Tuple

from collections import deque
import heapq

from .water_sort_game import GameState, Move, WaterSortGame


CostHeuristic = Callable[[GameState], int]


@dataclass(frozen=True)
class SearchResult:
    """Almacena la información relevante obtenida tras la búsqueda."""

    path: Sequence[Move]
    expanded_nodes: int
    max_frontier_size: int
    solution_depth: int
    execution_time: float


@dataclass(frozen=True)
class SearchNode:
    """Representa un nodo de búsqueda con referencias a su trayectoria."""

    state: GameState
    parent: Optional["SearchNode"] = None
    move: Optional[Move] = None
    depth: int = 0
    cost: int = 0
    estimated_total: int = 0

    def reconstruct_path(self) -> Sequence[Move]:
        """Reconstruye la secuencia de movimientos desde la raíz hasta este nodo."""
        path: List[Move] = []
        current: Optional["SearchNode"] = self

        # Se recorre hacia atrás la cadena de padres acumulando los movimientos hasta la raíz.
        while current is not None and current.move is not None:
            path.append(current.move)
            current = current.parent

        path.reverse()
        return tuple(path)


class Frontier(Protocol):
    """Protocolo para colas de frontera utilizadas en la búsqueda."""

    def push(self, item: Tuple[int, GameState, Sequence[Move]]) -> None:
        ...

    def pop(self) -> Tuple[int, GameState, Sequence[Move]]:
        ...

    def __len__(self) -> int:
        ...


class SearchSolver:
    """Clase que contiene la implementación de los algoritmos de búsqueda."""

    def __init__(self, game: WaterSortGame) -> None:
        """Inicializa el solver con una instancia del juego."""
        self.game: WaterSortGame = game
        self.default_depth_limit: int = self.game.num_tubes * self.game.tube_capacity * 2

    def _check_initial_goal(self, initial_state: GameState, start_time: float) -> Optional[SearchResult]:
        """Verifica si el estado inicial ya es objetivo y retorna resultado si lo es.
        
        Args:
            initial_state: Estado a verificar.
            start_time: Tiempo de inicio de la búsqueda.
            
        Returns:
            SearchResult si es objetivo, None en caso contrario.
        """
        if self.game.is_goal_state(initial_state):
            execution_time: float = time.perf_counter() - start_time
            return SearchResult(
                path=tuple(),
                expanded_nodes=0,
                max_frontier_size=1,
                solution_depth=0,
                execution_time=execution_time,
            )
        return None

    def _create_success_result(
        self,
        path: Sequence[Move],
        expanded_nodes: int,
        max_frontier_size: int,
        solution_depth: int,
        start_time: float
    ) -> SearchResult:
        """Crea un SearchResult para cuando se encuentra una solución.
        
        Args:
            path: Secuencia de movimientos que resuelve el puzzle.
            expanded_nodes: Número de nodos expandidos.
            max_frontier_size: Tamaño máximo de la frontera.
            solution_depth: Profundidad de la solución.
            start_time: Tiempo de inicio de la búsqueda.
            
        Returns:
            SearchResult con la solución encontrada.
        """
        execution_time: float = time.perf_counter() - start_time
        return SearchResult(
            path=path,
            expanded_nodes=expanded_nodes,
            max_frontier_size=max_frontier_size,
            solution_depth=solution_depth,
            execution_time=execution_time,
        )

    def _create_failure_result(
        self,
        expanded_nodes: int,
        max_frontier_size: int,
        start_time: float
    ) -> SearchResult:
        """Crea un SearchResult para cuando no se encuentra solución.
        
        Args:
            expanded_nodes: Número de nodos expandidos.
            max_frontier_size: Tamaño máximo de la frontera.
            start_time: Tiempo de inicio de la búsqueda.
            
        Returns:
            SearchResult indicando fallo en la búsqueda.
        """
        execution_time: float = time.perf_counter() - start_time
        return SearchResult(
            path=tuple(),
            expanded_nodes=expanded_nodes,
            max_frontier_size=max_frontier_size,
            solution_depth=-1,
            execution_time=execution_time,
        )

    def solve(self, initial_state: GameState, method: str, heuristic: Optional[CostHeuristic] = None) -> SearchResult:
        """Resuelve el puzzle usando el método de búsqueda indicado.

        Args:
            initial_state: Estado inicial desde el cual se iniciará la búsqueda.
            method: Identificador del algoritmo a ejecutar (por ejemplo, "bfs").
            heuristic: Función heurística opcional requerida por métodos informados.

        Returns:
            Resultado de la búsqueda con la ruta y las métricas recopiladas.

        Raises:
            ValueError: Si el método indicado no está implementado o es desconocido.
        """
        # Se normaliza el nombre del método para aceptar variantes en mayúsculas/minúsculas.
        normalized_method: str = method.strip().lower()

        if normalized_method == "bfs":
            return self.bfs(initial_state)

        if normalized_method == "dfs":
            return self.dfs(initial_state)

        if normalized_method in {"dls", "depth_limited", "depth_limited_search"}:
            return self.depth_limited_search(initial_state, depth_limit=self.default_depth_limit)

        if normalized_method in {"a*", "astar", "a_star"}:
            if heuristic is None:
                raise ValueError("A* requiere una función heurística")
            return self.a_star(initial_state, heuristic)

        if normalized_method in {"ida*", "idastar", "ida_star"}:
            if heuristic is None:
                raise ValueError("IDA* requiere una función heurística")
            return self.ida_star(initial_state, heuristic)

        if normalized_method in {"backtracking", "bt", "backtracking_with_bound"}:
            # Backtracking puede usar o no una heurística
            return self.backtracking_with_bound(initial_state, heuristic=heuristic)

        raise ValueError(f"Método de búsqueda desconocido: {method}")

    def bfs(self, initial_state: GameState) -> SearchResult:
        """Ejecuta la búsqueda en amplitud para encontrar una solución óptima en movimientos.

        Args:
            initial_state: Estado desde el cual se explora el espacio de búsqueda.

        Returns:
            Resultado que incluye la ruta solución (si existe) junto con métricas.
        """
        # Se mide el tiempo de ejecución desde el comienzo del algoritmo
        start_time: float = time.perf_counter()

        # Si el estado inicial ya es objetivo, se devuelve inmediatamente
        if result := self._check_initial_goal(initial_state, start_time):
            return result

        # Se inicializa la frontera FIFO y los conjuntos auxiliares
        frontier: Deque[SearchNode] = deque([SearchNode(state=initial_state)])
        visited: Set[GameState] = {initial_state}

        expanded_nodes: int = 0
        max_frontier_size: int = len(frontier)

        # Mientras haya nodos que explorar en la frontera
        while frontier:
            current_node: SearchNode = frontier.popleft()
            expanded_nodes += 1

            # Se generan y evalúan todos los movimientos válidos desde el estado actual
            for move in self.game.get_valid_moves(current_node.state):
                next_state: GameState = self.game.apply_move(current_node.state, move)

                # Se omiten estados ya visitados para evitar ciclos compartiendo lógica común
                if not self._register_if_unvisited(next_state, visited):
                    continue

                next_node: SearchNode = SearchNode(
                    state=next_state,
                    parent=current_node,
                    move=move,
                    depth=current_node.depth + 1,
                )

                # Se verifica inmediatamente si se alcanzó el objetivo
                if self.game.is_goal_state(next_state):
                    path: Sequence[Move] = next_node.reconstruct_path()
                    return self._create_success_result(
                        path, expanded_nodes, max_frontier_size,
                        next_node.depth, start_time
                    )

                frontier.append(next_node)
                max_frontier_size = max(max_frontier_size, len(frontier))

        # Si la búsqueda finaliza sin encontrar solución, se devuelven métricas acumuladas
        return self._create_failure_result(expanded_nodes, max_frontier_size, start_time)

    def dfs(self, initial_state: GameState) -> SearchResult:
        """Ejecuta la búsqueda en profundidad manejando límites y detección de ciclos."""
        return self._iterative_depth_first_search(initial_state, self.default_depth_limit)

    def depth_limited_search(self, initial_state: GameState, depth_limit: int) -> SearchResult:
        """Realiza una búsqueda en profundidad limitada hasta una cota específica."""
        if depth_limit < 0:
            raise ValueError("El límite de profundidad debe ser no negativo")

        return self._iterative_depth_first_search(initial_state, depth_limit)

    def _register_if_unvisited(self, state: GameState, visited: Set[GameState]) -> bool:
        """Registra el estado si no se ha visto previamente.

        Args:
            state: Estado que se desea evaluar.
            visited: Conjunto de referencia que acumula los estados visitados.

        Returns:
            Verdadero si el estado fue agregado; falso si ya se había procesado antes.
        """
        if state in visited:
            return False

        visited.add(state)
        return True

    def _iterative_depth_first_search(self, initial_state: GameState, depth_limit: int) -> SearchResult:
        """Ejecuta un recorrido en profundidad iterativo acotado por un límite.

        Args:
            initial_state: Estado a partir del cual se comienza a explorar.
            depth_limit: Profundidad máxima permitida para expandir nodos.

        Returns:
            Resultado de la exploración que incluye métricas y ruta en caso de éxito.
        """
        start_time: float = time.perf_counter()

        if result := self._check_initial_goal(initial_state, start_time):
            return result

        # Se inicializa la pila LIFO con la raíz para explorar priorizando profundidades mayores.
        stack: List[SearchNode] = [SearchNode(state=initial_state)]
        visited: Set[GameState] = {initial_state}

        expanded_nodes: int = 0
        max_frontier_size: int = len(stack)

        # Se procesa cada nodo hasta que la pila quede vacía.
        while stack:
            current_node: SearchNode = stack.pop()
            expanded_nodes += 1

            # Si se alcanzó el límite, no se generan sucesores para evitar desbordes.
            if current_node.depth >= depth_limit:
                continue

            for move in self.game.get_valid_moves(current_node.state):
                next_state: GameState = self.game.apply_move(current_node.state, move)

                # Se descarta el sucesor si ya fue explorado en otra rama.
                if not self._register_if_unvisited(next_state, visited):
                    continue

                next_node: SearchNode = SearchNode(
                    state=next_state,
                    parent=current_node,
                    move=move,
                    depth=current_node.depth + 1,
                )

                # Se verifica si el nuevo estado satisface la condición objetivo.
                if self.game.is_goal_state(next_state):
                    path: Sequence[Move] = next_node.reconstruct_path()
                    return self._create_success_result(
                        path, expanded_nodes, max_frontier_size,
                        next_node.depth, start_time
                    )

                # El sucesor se apila para continuar la exploración en profundidad.
                stack.append(next_node)
                max_frontier_size = max(max_frontier_size, len(stack))

        return self._create_failure_result(expanded_nodes, max_frontier_size, start_time)

    def a_star(self, initial_state: GameState, heuristic: CostHeuristic) -> SearchResult:
        """Ejecuta búsqueda A* utilizando la heurística proporcionada.
        
        Implementa el algoritmo A* que combina el costo real g(n) con la
        estimación heurística h(n) para encontrar el camino óptimo.
        
        Args:
            initial_state: Estado desde el cual se explora el espacio de búsqueda.
            heuristic: Función que estima el costo desde un estado hasta el objetivo.
            
        Returns:
            Resultado que incluye la ruta solución (si existe) junto con métricas.
        """
        # Paso 1: Iniciar medición de tiempo
        start_time: float = time.perf_counter()
        
        # Paso 2: Verificar si el estado inicial ya es objetivo
        if result := self._check_initial_goal(initial_state, start_time):
            return result
        
        # Paso 3: Crear estructuras de datos
        # ABIERTOS: cola de prioridad ordenada por f(n) = g(n) + h(n)
        # Formato: (f_value, counter, node) donde counter desempata por orden de inserción
        counter: int = 0  # Para evitar comparación de nodos cuando f es igual
        h_initial: int = heuristic(initial_state)
        initial_node = SearchNode(
            state=initial_state,
            depth=0,
            cost=0,
            estimated_total=h_initial
        )
        
        open_list: List[Tuple[int, int, SearchNode]] = [(h_initial, counter, initial_node)]
        heapq.heapify(open_list)
        counter += 1
        
        # CERRADOS: conjunto de estados ya procesados
        closed_set: Set[GameState] = set()
        
        # Diccionario para rastrear el mejor g(n) conocido para cada estado
        best_g_score: Dict[GameState, int] = {initial_state: 0}
        
        # Métricas
        expanded_nodes: int = 0
        max_frontier_size: int = len(open_list)
        
        # Paso 4: Bucle principal de búsqueda
        while open_list:
            # Paso 5: Seleccionar el nodo con menor f(n) de ABIERTOS
            f_value, _, current_node = heapq.heappop(open_list)
            
            # Si ya procesamos este estado, lo saltamos (puede haber duplicados)
            if current_node.state in closed_set:
                continue
            
            # Paso 6: Mover el nodo de ABIERTOS a CERRADOS
            closed_set.add(current_node.state)
            expanded_nodes += 1
            
            # Paso 7: Verificar si alcanzamos el objetivo
            if self.game.is_goal_state(current_node.state):
                path: Sequence[Move] = current_node.reconstruct_path()
                return self._create_success_result(
                    path, expanded_nodes, max_frontier_size,
                    current_node.depth, start_time
                )
            
            # Paso 8: Expandir el nodo (generar sucesores)
            for move in self.game.get_valid_moves(current_node.state):
                next_state: GameState = self.game.apply_move(current_node.state, move)
                
                # Calcular g(n) para el sucesor (costo desde inicio)
                tentative_g: int = current_node.depth + 1
                
                # Paso 9: Procesar el sucesor según si es nuevo o no
                # Si el estado está en CERRADOS y no encontramos mejor camino, lo ignoramos
                if next_state in closed_set:
                    if next_state in best_g_score and tentative_g >= best_g_score[next_state]:
                        continue
                    # Si encontramos un mejor camino, lo sacamos de CERRADOS
                    # (el algoritmo lo volverá a procesar si es mejor)
                    closed_set.discard(next_state)
                
                # Si es nuevo o encontramos un mejor camino
                if next_state not in best_g_score or tentative_g < best_g_score[next_state]:
                    # Actualizar el mejor g(n) conocido
                    best_g_score[next_state] = tentative_g
                    
                    # Calcular h(n) y f(n) = g(n) + h(n)
                    h_value: int = heuristic(next_state)
                    f_value: int = tentative_g + h_value
                    
                    # Crear nuevo nodo sucesor
                    next_node = SearchNode(
                        state=next_state,
                        parent=current_node,
                        move=move,
                        depth=tentative_g,
                        cost=tentative_g,
                        estimated_total=f_value
                    )
                    
                    # Añadir a ABIERTOS
                    heapq.heappush(open_list, (f_value, counter, next_node))
                    counter += 1
                    
                    # Actualizar métrica de frontera máxima
                    max_frontier_size = max(max_frontier_size, len(open_list))
        
        # Paso 10: Si ABIERTOS queda vacía sin encontrar solución
        return self._create_failure_result(expanded_nodes, max_frontier_size, start_time)

    def ida_star(self, initial_state: GameState, heuristic: CostHeuristic) -> SearchResult:
        """Ejecuta búsqueda IDA* mejorando el límite a partir de la heurística.
        
        IDA* combina la búsqueda en profundidad iterativa con la función de evaluación
        de A*. En cada iteración, realiza una búsqueda en profundidad limitada por
        un umbral basado en f(n) = g(n) + h(n).
        
        Args:
            initial_state: Estado desde el cual se explora el espacio de búsqueda.
            heuristic: Función que estima el costo desde un estado hasta el objetivo.
            
        Returns:
            Resultado que incluye la ruta solución (si existe) junto con métricas.
        """
        # Iniciar medición de tiempo
        start_time: float = time.perf_counter()
        
        # Verificar si el estado inicial ya es objetivo
        if result := self._check_initial_goal(initial_state, start_time):
            return result
        
        # Métricas globales
        total_expanded_nodes: int = 0
        max_frontier_size: int = 0
        
        # Límite inicial: f(s0) = g(s0) + h(s0) = 0 + h(s0)
        threshold: int = heuristic(initial_state)
        
        # Bucle principal: aumentar el umbral en cada iteración
        while True:
            # Realizar búsqueda en profundidad limitada con el umbral actual
            result = self._ida_star_search(
                initial_state=initial_state,
                heuristic=heuristic,
                threshold=threshold,
                start_time=start_time
            )
            
            # Actualizar métricas globales
            total_expanded_nodes += result.expanded_nodes
            max_frontier_size = max(max_frontier_size, result.max_frontier_size)
            
            # Si encontramos solución, devolver resultado
            if result.solution_depth >= 0:
                return self._create_success_result(
                    result.path, total_expanded_nodes, max_frontier_size,
                    result.solution_depth, start_time
                )
            
            # Si el nuevo umbral es infinito, no hay solución
            # (esto se indica con solution_depth = -1 y expanded_nodes = -1)
            if result.expanded_nodes == -1:
                return self._create_failure_result(
                    total_expanded_nodes, max_frontier_size, start_time
                )
            
            # El nuevo umbral es el mínimo f(n) que excedió el umbral anterior
            # (se almacena temporalmente en max_frontier_size para comunicación)
            threshold = result.max_frontier_size
    
    def _ida_star_search(
        self,
        initial_state: GameState,
        heuristic: CostHeuristic,
        threshold: int,
        start_time: float
    ) -> SearchResult:
        """Realiza una búsqueda en profundidad limitada por umbral para IDA*.
        
        Esta función auxiliar realiza una iteración de IDA*: explora el espacio
        de estados usando DFS recursivo, podando cuando f(n) excede el umbral.
        
        Args:
            initial_state: Estado inicial de esta iteración.
            heuristic: Función heurística para estimar costos.
            threshold: Límite actual de f(n) para esta iteración.
            start_time: Tiempo de inicio para limitar la ejecución.
            
        Returns:
            SearchResult donde:
            - Si encuentra solución: solution_depth >= 0, path contiene la solución
            - Si no encuentra: solution_depth = -1
            - Si no hay más estados: expanded_nodes = -1 (señal de FRACASO)
            - max_frontier_size almacena el siguiente umbral (min f(n) > threshold)
        """
        # Contador de nodos expandidos (mutable para recursión)
        expanded_nodes = [0]
        max_depth_reached = [0]
        
        def dfs_recursive(
            state: GameState,
            g_cost: int,
            path: List[Move],
            threshold: int,
            path_states: Set[GameState]
        ) -> tuple[Optional[List[Move]], int]:
            """DFS recursivo con límite de f.
            
            Returns:
                (path, min_exceeded): 
                - Si encuentra meta: (path, 0)
                - Si no encuentra: (None, min f que excedió threshold)
            """
            # Calcular f(n) = g(n) + h(n)
            h_cost = heuristic(state)
            f_cost = g_cost + h_cost
            
            # Si excede el umbral, retornar el valor para actualizar siguiente umbral
            if f_cost > threshold:
                return (None, f_cost)
            
            # Contar nodo expandido
            expanded_nodes[0] += 1
            max_depth_reached[0] = max(max_depth_reached[0], len(path))
            
            # Si es estado objetivo, retornar el camino
            if self.game.is_goal_state(state):
                return (path, 0)
            
            # Siguiente umbral mínimo encontrado
            min_exceeded = float('inf')
            
            # Explorar sucesores
            for move in self.game.get_valid_moves(state):
                next_state = self.game.apply_move(state, move)
                
                # Evitar ciclos en el camino actual
                if next_state in path_states:
                    continue
                
                # Añadir al camino
                new_path = path + [move]
                new_path_states = path_states | {next_state}
                
                # Recursión
                result, exceeded = dfs_recursive(
                    next_state,
                    g_cost + 1,
                    new_path,
                    threshold,
                    new_path_states
                )
                
                # Si encontramos solución, retornar inmediatamente
                if result is not None:
                    return (result, 0)
                
                # Actualizar el mínimo umbral excedido
                if exceeded < min_exceeded:
                    min_exceeded = exceeded
            
            # No se encontró solución en esta rama
            return (None, min_exceeded)
        
        # Ejecutar búsqueda recursiva
        path_states_initial: Set[GameState] = {initial_state}
        solution_path, min_exceeded = dfs_recursive(
            initial_state,
            0,
            [],
            threshold,
            path_states_initial
        )
        
        # Retornar resultado
        if solution_path is not None:
            # Se encontró solución
            return SearchResult(
                path=tuple(solution_path),
                expanded_nodes=expanded_nodes[0],
                max_frontier_size=max_depth_reached[0],
                solution_depth=len(solution_path),
                execution_time=0.0,
            )
        elif min_exceeded == float('inf'):
            # No hay más nodos que explorar: FRACASO
            return SearchResult(
                path=tuple(),
                expanded_nodes=-1,
                max_frontier_size=0,
                solution_depth=-1,
                execution_time=0.0,
            )
        else:
            # No se encontró en esta iteración, retornar siguiente umbral
            return SearchResult(
                path=tuple(),
                expanded_nodes=expanded_nodes[0],
                max_frontier_size=min_exceeded,  # Siguiente umbral
                solution_depth=-1,
                execution_time=0.0,
            )

    def backtracking_with_bound(
        self,
        initial_state: GameState,
        max_depth: Optional[int] = None,
        heuristic: Optional[CostHeuristic] = None
    ) -> SearchResult:
        """Realiza backtracking con poda basada en una cota de profundidad.
        
        Este algoritmo explora el espacio de estados recursivamente (backtracking)
        y mantiene una cota que se actualiza cada vez que encuentra una solución.
        Las ramas que exceden la cota actual son podadas.
        
        Args:
            initial_state: Estado desde el cual se explora el espacio de búsqueda.
            max_depth: Profundidad máxima inicial (cota inicial). Si es None, se calcula automáticamente.
            heuristic: Función heurística opcional para mejorar la poda.
            
        Returns:
            Resultado que incluye la mejor ruta encontrada junto con métricas.
        """
        # Iniciar medición de tiempo
        start_time: float = time.perf_counter()
        
        # Verificar si el estado inicial ya es objetivo
        if result := self._check_initial_goal(initial_state, start_time):
            return result
        
        # Cota inicial: si no se proporciona, usar un límite razonable
        if max_depth is None:
            # Estimación: número de colores * capacidad del tubo * factor de seguridad
            max_depth = self.game.num_colors * self.game.tube_capacity * 3
        
        # Variables para tracking
        best_solution: Optional[List[Move]] = None
        best_depth: int = max_depth
        expanded_nodes: int = 0
        max_depth_reached: int = 0
        
        def backtrack(
            state: GameState,
            path: List[Move],
            path_states: Set[GameState],
            current_bound: int
        ) -> Optional[List[Move]]:
            """Función recursiva de backtracking con poda.
            
            Args:
                state: Estado actual en la exploración.
                path: Camino desde el estado inicial hasta el estado actual.
                path_states: Conjunto de estados en el camino actual (para detectar ciclos).
                current_bound: Cota actual de profundidad.
                
            Returns:
                Mejor solución encontrada desde este estado, o None si no hay solución.
            """
            nonlocal best_solution, best_depth, expanded_nodes, max_depth_reached
            
            # Poda 1: Si ya excedimos la cota, retornar
            if len(path) >= current_bound:
                return None
            
            # Poda 2: Si usamos heurística, podar si f(n) excede la cota
            if heuristic is not None:
                estimated_total = len(path) + heuristic(state)
                if estimated_total >= current_bound:
                    return None
            
            # Contar nodo expandido
            expanded_nodes += 1
            max_depth_reached = max(max_depth_reached, len(path))
            
            # Si es estado objetivo, actualizar mejor solución
            if self.game.is_goal_state(state):
                # Encontramos una solución mejor que la cota actual
                if len(path) < best_depth:
                    best_depth = len(path)
                    best_solution = path.copy()
                return path.copy()
            
            # Variable para almacenar la mejor solución encontrada en este nivel
            local_best: Optional[List[Move]] = None
            
            # Explorar sucesores
            moves: Sequence[Move] = self.game.get_valid_moves(state)
            
            for move in moves:
                next_state: GameState = self.game.apply_move(state, move)
                
                # Evitar ciclos en el camino actual
                if next_state in path_states:
                    continue
                
                # Construir nuevo camino y conjunto de estados
                new_path = path + [move]
                new_path_states = path_states | {next_state}
                
                # Recursión con la cota actualizada
                # La cota para la búsqueda recursiva es la mejor solución encontrada hasta ahora
                result = backtrack(next_state, new_path, new_path_states, best_depth)
                
                # Si encontramos una solución en esta rama
                if result is not None:
                    # Actualizar la mejor solución local si es mejor
                    if local_best is None or len(result) < len(local_best):
                        local_best = result
                    
                    # Actualizar la cota global
                    if len(result) < best_depth:
                        best_depth = len(result)
                        best_solution = result.copy()
            
            return local_best
        
        # Ejecutar backtracking desde el estado inicial
        path_states_initial: Set[GameState] = {initial_state}
        backtrack(initial_state, [], path_states_initial, best_depth)
        
        # Retornar resultado
        if best_solution is not None:
            return self._create_success_result(
                tuple(best_solution), expanded_nodes, max_depth_reached,
                len(best_solution), start_time
            )
        else:
            # No se encontró solución dentro de la cota
            return self._create_failure_result(expanded_nodes, max_depth_reached, start_time)


"""Implementaciones de algoritmos de búsqueda para resolver Water Sort Puzzle."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Deque, Dict, Iterable, List, Optional, Protocol, Sequence, Set, Tuple

from collections import deque

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
        if self.game.is_goal_state(initial_state):
            execution_time: float = time.perf_counter() - start_time
            return SearchResult(
                path=tuple(),
                expanded_nodes=0,
                max_frontier_size=1,
                solution_depth=0,
                execution_time=execution_time,
            )

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
                    execution_time: float = time.perf_counter() - start_time
                    return SearchResult(
                        path=path,
                        expanded_nodes=expanded_nodes,
                        max_frontier_size=max_frontier_size,
                        solution_depth=next_node.depth,
                        execution_time=execution_time,
                    )

                frontier.append(next_node)
                max_frontier_size = max(max_frontier_size, len(frontier))

        # Si la búsqueda finaliza sin encontrar solución, se devuelven métricas acumuladas
        execution_time = time.perf_counter() - start_time
        return SearchResult(
            path=tuple(),
            expanded_nodes=expanded_nodes,
            max_frontier_size=max_frontier_size,
            solution_depth=-1,
            execution_time=execution_time,
        )

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

        if self.game.is_goal_state(initial_state):
            execution_time: float = time.perf_counter() - start_time
            return SearchResult(
                path=tuple(),
                expanded_nodes=0,
                max_frontier_size=1,
                solution_depth=0,
                execution_time=execution_time,
            )

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
                    execution_time: float = time.perf_counter() - start_time
                    return SearchResult(
                        path=path,
                        expanded_nodes=expanded_nodes,
                        max_frontier_size=max_frontier_size,
                        solution_depth=next_node.depth,
                        execution_time=execution_time,
                    )

                # El sucesor se apila para continuar la exploración en profundidad.
                stack.append(next_node)
                max_frontier_size = max(max_frontier_size, len(stack))

        execution_time = time.perf_counter() - start_time
        return SearchResult(
            path=tuple(),
            expanded_nodes=expanded_nodes,
            max_frontier_size=max_frontier_size,
            solution_depth=-1,
            execution_time=execution_time,
        )

    def a_star(self, initial_state: GameState, heuristic: CostHeuristic) -> SearchResult:
        """Ejecuta búsqueda A* utilizando la heurística proporcionada."""
        raise NotImplementedError("Implementar algoritmo A* con cola de prioridad")

    def ida_star(self, initial_state: GameState, heuristic: CostHeuristic) -> SearchResult:
        """Ejecuta búsqueda IDA* mejorando el límite a partir de la heurística."""
        raise NotImplementedError("Implementar algoritmo IDA* con incremento de umbral")

    def backtracking_with_bound(self, initial_state: GameState) -> SearchResult:
        """Realiza backtracking con poda basada en una cota de profundidad."""
        raise NotImplementedError("Implementar backtracking con estrategias de poda")


"""Generador de estados resolubles para el juego Water Sort Puzzle."""

from __future__ import annotations

from typing import Optional

from .water_sort_game import GameState, Move, TubeState, WaterSortGame


class PuzzleGenerator:
    """Generador responsable de construir estados iniciales resolubles."""

    def __init__(self, game: WaterSortGame) -> None:
        """Inicializa el generador con la referencia al juego."""
        self.game: WaterSortGame = game

    def generate(self, seed: Optional[int] = None) -> GameState:
        """Produce un estado inicial resoluble para el puzzle.

        Genera un estado meta (tubos uniformes y vacíos restantes) y aplica
        una secuencia de movimientos aleatorios válidos para desordenarlo.
        Al derivar el estado a partir de uno objetivo mediante movimientos
        válidos, se garantiza la resolubilidad (basta con invertir la secuencia).

        Args:
            seed: Semilla opcional para el generador aleatorio determinista.

        Returns:
            Estado inicial resoluble como tupla inmutable de tuplas (tope en índice 0).
        """
        # Importación local para evitar ciclos de importación innecesarios
        import random

        rng = random.Random(seed)

        # Construir estado objetivo: cada color ocupa un tubo completo y el resto vacíos
        # Nota: representación de tubos con el tope en el índice 0
        colors = [f"C{i}" for i in range(self.game.num_colors)]

        solved_tubes: list[TubeState] = []
        for color in colors:
            solved_tubes.append(tuple([color] * self.game.tube_capacity))

        # Tubos vacíos restantes
        empty_tubes = self.game.num_tubes - len(solved_tubes)
        if empty_tubes < 0:
            raise ValueError("El número de tubos es menor que el número de colores")

        for _ in range(empty_tubes):
            solved_tubes.append(tuple())

        state: GameState = tuple(solved_tubes)

        # Número de pasos de desorden: proporcional al tamaño del problema
        # Comentario: usar un mínimo razonable para evitar estados triviales
        min_steps = 12
        max_steps = max(min_steps, self.game.num_colors * 10)
        scramble_steps = rng.randint(max_steps // 2, max_steps)

        # Desordenar aplicando movimientos válidos aleatorios, evitando revertir inmediatamente
        last_move: Optional[Move] = None
        step = 0
        while step < scramble_steps:
            moves = list(self.game.get_valid_moves(state))
            if not moves:
                # Si no hay movimientos, reiniciar desde objetivo para garantizar progreso
                state = tuple(solved_tubes)
                last_move = None
                step = 0
                continue

            # Filtrar el movimiento inverso inmediato para diversificar
            if last_move is not None:
                # Se crea el movimiento inverso (ej. (2,5) -> (5,2))
                inv = (last_move[1], last_move[0])
                # Se crea una lista de movimientos válidos que no sean el inverso
                filtered = [m for m in moves if (m.source, m.target) != inv]
                # Si hay movimientos válidos que no sean el inverso, se actualiza la lista de movimientos
                # Si el único movimiento posible era el inverso, no se filtra nada
                if filtered:
                    moves = filtered

            # Se elige un movimiento al azar
            move = rng.choice(moves)
            # Se aplica el movimiento al estado
            state = self.game.apply_move(state, move)
            # Se actualiza el último movimiento
            last_move = (move.source, move.target)
            step += 1

        # Evitar retornar por accidente un estado objetivo
        if self.game.is_goal_state(state):
            # Forzar un último movimiento válido para salir del objetivo
            moves = list(self.game.get_valid_moves(state))
            if moves:
                state = self.game.apply_move(state, moves[0])

        return state
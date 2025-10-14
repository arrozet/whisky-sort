"""Definición de la lógica principal del juego Water Sort Puzzle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple


TubeState = Tuple[str, ...]
GameState = Tuple[TubeState, ...]


@dataclass(frozen=True)
class Move:
    """Representa un movimiento entre dos tubos."""

    source: int
    target: int


class WaterSortGame:
    """Clase que encapsula la lógica y las reglas del juego Water Sort Puzzle."""

    def __init__(self, num_tubes: int, num_colors: int, seed: Optional[int] = None) -> None:
        """Configura los parámetros del juego y prepara el estado inicial."""
        self.num_tubes: int = num_tubes
        self.num_colors: int = num_colors
        self.seed: Optional[int] = seed
        self.tube_capacity: int = 4
        # Aquí se inicializarán los generadores y estructuras auxiliares.

    def get_initial_state(self) -> GameState:
        """Genera un estado inicial aleatorio pero resoluble."""
        raise NotImplementedError("Implementar generación de estado inicial")

    def get_valid_moves(self, state: GameState) -> Sequence[Move]:
        """Calcula todos los movimientos válidos disponibles para un estado dado."""
        moves: List[Move] = []

        # Si el estado no es válido, no hay movimientos posibles
        if not self.is_valid_state(state):
            return moves

        source_index: int = 0
        # Bucle que recorre todos los tubos como posibles tubos origen
        while source_index < len(state):
            # Obtiene el tubo origen actual
            source_tube: TubeState = state[source_index]

            # Solo analiza tubos que no estén vacíos
            if source_tube:
                # Obtiene el color que está en la parte superior del tubo origen
                top_color: str = source_tube[0]

                # Inicialmente puede transferirse al menos 1 unidad (la del tope)
                transferable_units: int = 1

                # Índice para recorrer las unidades del tubo origen
                unit_index: int = 1

                # Calcula cuántas unidades consecutivas del mismo color pueden verterse
                # Esto implementa la regla de que se pueden verter bloques completos
                # del mismo color que están en la parte superior del tubo
                while unit_index < len(source_tube) and source_tube[unit_index] == top_color:
                    transferable_units += 1
                    unit_index += 1

                target_index: int = 0
                # Bucle que recorre todos los tubos como posibles tubos destino
                while target_index < len(state):
                    # Obtiene el tubo destino actual
                    target_tube: TubeState = state[target_index]

                    # 1. No se puede verter un tubo sobre sí mismo
                    is_different_tube: bool = source_index != target_index

                    # 2. El tubo destino debe estar vacío O tener el mismo color arriba
                    color_compatible: bool = not target_tube or target_tube[0] == top_color

                    # 3. Después del movimiento no debe excederse la capacidad (4 unidades)
                    # Nota: Esta condición implica automáticamente que hay espacio disponible
                    # ya que transferable_units >= 1
                    fits_capacity: bool = len(target_tube) + transferable_units <= self.tube_capacity

                    # Si todas las condiciones se cumplen, el movimiento es válido
                    if is_different_tube and color_compatible and fits_capacity:
                        moves.append(Move(source=source_index, target=target_index))

                    target_index += 1

            # Pasa al siguiente tubo origen
            source_index += 1

        return moves

    def apply_move(self, state: GameState, move: Move) -> GameState:
        """
        Aplica un movimiento válido sobre un estado y devuelve el nuevo estado resultante.

        Este método ejecuta físicamente el movimiento calculando cómo cambian los tubos
        origen y destino después de verter el bloque de líquido.

        Args:
            state: Estado actual del juego (tupla de tubos)
            move: Movimiento válido que se va a aplicar (índices origen y destino)

        Returns:
            Nuevo estado del juego después de aplicar el movimiento

        Raises:
            ValueError: Si el movimiento no es válido por alguna razón
        """
        # Validación inicial del estado
        if not self.is_valid_state(state):
            raise ValueError("El estado proporcionado no es válido")

        # Obtener referencias a los tubos involucrados
        source_tube: TubeState = state[move.source]  # Tubo del que se vierte
        target_tube: TubeState = state[move.target]  # Tubo que recibe el líquido

        # Verificar que el tubo origen no esté vacío
        if not source_tube:
            raise ValueError("El tubo de origen está vacío")

        # Identificar el bloque continuo que se puede verter
        top_color: str = source_tube[0]  # Color del tope del tubo origen
        transferable_units: int = 1  # Siempre hay al menos 1 unidad

        # Contar cuántas unidades consecutivas del mismo color hay en la parte superior
        unit_index: int = 1
        while unit_index < len(source_tube) and source_tube[unit_index] == top_color:
            transferable_units += 1  # Incrementar contador del bloque
            unit_index += 1

        # Validar que el tubo destino puede recibir el bloque
        # Regla 1: No se puede verter en un tubo completamente lleno
        if len(target_tube) == self.tube_capacity:
            raise ValueError("El tubo de destino está completo")

        # Regla 2: Si el destino tiene contenido, el color superior debe coincidir
        if target_tube and target_tube[0] != top_color:
            raise ValueError("El color superior del destino no coincide")

        # Regla 3: Verificar que no se exceda la capacidad después del movimiento
        if len(target_tube) + transferable_units > self.tube_capacity:
            raise ValueError("El movimiento excede la capacidad del tubo de destino")

        # Ejecutar físicamente el movimiento (forma inmutable)
        # Crear una copia modificable de la lista de tubos
        new_tubes: List[TubeState] = list(state)

        # Extraer el bloque que se va a transferir (desde el inicio hasta transferable_units)
        transferred_block: TubeState = source_tube[:transferable_units]

        # El tubo origen pierde las unidades transferidas (queda lo que sobra)
        updated_source: TubeState = source_tube[transferable_units:]

        # El tubo destino recibe el bloque transferido al principio (mantiene su orden)
        updated_target: TubeState = transferred_block + target_tube

        # Actualizar los tubos en la nueva configuración
        new_tubes[move.source] = updated_source
        new_tubes[move.target] = updated_target

        # Devolver el nuevo estado como tupla inmutable
        return tuple(new_tubes)

    def is_goal_state(self, state: GameState) -> bool:
        """Verifica si el estado proporcionado es un estado objetivo válido."""
        if not self.is_valid_state(state):
            return False

        tube_index: int = 0

        while tube_index < len(state):
            tube: TubeState = state[tube_index]

            # El tubo debe estar vacío o lleno (si es vacio no se hacen las comprobaciones siguientes)
            if tube:
                # El tubo debe estar lleno
                if len(tube) != self.tube_capacity:
                    return False

                # Todos los colores deben ser iguales
                if len(set(tube)) != 1:
                    return False

            tube_index += 1

        return True

    def is_valid_state(self, state: GameState) -> bool:
        """Determina si un estado cumple con las restricciones básicas del juego."""
        if len(state) != self.num_tubes:
            return False

        tube_index: int = 0

        while tube_index < len(state):
            tube: TubeState = state[tube_index]

            # El tubo debe tener una capacidad menor o igual a la capacidad del tubo
            if len(tube) <= self.tube_capacity and len(tube) > 0:
                return False

            color_index: int = 0

            while color_index < len(tube):
                color: str = tube[color_index]

                # El color debe ser una cadena de caracteres
                if not isinstance(color, str):
                    return False

                color_index += 1

            tube_index += 1

        return True

    def iterate_colors(self, state: GameState) -> Iterable[str]:
        """Itera sobre todas las unidades de color presentes en un estado."""
        return self._iterate_colors(state)

    def _iterate_colors(self, state: GameState) -> Iterator[str]:
        """Generador interno que produce las unidades de color del estado."""
        tube_index: int = 0

        # Recorre cada tubo del estado
        while tube_index < len(state):
            tube: TubeState = state[tube_index]

            # Extrae cada unidad de color del tubo actual
            color_index: int = 0
            while color_index < len(tube):
                # Produce la unidad de color individual
                yield tube[color_index]   # es un return de la funcion, pero cada vez que se llama a la funcion, se devuelve el siguiente elemento de la lista
                color_index += 1

            tube_index += 1


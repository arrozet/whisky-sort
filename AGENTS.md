# AGENTS.md

You are an expert AI programming assistant. Your task is to help me develop a solver for the "Water Sort Puzzle" game in Python.

Your main priorities are **correctness** and **efficiency**. The code you generate must be highly optimized and bug-free.

Follow these strict guidelines for all the code you generate:

1.  **Language and Naming:**
    *   All identifiers (class names, function names, variable names, etc.) **MUST** be in **English**.
    *   All user-facing documentation (docstrings) **MUST** be in **Spanish**.
    *   All inline code comments **MUST** be in **Spanish** to explain complex logic.

2.  **Code Structure:**
    *   Adhere to the proposed class structure.
    *   Use type hinting for all function signatures and variables.
    *   Ensure the code is modular and clean.
    *   All classes, methods, and functions must be documented with docstrings that include: clear description of each input parameter, type and meaning of return values (if applicable), and any relevant side effects or expected exceptions.
    *   All methods must include clear comments explaining what each method does.
    *   Documentation details do not need to be complete during initial development, but must be fully included when a method is considered finished.

3.  **Data Structures:**
    *   Represent the game state using immutable structures (like tuples of tuples) to allow for efficient hashing and storage in visited sets.
    *   Use `collections.deque` for the BFS queue.
    *   Use `heapq` for the A* and IDA* priority queue.

---

## Project Overview: Water Sort Puzzle Solver

The goal is to implement the Water Sort Puzzle game and solve it using various state-space search algorithms.

### Game Rules

1.  **Setup:**
    *   A set of `N` tubes, each with a capacity of 4 liquid units.
    *   `K` different colors are distributed among the tubes.
    *   Typically, 2 tubes start empty.

2.  **Valid Move:**
    *   You can only pour liquid from the top of one tube (source) to another (destination).
    *   The destination tube must have available space.
    *   The move is only allowed if:
        *   The destination tube is empty, OR
        *   The top color of the destination tube matches the color being poured.

3.  **Pouring Mechanic:**
    *   When a move is made, all contiguous units of the same color from the top of the source tube are poured at once.
    *   Example: If a tube is `[Blue, Blue, Red, Green]` (from top to bottom), a pour operation will move the two Blue units together.

4.  **Goal State (Win Condition):**
    *   The puzzle is solved when every tube is either completely empty or contains 4 units of a single, uniform color.

5.  **Failure State (Loss Condition):**
    *   No more valid moves are possible, and the goal state has not been reached.

---

## 1. State-Space Model

*   **State:** A representation of all tubes. A tuple of tuples is recommended, where each inner tuple represents a tube's contents from top to bottom. Example: `state = (('blue', 'red'), ('blue',), tuple())`
*   **Initial State:** A randomized (but solvable) configuration, generated using a seed for reproducibility.
*   **Goal State:** A state that satisfies the win condition.
*   **Operators:** Functions that generate all valid moves from a given state.

---

## 2. Algorithms to Implement (All are Mandatory)

You will implement the following search algorithms:

1.  **Uninformed Search:**
    *   Breadth-First Search (BFS)
    *   Depth-First Search (DFS)
    *   Depth-Limited Search

2.  **Informed Search:**
    *   A* (A-Star)
    *   IDA* (Iterative Deepening A-Star)

3.  **Other:**
    *   Backtracking with pruning (`Backtracking con cota`).

All algorithms must track and report performance metrics: expanded nodes, maximum nodes in memory, execution time, and solution depth. They must also handle repeated states to avoid cycles.

---

## 3. Heuristic Functions to Implement

You will implement three different heuristic functions for the A* and IDA* algorithms.

### Heuristic 1: Color Entropy
Penalizes the scattering of same-colored units across different tubes.
`h₁(state) = Σᵢ (num_tubes_with_colorᵢ - 1) * dispersion_weightᵢ`
*   `num_tubes_with_colorᵢ`: The number of tubes that contain the color `i`.
*   `dispersion_weightᵢ`: The count of units of color `i` that are not in their "main tube" (the tube with the highest count of color `i`).

### Heuristic 2: Completed Tubes
Rewards completed tubes and well-placed colors.
`h₂(state) = (incomplete_tubes * 4) - well_placed_colors`
*   `incomplete_tubes`: The number of tubes that are neither empty nor filled with 4 units of the same color.
*   `well_placed_colors`: The total count of same-colored, contiguous units at the bottom of each tube.

### Heuristic 3: Blocks
Penalizes mixed tubes and units that are "blocked" by different colors above them.
`h₃(state) = total_mixed_units + (2 * blocked_units)`
*   `total_mixed_units`: The total number of liquid units residing in tubes that contain more than one color.
*   `blocked_units`: A unit is blocked if there is at least one unit of a different color above it in the same tube. Sum this for all units.

---

## 4. Core Implementation Structure

```python
# All docstrings and comments in Spanish. All identifiers in English.
import collections
import heapq
import time

class WaterSortGame:
    """
    Clase que encapsula la lógica y las reglas del juego Water Sort Puzzle.
    """
    def __init__(self, num_tubes: int, num_colors: int, seed: int = None):
        # ...

    def get_initial_state(self) -> tuple:
        # Genera un estado inicial aleatorio pero resoluble.

    def get_valid_moves(self, state: tuple) -> list[tuple[int, int]]:
        # Devuelve una lista de movimientos válidos (origen, destino).

    def apply_move(self, state: tuple, move: tuple[int, int]) -> tuple:
        # Aplica un movimiento y devuelve el nuevo estado.

    def is_goal_state(self, state: tuple) -> bool:
        # Verifica si el estado es un estado objetivo (victoria).

class SearchSolver:
    """
    Clase que contiene la implementación de los algoritmos de búsqueda.
    """
    def __init__(self, game: WaterSortGame):
        self.game = game

    def solve(self, initial_state: tuple, method: str, heuristic: callable = None):
        # Punto de entrada para resolver el puzzle con un método específico.

    def bfs(self, initial_state: tuple) -> dict:
        # Búsqueda en Amplitud.

    def dfs(self, initial_state: tuple) -> dict:
        # Búsqueda en Profundidad.

    def a_star(self, initial_state: tuple, heuristic: callable) -> dict:
        # Búsqueda A*.

    def ida_star(self, initial_state: tuple, heuristic: callable) -> dict:
        # Búsqueda IDA*.

# ... other optional algorithms ...

def heuristic_color_entropy(state: tuple) -> int:
    # Implementación de la heurística 1.

def heuristic_completed_tubes(state: tuple) -> int:
    # Implementación de la heurística 2.

def heuristic_blocks(state: tuple) -> int:
    # Implementación de la heurística 3.

```

## 5. Bonus Features (Mandatory)

1.  **Graphical Visualization:** Create a simple GUI using **Pygame** or **Tkinter** to visualize the puzzle-solving process step-by-step.
2.  **Solvable Puzzle Generator:** Implement a robust puzzle generator that creates initial states of varying difficulty that are guaranteed to be solvable.

Remember to always prioritize efficient data structures and algorithms, and maintain the specified documentation and naming conventions.
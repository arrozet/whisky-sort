# Water Sort Puzzle Solver

Solver para el juego Water Sort Puzzle utilizando algoritmos de búsqueda en espacio de estados. Implementado como práctica del curso de Inteligencia Artificial para Juegos.

## 🎮 Descripción

El Water Sort Puzzle es un rompecabezas lógico donde el jugador debe organizar líquidos de diferentes colores en tubos de ensayo hasta que cada tubo contenga un único color o esté vacío.

Este proyecto implementa varios algoritmos de búsqueda para resolver automáticamente el puzzle:
- **BFS** (Breadth-First Search)
- **DFS** (Depth-First Search)
- **DLS** (Depth-Limited Search)
- **A*** con 3 heurísticas diferentes
- **IDA*** (Iterative Deepening A*) con 3 heurísticas diferentes
- **Backtracking con Cota** (con o sin heurística)

## 📋 Requisitos

- Python 3.9+
- No requiere dependencias externas (solo bibliotecas estándar)

## 🚀 Instalación

```bash
git clone https://github.com/tu-usuario/whisky-sort.git
cd whisky-sort
```

## 💻 Uso

### Uso Básico

```bash
# Resolver con BFS (por defecto)
python -m src

# Resolver con algoritmo específico
python -m src --algorithm bfs --tubes 5 --colors 3 --seed 42

# Resolver con A* y heurística 2
python -m src --algorithm astar --heuristic h2 --tubes 6 --colors 4

# Resolver con IDA* y heurística 2 (usa menos memoria)
python -m src --algorithm idastar --heuristic h2 --tubes 6 --colors 4

# Resolver con Backtracking + heurística (busca mejor solución)
python -m src --algorithm backtracking --heuristic h2 --tubes 5 --colors 3

# Ver la solución paso a paso
python -m src --algorithm astar --heuristic h2 --show-steps --seed 42
```

### Comparar Algoritmos

```bash
# Comparar todos los algoritmos en el mismo puzzle
python -m src --compare --tubes 5 --colors 3 --seed 42
```

### Opciones Disponibles

#### Configuración del Juego
- `--tubes, -t N`: Número de tubos (default: 5)
- `--colors, -c N`: Número de colores (default: 3)
- `--seed, -s N`: Semilla para reproducibilidad

#### Algoritmos
- `--algorithm, -a ALGO`: Algoritmo a usar
  - `bfs`: Búsqueda en Amplitud
  - `dfs`: Búsqueda en Profundidad
  - `dls`: Búsqueda en Profundidad Limitada
  - `astar` o `a*`: Búsqueda A*
  - `idastar` o `ida*`: Búsqueda IDA*
  - `backtracking` o `bt`: Backtracking con Cota

#### Heurísticas (para A*, IDA* y Backtracking)
- `--heuristic, -H HEUR`: Heurística a usar
  - `h1` o `entropy`: Entropía de colores
  - `h2` o `completed`: Tubos completados
  - `h3` o `blocks`: Bloqueos y mezclas
  - Nota: Backtracking puede ejecutarse con o sin heurística

#### Visualización
- `--show-steps`: Mostrar solución paso a paso
- `--show-initial`: Mostrar estado inicial
- `--show-final`: Mostrar estado final
- `--verbose, -v`: Información detallada
- `--quiet, -q`: Solo resultados finales

#### Modos Especiales
- `--compare`: Comparar todos los algoritmos
- `--benchmark N`: Ejecutar N veces y promediar

## 📊 Ejemplo de Salida

```
======================================================================
WATER SORT PUZZLE SOLVER
======================================================================

Configuracion:
  - Tubos: 5
  - Colores: 3
  - Semilla: 42

Estado Inicial:
   [ C2 ] [ C1 ] [    ] [    ] [ C1 ] 
   [ C1 ] [ C0 ] [    ] [    ] [ C1 ] 
   [ C2 ] [ C0 ] [    ] [    ] [ C0 ] 
   [ C0 ] [ C2 ] [    ] [    ] [ C2 ] 
     T0     T1     T2     T3     T4   

>> Ejecutando ASTAR...
   Usando heuristica: h2

======================================================================
Algoritmo: ASTAR + H2
======================================================================
[OK] Solucion encontrada!
  - Profundidad de la solucion: 8
  - Movimientos en la solucion: 8
  - Nodos expandidos: 28
  - Maximo de nodos en memoria: 81
  - Tiempo de ejecucion: 0.0012 segundos
```

## 🧪 Pruebas

```bash
# Ejecutar pruebas de A*
python test_astar.py

# Ejecutar pruebas de IDA*
python test_idastar.py

# Ejecutar pruebas de Backtracking
python test_backtracking.py

# Demo de visualización
python demo_visualization.py
```

## 🏗️ Estructura del Proyecto

```
whisky-sort/
├── src/
│   ├── __init__.py
│   ├── __main__.py           # Punto de entrada CLI
│   ├── water_sort_game.py    # Lógica del juego
│   ├── search_solver.py      # Algoritmos de búsqueda
│   ├── heuristics.py         # Funciones heurísticas
│   ├── generator.py          # Generador de puzzles
│   └── gui.py                # GUI (próximamente)
├── test_astar.py             # Tests de A*
├── demo_visualization.py     # Demo de visualización
└── README.md
```

## 📖 Heurísticas Implementadas

### H1: Entropía de Colores
Penaliza la dispersión de colores en múltiples tubos.
```
h₁(estado) = Σᵢ (num_tubos_con_colorᵢ - 1) × peso_dispersiónᵢ
```

### H2: Tubos Completados
Recompensa tubos completados y colores bien ubicados.
```
h₂(estado) = (tubos_incompletos × 4) - colores_bien_posicionados
```

### H3: Bloqueos
Penaliza mezclas y unidades bloqueadas.
```
h₃(estado) = total_unidades_mezcladas + (2 × unidades_bloqueadas)
```

## 🎯 Resultados

En pruebas con puzzles de 5 tubos y 3 colores (seed=42):

| Algoritmo     | Profundidad | Nodos Expandidos | Max Memoria/Prof | Tiempo (s) |
|---------------|-------------|------------------|------------------|------------|
| BFS           | 8 (óptimo)  | 518              | 321              | 0.0115     |
| DFS           | 38          | 38               | 91               | 0.0010     |
| A* + H1       | 9           | 18               | 54               | 0.0009     |
| A* + H2       | 8 (óptimo)  | 28               | 81               | 0.0011     |
| A* + H3       | 9           | 17               | 48               | 0.0006     |
| IDA* + H1     | 13          | 15               | 13               | 0.0005     |
| IDA* + H2     | 10          | 19               | 13               | 0.0005     |
| IDA* + H3     | 42          | 45               | 42               | 0.0008     |
| BT (sin h)    | 8 (óptimo)  | 86,965           | 35               | 2.5174     |
| BT + H2       | 12          | 48               | 32               | 0.0017     |

**Observaciones:**
- **BFS, A*+H2 y BT (sin h)** encuentran la solución óptima (8 movimientos)
- **IDA*** usa significativamente menos memoria que A* (profundidad vs cola completa)
- **A*+H2** ofrece el mejor balance entre optimalidad y eficiencia
- **IDA*+H2** es ideal cuando la memoria es limitada
- **Backtracking sin heurística** encuentra el óptimo pero expande muchos nodos
- **Backtracking con heurística** es mucho más eficiente pero puede ser sub-óptimo

## 👥 Autores

Proyecto desarrollado como práctica del curso de Inteligencia Artificial para Juegos.

## 📄 Licencia

Ver archivo `LICENSE` para más detalles.

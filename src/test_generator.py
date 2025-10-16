# test_generator.py

# 1. Importa la clase principal del juego
from .water_sort_game import WaterSortGame

def pretty_print_state(state):
    """Función auxiliar para imprimir el estado del juego de forma bonita."""
    print("--- ESTADO DEL JUEGO GENERADO ---")
    if not state:
        print("Estado vacío.")
        return

    # Busca la altura máxima de un tubo para alinear la impresión
    max_height = 0
    for tube in state:
        if len(tube) > max_height:
            max_height = len(tube)

    # Imprime el estado nivel por nivel, de arriba a abajo
    for i in range(max_height):
        line = ""
        for tube in state:
            if i < len(tube):
                line += f"| {tube[i]} |  "
            else:
                line += "|    |  "
        print(line)

    # Imprime la base de los tubos
    base = ""
    for i in range(len(state)):
        base += f"'-T{i}-'  "
    print(base)
    print("---------------------------------")


# --- PUNTO DE ENTRADA PRINCIPAL ---
if __name__ == "__main__":
    # 2. Configura los parámetros del juego que quieres probar
    # Por ejemplo: 5 tubos en total, 3 colores diferentes.
    # La capacidad de los tubos está fija en 4 dentro de la clase.
    NUM_TUBOS = 5
    NUM_COLORES = 3

    print(f"Creando un juego con {NUM_TUBOS} tubos y {NUM_COLORES} colores.")

    # 3. Crea una instancia del juego
    # Le pasamos una semilla (seed=42) para que el resultado sea siempre el mismo
    # y podamos verificarlo. Si quieres uno diferente cada vez, pon seed=None.
    game = WaterSortGame(num_tubes=NUM_TUBOS, num_colors=NUM_COLORES, seed=42)

    # 4. Llama a la función que genera el estado inicial
    # Esta función, a su vez, llamará a tu PuzzleGenerator.generate()
    initial_state = game.get_initial_state()

    # 5. Imprime el resultado en la terminal
    pretty_print_state(initial_state)
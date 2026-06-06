"""Pipeline de procesamiento en paralelo para datos de matrices de 
diferencia a un dataset de vectores de diferencia.

Este script expone una interfaz de línea de comandos (CLI) para orquestar
la generación de matrices de correlación de múltiples sujetos de manera
concurrente utilizando un pool de procesos distribuidos.

Ejemplo de uso:
    $ uv run /scripts/diff_to_dataset_pipeline.py --input-dir /data/intermediate_data/diff_matrices --output-dir /data/intermediate_data/vector_diff_datasets
"""

import argparse
import multiprocessing as mp
from pathlib import Path
import time
from tesis.tools import procesamiento_paralelo_por_sujeto
from tesis.features import vectores_diff_pipeline


def parse_args() -> argparse.Namespace:
    """Parsea los argumentos de la línea de comandos.

    Returns:
        argparse.Namespace: Un objeto que contiene los argumentos parseados:
            - raw_dir (Path): Ruta al directorio de origen de los datos.
            - intermediate_dir (Path): Ruta al directorio para los resultados.
            - workers (int): Número de procesos paralelos a ejecutar.
    """
    parser = argparse.ArgumentParser(
        description="Pipeline de transformacion de matrices de diferencia a un dataset de vectores de diferencia"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directorio de origen (matrices de diferencia)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directorio de salida (dataset de vectores)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, mp.cpu_count() - 1),
        help="Número de procesos paralelos (por defecto: CPU_count - 1)",
    )
    return parser.parse_args()


def main() -> None:
    """Función principal que orquesta el procesamiento paralelo de los sujetos.

    Lee los sujetos disponibles en el directorio de entrada, levanta un
    pool de procesos concurrentes empleando `ProcessPoolExecutor` y gestiona
    las excepciones individuales de cada tarea sin detener el pipeline entero.
    """
    inicio = time.perf_counter() #Inicia el tiempo de ejecución
    args = parse_args()

    # Obtiene y ordena la lista de carpetas de sujetos disponibles
    lista_sujetos = sorted(p.name for p in args.input_dir.iterdir() if p.is_dir())

    print(f"Iniciando procesamiento de {len(lista_sujetos)} sujetos...")
    print(f"Workers activos: {args.workers}")

    procesamiento_paralelo_por_sujeto(lista_sujetos= lista_sujetos,
                                      funcion_sujeto= vectores_diff_pipeline,
                                      workers= args.workers,
                                      paths=(args.input_dir, args.output_dir),
                                      )

    # Imprimir en el tiempo de ejecución en segundos
    fin = time.perf_counter()
    tiempo_total = fin - inicio
    print(f"El script tardó {tiempo_total:.4f} segundos en ejecutarse.")


if __name__ == "__main__":
    main()
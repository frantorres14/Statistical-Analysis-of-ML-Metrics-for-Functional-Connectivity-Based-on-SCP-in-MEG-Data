"""Pipeline de procesamiento en paralelo para datos MEG del HCP.

Este script expone una interfaz de línea de comandos (CLI) para orquestar
el preprocesamiento de múltiples sujetos de manera concurrente utilizando
un pool de procesos distribuidos.

Ejemplo de uso:
    $ uv run scripts/filter_trial_pipeline.py --raw-dir ./data/raw_data --intermediate-dir ./data/intermediate_data/filtered_data
"""

import argparse
import multiprocessing as mp
from pathlib import Path
import time
from tesis.preprocess import filtrar_sujeto_pipeline
from tesis.tools import procesamiento_paralelo_por_sujeto, obtener_lista_sujetos


def parse_args() -> argparse.Namespace:
    """Parsea los argumentos de la línea de comandos.

    Returns:
        argparse.Namespace: Un objeto que contiene los argumentos parseados:
            - raw_dir (Path): Ruta al directorio de origen con datos crudos.
            - intermediate_dir (Path): Ruta al directorio para los resultados.
            - workers (int): Número de procesos paralelos a ejecutar.
    """
    parser = argparse.ArgumentParser(
        description="Pipeline de Preprocesamiento MEG - HCP"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directorio de datos raw (origen)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directorio de salida (datos filtrados)",
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
    lista_sujetos = obtener_lista_sujetos(args.input_dir)

    print(f"Iniciando procesamiento de {len(lista_sujetos)} sujetos...")
    print(f"Workers activos: {args.workers}")

    procesamiento_paralelo_por_sujeto(lista_sujetos= lista_sujetos,
                                      funcion_sujeto= filtrar_sujeto_pipeline,
                                      workers= args.workers,
                                      paths=(args.input_dir, args.output_dir),
                                      )

    # Imprimir en el tiempo de ejecución en segundos
    fin = time.perf_counter()
    tiempo_total = fin - inicio
    print(f"El script tardó {tiempo_total:.4f} segundos en ejecutarse.")


if __name__ == "__main__":
    main()
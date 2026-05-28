"""Pipeline de procesamiento en paralelo para datos MEG del HCP.

Este script expone una interfaz de línea de comandos (CLI) para orquestar
el preprocesamiento de múltiples sujetos de manera concurrente utilizando
un pool de procesos distribuidos.

Ejemplo de uso:
    $ uv run script/preprocess_meg_data.py --raw-dir ./data/raw_data --intermediate-dir ./data/intermediate_data
"""

import argparse
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import time
from tesis.preprocess import procesar_sujeto


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
        "--raw-dir",
        type=Path,
        required=True,
        help="Directorio de datos raw (origen)",
    )
    parser.add_argument(
        "--intermediate-dir",
        type=Path,
        required=True,
        help="Directorio de salida (datos intermedios)",
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
    lista_sujetos = sorted(p.name for p in args.raw_dir.iterdir() if p.is_dir())

    print(f"Iniciando procesamiento de {len(lista_sujetos)} sujetos...")
    print(f"Workers activos: {args.workers}")

    # Inicialización del contexto de procesamiento paralelo
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Mapea cada futuro con su respectivo identificador de sujeto
        futures = {
            executor.submit(
                procesar_sujeto, sujeto, args.raw_dir, args.intermediate_dir
            ): sujeto
            for sujeto in lista_sujetos
        }

        # Procesa los resultados a medida que van finalizando (asíncrono)
        for future in as_completed(futures):
            sujeto = futures[future]
            try:
                # Captura el retorno exitoso de la función `procesar_sujeto`
                print(future.result())
            except Exception as e:
                # Evita que un error en un sujeto tire abajo todo el pipeline
                print(f"[ERROR crítico en {sujeto}]: {e}")

    # Imprimir en el tiempo de ejecución en segundos
    fin = time.perf_counter()
    tiempo_total = fin - inicio
    print(f"El script tardó {tiempo_total:.4f} segundos en ejecutarse.")


if __name__ == "__main__":
    main()
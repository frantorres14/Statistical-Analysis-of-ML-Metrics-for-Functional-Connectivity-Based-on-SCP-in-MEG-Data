from pathlib import Path
from typing import List

import argparse
import pandas as pd


def limpiar_dataset(df: pd.DataFrame, folder_name: str,file_name: str) -> pd.DataFrame:
    """
    Limpia un DataFrame siguiendo las reglas definidas.
    """
    # Se hace una copia para evitar advertencias de pandas sobre la asignación en vistas
    df = df.copy()

    # Se eliminan las columnas que no son necesarias
    if "run" in df.columns:
        df = df.loc[~df["run"].astype(str).isin({"3", "5"})].copy()

    # Se reemplazan los valores nulos en las columnas 'type_task' y 'type_ref' con "Restin"
    df["type_task"] = df["type_task"].fillna("Restin")
    df["type_ref"] = df["type_ref"].fillna("Restin")
    # Se filtran los registros para mantener solo aquellos con 'type_ref' en {"Restin", "TIM", "TFLA"}
    df = df.loc[df["type_ref"].isin({"Restin", "TIM", "TFLA"})].copy()

    return df


def obtener_parquets(carpeta: Path, dataset_type: str) -> List[Path]:
    """
    Obtiene los parquets válidos dependiendo del tipo de dataset.
    """
    archivos = sorted(carpeta.glob("*.parquet"))

    if dataset_type == "corr":
        return archivos

    if dataset_type == "diff":
        # Se filtran los archivos que contienen "tim-tfla" en su nombre, ignorando mayúsculas y minúsculas
        return [archivo for archivo in archivos if "tim-tfla" in archivo.stem.lower()]

    raise ValueError(f"Tipo de dataset desconocido: {dataset_type}")


def procesar_carpetas(
    input_dir: Path,
    dataset_type: str,
) -> pd.DataFrame:
    """
    Recorre todas las subcarpetas y concatena los datasets.
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"No existe {input_dir}")

    # Se obtienen y ordenan las carpetas dentro del directorio de entrada
    carpetas = sorted(carpeta for carpeta in input_dir.iterdir() if carpeta.is_dir())

    dfs = []

    for carpeta in carpetas:

        parquet_files = obtener_parquets(carpeta,dataset_type)

        if not parquet_files:
            continue

        for archivo in parquet_files:

            df = pd.read_parquet(archivo)

            df = limpiar_dataset(df=df, folder_name=carpeta.name, file_name=archivo.name)

            dfs.append(df)

    if not dfs:
        raise RuntimeError("No se encontraron datasets para concatenar.")

    return pd.concat(dfs, ignore_index=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Limpieza y concatenación de datasets vectoriales."
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Ruta a vector_corr_datasets o vector_diff_datasets.",
    )

    parser.add_argument(
        "--output-file",
        type=Path,
        required=True,
        help="Ruta del parquet de salida.",
    )

    parser.add_argument(
        "--dataset-type",
        choices=["corr", "diff"],
        required=True,
        help="Tipo de dataset.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    args.output_file.parent.mkdir(parents=True,exist_ok=True,)

    df = procesar_carpetas(input_dir=args.input_dir, dataset_type=args.dataset_type)

    df.to_parquet(args.output_file,index=False)


if __name__ == "__main__":
    main()
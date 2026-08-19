from typing import Callable, List
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
import re
import pyarrow as pa
import pyarrow.parquet as pq
from dataclasses import dataclass
import numpy as np

def obtener_lista_sujetos(path: Path) -> list[Path]:
    """
    Obtiene una directorio y regresa la lista de carpetas dentro.
    Las carpetas deberían de ser identificadores de los sujetos
    de prueba del HCP.
    
    Args:
        path: Un Path donde deberían de estar las carpetas por sujeto
    
    returns: Una lista con los directorios de las carpetas en el directorio
        de entrada.
    """
    return sorted(p.name for p in path.iterdir() if p.is_dir())


@dataclass
class MetadataArchivo:
    """Almacena los metadatos extraídos de los nombres de los archivos del pipeline.

    Esta estructura de datos unifica la información proveniente tanto de archivos
    crudos (.mat) como de archivos procesados (.parquet), permitiendo un manejo
    homogéneo a lo largo del pipeline de datos.

    Attributes:
        sujeto (str): Identificador único del sujeto (ej. "105923").
        run (str): Número de la corrida o bloque de adquisición (ej. "6").
        task (str): Nombre de la tarea realizada (ej. "Wrkmem", "Restin").
        trial_id (int): Identificador del ensayo específico (ej. "14"). 
        type_task (str | None): Subtipo o condición de la tarea 
            (ej. "0-back", "2-back"). Defaults to "".
        type_ref (str | None): Tipo de referencia o métrica específica 
            de la tarea. Puede no estar presente (ej. "TIM", "TRESP"). Defaults to None.
        process (str): Etapa o tipo de procesamiento aplicado 
            (ej. "filtered", "corr"). Defaults to "".
        instrumento (str): Equipo o modalidad de adquisición. 
            Defaults to "MEG".
        preproc_base (str): Software o método base de preprocesamiento 
            (ej. "tmegpreproc", "rmegpreproc"). Defaults to "".

    """
    sujeto: str
    run: str
    task: str
    trial_id: str | None = None
    type_task: str | None = None
    type_ref: str | None = None
    process: str = ""
    instrumento: str = "MEG"
    preproc_base: str = ""

PATRON_RAW = re.compile(
    r"^(?P<sujeto>\d+)_"
    r"(?P<instrumento>[A-Za-z]+)_"
    r"(?P<run>\d+)-(?P<task>[A-Za-z0-9]+)_"
    r"(?P<preproc_base>[a-z]+)"
    r"(?:_(?P<type_ref>[A-Za-z]+))?\.mat$"
)


def metadata_nombre_raw(nombre_archivo: str) -> MetadataArchivo:
    """Extrae metadatos de un archivo MEG .mat a partir de su nombre.

    Analiza el nombre del archivo proporcionado utilizando expresiones regulares
    para determinar su estructura. Soporta formatos de archivos crudos (.mat) 
    y archivos procesados (.parquet). Los campos opcionales que no se encuentren
    en el nombre del archivo se asignarán de manera segura como `None` o strings vacíos.

    Args:
        nombre_archivo (str): El nombre del archivo del cual se extraerán los metadatos.

    Returns:
        MetadataArchivo: Un objeto dataclass instanciado con los metadatos 
        extraídos del nombre del archivo.

    Raises:
        TypeError: Si el argumento `nombre_archivo` no es una cadena de texto.
        ValueError: Si el nombre del archivo no coincide con ninguno de los 
            patrones esperados (crudo o procesado).
        RuntimeError: Si ocurre un error inesperado durante el procesamiento.
    """
    # Validación de tipos de entrada
    if not isinstance(nombre_archivo, str):
        raise TypeError(f"Se esperaba un string, se recibió: {type(nombre_archivo).__name__}")

    try:
        # 2. Intentamos leerlo como archivo crudo (.mat)
        match_crudo = PATRON_RAW.search(nombre_archivo)
        if match_crudo:
            datos = match_crudo.groupdict()
            return MetadataArchivo(
                sujeto=datos.get("sujeto", ""),
                instrumento=datos.get("instrumento", ""),
                run=datos.get("run", ""),
                task=datos.get("task", ""),
                preproc_base=datos.get("preproc_base", ""),
                type_ref=datos.get("type_ref"), # Devuelve None si no existe
            )

        # Manejo de error si no coincide con ningún patrón
        raise ValueError(f"El archivo '{nombre_archivo}' no cumple con los patrones esperados.")

    except ValueError:
        # Relanzamos el ValueError explícitamente para que sea atrapado más arriba
        raise
    except Exception as e:
        # Capturamos otros errores inesperados (ej. problemas de memoria) de forma nativa
        raise RuntimeError(f"Error inesperado procesando '{nombre_archivo}': {e}") from e


def guardar_procesamiento_parquet(
    df: pd.DataFrame,
    path_archivo: Path,
    subfijo_proceso: str,
    metadata: MetadataArchivo,
    path_save: Path,
) -> None:
    """Exporta el DataFrame a un archivo Parquet inyectando la dataclass como metadatos.

    Genera el nombre del archivo dinámicamente basándose en los metadatos actuales,
    añade el sufijo del nuevo proceso y guarda el DataFrame en formato Parquet 
    preservando tanto los metadatos internos de Pandas como los metadatos 
    personalizados del pipeline.

    Args:
        df (pd.DataFrame): Los datos procesados que se desean guardar.
        path_archivo (str): Path del archivo ancestro del que provienen los datos.
        subfijo_proceso (str): Identificador del proceso actual (ej. "filtered", "corr").
        metadata (MetadataArchivo): Objeto con los metadatos extraídos de pasos previos.
        path_save (Path): Ruta del directorio base donde se guardará el nuevo archivo.

    Returns:
        None
    """
    # Se actualiza el proceso actual en los metadatos
    metadata.process = subfijo_proceso

    # Se crea el nuevo nombre dependiendo de los metadatos
    subfijos = [metadata.sujeto, metadata.run, metadata.task]
    if metadata.type_ref:
        subfijos.append(metadata.type_ref)
    if metadata.type_task:
        subfijos.append(metadata.type_task)
    subfijos.extend([metadata.process, metadata.trial_id])
    
    archivo_name = f"{'_'.join(s for s in subfijos if s)}.parquet"
    ruta_guardar = path_save / archivo_name

    # Conversión de DataFrame a PyArrow Table
    table = pa.Table.from_pandas(df, preserve_index=True) # IMPORTANTE: para guardar los índices de las correlaciones

    # Mapeo de la clase MetadataArchivo a un diccionario de bytes
    custom_metadata = {
        b"archivo_ancestro": path_archivo.name.encode("utf-8"),
        b"sujeto": metadata.sujeto.encode("utf-8"),
        b"run": metadata.run.encode("utf-8"),
        b"task": metadata.task.encode("utf-8"),
        b"type_ref": (metadata.type_ref or "none").encode("utf-8"), 
        b"type_task": (metadata.type_task or "none").encode("utf-8"),
        b"trial_id": metadata.trial_id.encode("utf-8"),
        b"process": metadata.process.encode("utf-8"),
        b"instrumento": metadata.instrumento.encode("utf-8"),
        b"preproc_base": metadata.preproc_base.encode("utf-8"),
    }

    # Se recuperan los metadatos de pandas (esquema de datos, índices) y se combinan
    # con los que se están guardando
    existing_metadata = table.schema.metadata or {}
    final_metadata = {**existing_metadata, **custom_metadata}
    table = table.replace_schema_metadata(final_metadata)

    # Se guarda el archivo
    pq.write_table(table, ruta_guardar, compression="snappy")


def obtener_metadatos_parquet(ruta_archivo: Path) -> MetadataArchivo:
    """Lee exclusivamente los metadatos personalizados de un archivo Parquet.
    
    Args:
        ruta_archivo (Path): Ruta al archivo .parquet.
        
    Returns:
        MetadataArchivo: Clase con atributos y valores de metadatos en formato string.
    """
    # Leer solo el archivo de metadatos (muy rápido, no carga los datos)
    metadata_archivo = pq.read_metadata(ruta_archivo)
    
    # Los metadatos de la tabla combinan los de Pandas y los tuyos personalizados
    metadata_bytes = metadata_archivo.metadata or {}
    
    # Decodificamos de bytes a string (filtrando metadatos del sistema como los de Pandas)
    metadata_dict = {}
    for k, v in metadata_bytes.items():
        clave = k.decode("utf-8")
        # Opcional: Evitamos traer el esquema interno que mete Pandas automáticamente
        if clave != "pandas" and clave != "ARROW:schema":
            metadata_dict[clave] = v.decode("utf-8")

    # Convertir el diccionario a objeto MetadataArchivo
    metadata = MetadataArchivo(
        sujeto=metadata_dict.get("sujeto", ""),
        run=metadata_dict.get("run", ""),
        task=metadata_dict.get("task", ""),
        trial_id=metadata_dict.get("trial_id"),
        type_task=metadata_dict.get("type_task") if metadata_dict.get("type_task") != "none" else None,
        type_ref=metadata_dict.get("type_ref") if metadata_dict.get("type_ref") != "none" else None,
        process=metadata_dict.get("process", ""),
        instrumento=metadata_dict.get("instrumento", "MEG"),
        preproc_base=metadata_dict.get("preproc_base", ""),
    )
            
    return metadata


def procesamiento_paralelo_por_sujeto(lista_sujetos: List[str],
                                   funcion_sujeto: Callable,
                                   workers: int,
                                   paths: tuple[Path, ...],
                                    ):
    
    # Inicialización del contexto de procesamiento paralelo        
    with ProcessPoolExecutor(max_workers=workers) as executor:
        # Mapea cada futuro con su respectivo identificador de sujeto
        futures = {
            executor.submit(
                funcion_sujeto, sujeto, *paths)
                :sujeto for sujeto in lista_sujetos
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


import pandas as pd


def process_accuracy_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma y resume un DataFrame extracto de métricas por modelo y conjunto de datos.

    Filtra las columnas relativas a 'accuracy_group', itera sobre los modelos
    y datasets presentes en el DataFrame de entrada y genera una nueva estructura
    pivotada con los resultados limpios por sujeto.

    Parameters
    df : pd.DataFrame
        DataFrame de origen que debe contener al menos las columnas 'model',
        'data_name' y una o más columnas cuyo nombre empiece con 'accuracy_group'.

    Returns
    pd.DataFrame
        Un DataFrame reestructurado donde cada fila representa un sujeto
        asociado a un modelo específico, mostrando los valores correspondientes
        a cada accuracy de cada dataset en columnas independientes.
    """
    data = []

    # Se extraen los nombres de las columnas de los accuracy
    accuracy_group_cols = [
        col for col in df.columns if col.startswith("accuracy_group")
    ]

    # Se extraen los accuracy de cada sujeto por dataset y por modelo
    for model in df["model"].unique():
        for group in accuracy_group_cols:
            fila = {}
            group_name = group.split("_")[-1]
            fila["sujeto"] = group_name
            fila["modelo"] = model

            for dataset in sorted(df["data_name"].unique(), reverse=True):
                df_query = df.query(
                    f"model == '{model}' & data_name == '{dataset}'"
                )
                values = df_query[group].dropna().values
                data_name = dataset.split("_")[1]

                # Previene errores de índice en caso de que una combinación no arroje valores
                fila[data_name] = values[0] if len(values) > 0 else None

            data.append(fila)

    return pd.DataFrame(data)
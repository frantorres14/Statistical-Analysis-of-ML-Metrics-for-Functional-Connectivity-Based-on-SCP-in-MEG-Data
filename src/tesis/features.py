import os
import numpy as np
import pandas as pd
from typing import Iterator, Tuple
from scipy.signal import butter, filtfilt
from tesis.dataclass import DataHCP 
from typing import List, Optional

def obtener_trials_validos(data_hcp: DataHCP, canales: Optional[List[str]] = None) -> Iterator[Tuple[int, pd.DataFrame]]:
    """
    Evalúa los metadatos de un archivo HCP y extrae secuencialmente los ensayos válidos.

    La función identifica el tipo de tarea ('Wrkmem' o 'Motort') a partir de los 
    metadatos del archivo. Filtra los trial descartando aquellos de son de
    fijación o con respuestas incorrectas, y retorna un generador de DataFrames.

    Args:
        data_hcp: Instancia de DataHCP que contiene los datos y metadatos de un archivo
            .mat de los registros MEG del HCP.
        canales (list, optional): Lista de nombres de canales a incluir. 
                Si es None, se incluyen todos los canales.

    Yields:
        Tuple[int, pd.DataFrame]: Una tupla que contiene:
            - int: El índice o número identificador del ensayo (trial).
            - pd.DataFrame: Los datos correspondientes a ese ensayo.

    Raises:
        ValueError: Si el tipo de tarea detectada en los metadatos no es 
            soportado (diferente de 'Wrkmem' o 'Motort').
    """
    info = data_hcp.get_trialinfo()
    
    if data_hcp.task == "Wrkmem":
        # Máscara: No fijación (columna 3 != 0) y respuestas correctas (columna 13 == 1.0)
        task_type_col= 3
        correcta_col= 13
        task_type_map= {1: "0-back", 2: "2-back"}
        mask = (info[:, task_type_col] != 0) | (info[:, correcta_col] == 1.0)
    elif data_hcp.task == "Motort":
        # Máscara: Tareas de movimiento activo (columna 1 es 1, 2, 4, o 5)
        task_type_col= 1
        task_type_map= {1: "L-hand",2: "L-foot",4: "R-hand", 5: "R-foot" }
        mask = np.isin(info[:, task_type_col], [1, 2, 4, 5])
    else:
        raise ValueError(f"Tarea no soportada: '{data_hcp.task}'. Se esperaba 'Wrkmem' o 'Motort'.")

    trials_validos = np.where(mask)[0]
    
    for trial in trials_validos:
        df_trial = data_hcp.get_df_trial(i_trial=trial, canales= canales)
        task_type = task_type_map[info[trial, task_type_col]]
        yield trial, task_type, df_trial


def guardar_csv(df: pd.DataFrame, nombre_archivo: str, subfijo_proceso : str, trial_id: int, path_save: str) -> None:
    """
    Exporta el DataFrame de un ensayo específico a un archivo CSV.
    Crea el directorio de destino si no existe y guarda los datos del DataFrame.

    Args:
        df (pd.DataFrame): Los datos procesados que se desean guardar.
        nombre_archivo (str): Nombre del archivo.
        subfijo_proceso (str): El subfijo del proceso que se llevó acabo antes de guardar el dataframe. Es parte del nombre del archivo después del nombre base.
        trial_id (int): El número identificador del ensayo.
        path_save (str): Ruta del directorio donde se guardará el archivo.

    Returns:
        None
    """
    os.makedirs(path_save, exist_ok=True)
    
    nombre_base = os.path.splitext(nombre_archivo)[0]
    archivo_name = f"{nombre_base}_{subfijo_proceso}_{trial_id}.csv"
    ruta_guardar = os.path.join(path_save, archivo_name)
    
    df.to_csv(ruta_guardar, index=False)


def aplicar_filtro_broadband(
    df: pd.DataFrame, 
    frecuencias: Tuple[float, float] = (1.0, 40.0), 
    orden: int = 4, 
    fs: float = 508.6275
) -> pd.DataFrame:
    """
    Aplica un filtro pasabanda Butterworth de fase cero a señales fisiológicas.

    Verifica la integridad del DataFrame (ausencia de valores nulos o infinitos),
    calcula los coeficientes del filtro digital basado en las frecuencias de 
    corte y la frecuencia de muestreo, y aplica el filtro a lo largo del 
    eje temporal (filas).

    Args:
        df (pd.DataFrame): Datos crudos a filtrar. Las columnas representan canales y 
            las filas representan el tiempo.
        frecuencias (Tuple[float, float], opcional): Frecuencias de corte inferior y 
            superior en Hz. Por defecto es (1.0, 40.0).
        orden (int, opcional): Orden del filtro Butterworth. Por defecto es 4.
        fs (float, opcional): Frecuencia de muestreo (sample rate) en Hz. 
            Por defecto es 508.6275.

    Returns:
        pd.DataFrame: DataFrame con las señales filtradas, conservando los índices y 
            nombres de columnas originales.

    Raises:
        ValueError: Si el DataFrame contiene valores NaN o Infinitos.
        ValueError: Si las frecuencias de corte están fuera del rango permitido 
            (menores a 0 o mayores a la frecuencia de Nyquist).
        RuntimeError: Si ocurre un error interno en scipy durante el filtrado.
    """
    if df.isnull().values.any():
        cols_con_nan = df.columns[df.isnull().any()].tolist()
        raise ValueError(
            f"Error de integridad: Se detectaron valores NaN en las columnas: {cols_con_nan}. "
            "El preproceso debe asegurar que no existan nulos antes de filtrar."
        )

    if np.isinf(df.values).any():
        raise ValueError("Error de integridad: El DataFrame contiene valores infinitos (inf).")

    lowcut, highcut = frecuencias
    nyquist = 0.5 * fs
    
    if lowcut <= 0 or highcut >= nyquist:
        raise ValueError(
            f"Frecuencias fuera de rango: [{lowcut}, {highcut}] Hz. "
            f"Para una fs de {fs}Hz, el rango permitido es entre 0 y {nyquist}Hz."
        )

    # Diseño del filtro pasabanda
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(orden, [low, high], btype='band')

    try:
        # axis=0 aplica el filtro columna por columna a lo largo del tiempo
        data_filtrada = filtfilt(b, a, df.values, axis=0)
    except Exception as e:
        raise RuntimeError(f"Error crítico durante el filtrado digital: {e}")

    return pd.DataFrame(data_filtrada, index=df.index, columns=df.columns)

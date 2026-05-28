import numpy as np
import pandas as pd
import scipy.io as sio
import matplotlib.pyplot as plt
import re
from typing import List, Optional, Union, Iterator, Tuple
from scipy.signal import butter, sosfiltfilt
from pathlib import Path
import os
from functools import lru_cache
from tesis.config import CANALES_VALIDOS

class DataHCP:
    """
    Clase para el manejo y extracción de datos MEG del Human Connectome Project (HCP).
    
    Esta interfaz facilita la lectura de archivos .mat, permitiendo el acceso 
    estructurado a ensayos (trials), metadatos de la tarea y visualización de señales.

    Attributes:
        archivo (str): Nombre del archivo .mat cargado.
        sujeto (str): Identificador del sujeto extraído del nombre del archivo.
        _raw_data (dict): Contenido completo del archivo .mat cargado.
        task (str): Nombre de la tarea extraído del nombre del archivo.
        fsample (float): Frecuencia de muestreo de la señal.
        _labels (List[str]): Lista de nombres de canales disponibles en el dataset.
    Methods:
        number_trials: Retorna el número total de ensayos disponibles.
        get_trialinfo: Extrae la información de configuración o eventos de los ensayos.
        get_df_trial: Genera un DataFrame de Pandas para un ensayo específico.
        plot_trial: Visualiza las series de tiempo de un ensayo.
    """

    def __init__(self, path: str):
        """
        Inicializa la instancia cargando el archivo .mat y preprocesando etiquetas.

        Args:
            path (str): Ruta completa al archivo .mat del HCP.

        Raises:
            FileNotFoundError: Si el archivo no existe en la ruta especificada.
            AttributeError: Si el formato del archivo .mat no coincide con la estructura esperada.
        """
        self.archivo= re.search(r"([^\\/]+)\.mat$", path).group(1) if re.search(r"([^\\/]+)\.mat$", path) else None
        if not self.archivo:
            raise ValueError(f"Ruta inválida: '{path}' no parece ser un archivo .mat válido.")
        self.sujeto= re.search(r"[\\/](\d{6})[\\/]", path).group(1) if re.search(r"[\\/](\d{6})[\\/]", path) else None
        self._raw_data = sio.loadmat(path)["data"]

        match = re.search(r"-(.*?)_", path)
        self.task = match.group(1) if match else "Unknown"

        self.fsample = float(self._raw_data["fsample"][0,0][0,0])

        raw_labels = self._raw_data[0,0]['label'].squeeze()
        self._labels = [lbl[0] if isinstance(lbl, np.ndarray) else lbl for lbl in raw_labels]

    @property
    def number_trials(self) -> int:
        """
        Retorna el número total de ensayos (trials) disponibles en el dataset.
        Returns:
            int: Cantidad de ensayos.
        """
        return len(self._raw_data[0,0]["trial"][0])

    def get_trialinfo(self) -> np.ndarray:
        """
        Extrae la información de configuración o eventos de los ensayos.
        Returns:
            np.ndarray: Matriz con los metadatos de trialinfo.
        """
        return self._raw_data["trialinfo"][0][0]

    def get_df_trial(self, i_trial: int, canales: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Genera un DataFrame de Pandas para un ensayo específico.
        Args:
            i_trial (int): Índice del ensayo (0 a n-1).
            canales (list, optional): Lista de nombres de canales a incluir. 
                Si es None, se incluyen todos los canales.
        Returns:
            pd.DataFrame: DataFrame con el tiempo como índice (opcional) y canales en columnas.
        """
        trial_data = self._raw_data[0,0]["trial"][0][i_trial]
        # tiempo = np.ravel(self._raw_data[0,0]["time"][0][i_trial]) # Reservado para uso futuro

        if canales:
            # Localizar índices de canales específicos
            indices = [self._labels.index(canal) for canal in canales]
            data_subset = trial_data[indices, :]
            column_names = canales
        else:
            data_subset = trial_data
            column_names = self._labels

        df = pd.DataFrame(data_subset, index=column_names).T
        return df

    def plot_trial(
        self, 
        i_trial: int, 
        canales: Optional[List[str]] = None, 
        n_canales: int = 10, 
        fig_size: tuple = (10, 5)
    ) -> None:
        """
        Visualiza las series de tiempo de un ensayo.
        Args:
            i_trial (int): Índice del ensayo a graficar.
            canales (list, optional): Canales específicos a graficar.
            n_canales (int): Cantidad de canales a mostrar si 'canales' es None. 
                Por defecto 10.
            fig_size (tuple): Dimensiones de la figura (ancho, alto).
        """
        df_trial = self.get_df_trial(i_trial, canales)
        time = np.ravel(self._raw_data[0,0]["time"][0][i_trial])
        
        plt.figure(figsize=fig_size)
        
        # Determinar qué canales iterar
        canales_a_graficar = canales if canales else self._labels[:n_canales]
        
        for canal in canales_a_graficar:
            if canal in df_trial.columns:
                plt.plot(time, df_trial[canal].values, label=canal)
        
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.title(f'Tarea: {self.task} | Series de tiempo MEG - Ensayo {i_trial}')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


def get_common_channels(raw_data_path: Union[str, Path]) -> List[str]:
    """Extrae y encuentra los canales (labels) comunes en todos los archivos .mat.

    Itera sobre las carpetas de sujetos dentro del directorio proporcionado,
    lee los archivos `.mat` (excluyendo los que contienen "trialinfo" en su nombre),
    extrae las etiquetas de los canales MEG y devuelve únicamente aquellos
    canales que están presentes de forma unánime en todos los archivos procesados.

    Args:
        raw_data_path (Union[str, Path]): La ruta absoluta o relativa al 
            directorio principal que contiene las carpetas de los sujetos.

    Returns:
        List[str]: Una lista ordenada alfabéticamente con los nombres de los 
            canales MEG que hacen intersección en todos los archivos. 
            Retorna una lista vacía si no se encontraron datos válidos.

    Raises:
        FileNotFoundError: Si el directorio especificado en `raw_data_path` no existe.
    """
    base_path = Path(raw_data_path)
    all_labels = []

    # Validar que la ruta exista
    if not base_path.exists() or not base_path.is_dir():
        raise FileNotFoundError(f"El directorio '{raw_data_path}' no existe.")

    # Iterar sobre las carpetas de los sujetos
    for subject_dir in base_path.iterdir():
        if not subject_dir.is_dir():
            continue  # Saltar si no es una carpeta

        # Buscar específicamente archivos .mat en la carpeta del sujeto
        for file_path in subject_dir.glob("*.mat"):
            
            # Reemplazamos la búsqueda por índices rígidos (-13:-4) por algo más seguro
            if "trialinfo" in file_path.name:
                continue

            try:
                # Leer el archivo .mat usando la ruta completa
                data = sio.loadmat(file_path)
                
                # Extraer y normalizar los labels
                raw_labels = data["data"][0, 0]['label'].squeeze()
                labels = [
                    lbl[0] if isinstance(lbl, np.ndarray) else lbl 
                    for lbl in raw_labels
                ]
                all_labels.append(labels)
                
            except Exception as e:
                # Capturar errores de lectura sin detener todo el proceso
                print(f"Error procesando el archivo {file_path.name}: {e}")

    # Manejar el caso donde no se encontró ningún archivo válido
    if not all_labels:
        return []

    # Encontrar la intersección de todas las listas
    common_channels = set(all_labels[0]).intersection(*all_labels[1:])

    # Retornar como lista ordenada para garantizar reproducibilidad
    return sorted(list(common_channels))



def obtener_trials_validos(data_hcp: DataHCP, canales: Optional[List[str]] = None) -> Iterator[Tuple[int, pd.DataFrame]]:
    """
    Evalúa los metadatos de un archivo HCP y extrae secuencialmente los ensayos válidos.

    La función identifica el tipo de tarea ('Wrkmem' o 'Motort') a partir de los metadatos del archivo.
    Filtra los trial descartando aquellos que son de fijación, con respuestas incorrectas o 
    con respuestas demasiado cortas menores a 150 milisegundos, y retorna un generador de DataFrames.

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
        # Valores de las columnas a tomar en cuenta para la máscara
        task_type_col= 3
        correcta_col= 13
        resp_time_col = 15
        task_type_map= {1: "0-back", 2: "2-back"}
        # Se aceptan los trials que no sean fijación, la respuesta sea correcta y se conteste después de 150 ms
        mask= (info[:, task_type_col] != 0) & (info[:, correcta_col] == 1.0) & (info[:, resp_time_col] > 0.15)
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


def guardar_parquet(df: pd.DataFrame, nombre_archivo: str, subfijo_proceso: str, trial_id: int, path_save: str) -> None:
    """
    Exporta el DataFrame de un ensayo específico a un archivo Parquet.
    Crea el directorio de destino si no existe y guarda los datos del DataFrame
    de forma comprimida y optimizada.

    Args:
        df (pd.DataFrame): Los datos procesados que se desean guardar.
        nombre_archivo (str): Nombre del archivo base.
        subfijo_proceso (str): El subfijo del proceso que se llevó acabo antes de guardar el dataframe. 
                               Es parte del nombre del archivo después del nombre base.
        trial_id (int): El número identificador del ensayo.
        path_save (str): Ruta del directorio donde se guardará el archivo.

    Returns:
        None
    """
    os.makedirs(path_save, exist_ok=True)
    
    nombre_base = os.path.splitext(nombre_archivo)[0]
    # Cambiamos la extensión a .parquet
    archivo_name = f"{nombre_base}_{subfijo_proceso}_{trial_id}.parquet"
    ruta_guardar = os.path.join(path_save, archivo_name)
    
    # index=False evita guardar la columna del índice si no es necesaria, ahorrando más espacio
    df.to_parquet(ruta_guardar, index=False, engine='pyarrow')

@lru_cache(maxsize=32)
def _crear_filtro_sos(frecuencias: Tuple[float, float], orden: int, fs: float,) -> np.ndarray:
    """
    Genera y cachea los coeficientes SOS de un filtro Butterworth.

    Args:
        frecuencias (Tuple[float, float]): Frecuencias de corte inferior y superior en Hz.
        orden (int): Orden del filtro.
        fs (float): Frecuencia de muestreo en Hz.

    Returns:
        np.ndarray: Coeficientes SOS del filtro Butterworth.
    """

    lowcut, highcut = frecuencias
    nyquist = 0.5 * fs

    if lowcut <= 0 or highcut >= nyquist:
        raise ValueError(f"Frecuencias fuera de rango: [{lowcut}, {highcut}] Hz. Para fs={fs}Hz el rango válido es (0, {nyquist}).")
    return butter(N=orden, Wn=[lowcut, highcut], btype="bandpass", fs=fs, output="sos")



def aplicar_filtro_broadband(
    df: pd.DataFrame,
    frecuencias: Tuple[float, float] = (1.0, 40.0),
    orden: int = 4,
    fs: float = 508.6275,
    dtype: np.dtype = np.float32,
) -> pd.DataFrame:
    """
    Aplica un filtro Butterworth pasabanda de fase cero.
    La operación se vectoriza sobre todos los canales simultáneamente utilizando NumPy y SciPy.

    Args:
        df (pd.DataFrame): Señales crudas. Las filas representan tiempo y las columnas canales.
        frecuencias (Tuple[float, float], opcional):
            Frecuencias de corte inferior y superior en Hz. Por defecto es (1.0, 40.0).
        orden (int, opcional):
            Orden del filtro Butterworth. Por defecto es 4.
        fs (float, opcional):
            Frecuencia de muestreo en Hz. Por defecto es 508.6275.
        dtype (np.dtype, opcional):
            Tipo numérico utilizado durante el filtrado.

    Returns:
        pd.DataFrame:
            Señales filtradas conservando índices y columnas.

    Raises:
        ValueError:
            Si existen NaN, Inf o parámetros inválidos.
        RuntimeError:
            Si scipy falla durante el filtrado.
    """

    # Conversión eficiente
    data = df.to_numpy(dtype=dtype, copy=False)

    # Validaciones vectorizadas rápidas
    if not np.isfinite(data).all():

        if np.isnan(data).any():
            cols_con_nan = df.columns[np.isnan(data).any(axis=0)].tolist()
            raise ValueError(f"Error de integridad: Se detectaron NaN en columnas: {cols_con_nan}")
        raise ValueError(
            "Error de integridad: Se detectaron valores infinitos."
        )

    # Obtención cacheada del filtro
    sos = _crear_filtro_sos(frecuencias=frecuencias, orden=orden, fs=fs)

    try:
        data_filtrada = sosfiltfilt(sos, data, axis=0)
    except Exception as e:
        raise RuntimeError(
            f"Error crítico durante el filtrado digital: {e}") from e

    return pd.DataFrame(data_filtrada, index=df.index, columns=df.columns, copy=False,)


def df_trialinfo_wrkmem(path: str, columns: List[str]) -> pd.DataFrame:
    """Procesa y unifica archivos de información de ensayos (trialinfo) de MEG.

    Lee las carpetas de los sujetos en la ruta proporcionada, carga los archivos
    MATLAB (.mat) que contienen la información de los ensayos de memoria de
    trabajo (Wrkmem) y estructura las matrices de datos de las condiciones
    TIM y TRESP en un único DataFrame de Pandas.

    Args:
        path: Ruta al directorio raíz que contiene las carpetas de los sujetos
          (e.g., 'D:/raw_data/').
        columns: Lista con los nombres cortos de las 40 columnas para etiquetar
          la matriz de datos.

    Returns:
        Un DataFrame de Pandas con todos los ensayos unificados. Contiene las
        columnas adicionales 'sujeto' (índice 0), 'tipo_dato' (índice 1),
        y 'trial' (índice 2, número de ensayo basado en 1 dentro de su bloque),
        seguidas de las columnas especificadas en el argumento `columns`.

    Raises:
        FileNotFoundError: Si la ruta especificada en `path` no existe.
        KeyError: Si el archivo .mat no contiene la estructura esperada
          'trlInfo'.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"La ruta especificada no existe: {path}")

    lista_sujetos = os.listdir(path)
    dataframes_ensayos = []

    for sujeto in lista_sujetos:
        path_sujeto = os.path.join(path, sujeto)

        if not os.path.isdir(path_sujeto):
            continue

        # Se obtienen únicamente los archivos Wrkmem
        for archivo in os.listdir(path_sujeto):
            if "trialinfo" not in archivo or "Wrkmem" not in archivo:
                continue

            ruta_completa = os.path.join(path_sujeto, archivo)
            trlinfo_data = sio.loadmat(ruta_completa)

            # Para cada tipo de dato se extraen las matrices con los datos
            for s in [0, 1]:  # 0: TIM, 1: TRESP
                task = trlinfo_data["trlInfo"]["lockNames"][0][0][0][s][0].upper()
                matriz_trial = trlinfo_data["trlInfo"]["lockTrl"][0][0][0][s]

                df_temporal = pd.DataFrame(matriz_trial, columns=columns)

                # Se genera el número de ensayo por fila (empezando en 1)
                num_trial = np.arange(1, len(df_temporal) + 1)

                # Se agregan las columnas al principio del dataframe
                df_temporal.insert(0, "sujeto", sujeto)
                df_temporal.insert(1, "tipo_dato", task)
                df_temporal.insert(2, "trial", num_trial)

                dataframes_ensayos.append(df_temporal)

    # Se concatenan todos los dataframes
    return pd.concat(dataframes_ensayos, ignore_index=True)


TASK_REGEX = re.compile(r"-(.*?)_")

def procesar_archivo(path_archivo: Path, path_sujeto_guardar: Path) -> None:
    """Procesa un archivo individual de MEG aplicando filtros por ensayo.

    Identifica la tarea del archivo mediante expresiones regulares. Si es una 
    grabación en reposo ('Restin'), extrae y filtra todos sus ensayos. Si es una 
    tarea conductual ('Wrkmem' o 'Motort'), extrae únicamente los ensayos que 
    cumplen con los criterios de validez antes de aplicar el filtro de banda ancha.
    Los resultados se exportan en formato Parquet.

    Args:
        path_archivo: Objeto `Path` con la ruta del archivo raw (.mat) a procesar.
        path_sujeto_guardar: Objeto `Path` con la ruta del directorio donde se 
          almacenarán los archivos Parquet resultantes.

    Returns:
        None
    """
    archivo = path_archivo.name
    if "trialinfo" in archivo:
        return

    match = TASK_REGEX.search(archivo)
    if not match:
        return

    tarea = match.group(1)
    data = DataHCP(str(path_archivo))

    if tarea == "Restin":
        for i_trial in range(data.number_trials):
            df = data.get_df_trial(i_trial, CANALES_VALIDOS)
            df_filtrado = aplicar_filtro_broadband(df)
            guardar_parquet(df=df_filtrado, nombre_archivo=archivo, subfijo_proceso="preproc", trial_id=i_trial, path_save=path_sujeto_guardar)

    elif tarea in {"Wrkmem", "Motort"}:
        for i_trial, type_task, df_valido in obtener_trials_validos(data, canales=CANALES_VALIDOS):
            df_filtrado = aplicar_filtro_broadband(df_valido)
            guardar_parquet(df=df_filtrado, nombre_archivo=archivo, subfijo_proceso=f"{type_task}_preproc", trial_id=i_trial, path_save=path_sujeto_guardar)


def procesar_sujeto(sujeto: str, data_raw_dir: Path, data_intermediate_dir: Path) -> str:
    """Administra y procesa la totalidad de archivos asociados a un sujeto.

    Crea el directorio de salida intermedio para el sujeto especificado, localiza 
    todos los archivos válidos dentro de su carpeta de origen y los envía de manera 
    secuencial a la función de procesamiento de archivos.

    Args:
        sujeto: Identificador numérico o alfanumérico del sujeto (e.g., '105923').
        data_raw_dir: Objeto `Path` que apunta al directorio raíz de los datos raw.
        data_intermediate_dir: Objeto `Path` que apunta al directorio raíz donde 
          se guarda la estructura de datos procesados.

    Returns:
        Un mensaje en cadena de texto (str) indicando el éxito de la operación 
        junto con el ID del sujeto finalizado.
    """
    path_sujeto = data_raw_dir / sujeto
    path_sujeto_guardar = data_intermediate_dir / sujeto
    path_sujeto_guardar.mkdir(parents=True, exist_ok=True)

    archivos = [p for p in path_sujeto.iterdir() if p.is_file()]
    for archivo in archivos:
        procesar_archivo(archivo, path_sujeto_guardar)

    return f"Sujeto {sujeto} finalizado."
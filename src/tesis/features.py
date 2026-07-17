from pathlib import Path
import pandas as pd
from tesis.tools import guardar_procesamiento_parquet, obtener_metadatos_parquet
import numpy as np
from dataclasses import asdict
from typing import Optional, Dict, List, Tuple

def guardar_matriz_correlacion(path_archivo: Path, path_output: Path) -> None:
    """Genera una matriz de correlación y la guarda en formato Parquet.

    Obtiene una ruta a un archivo .parquet el cual lee como Pd.DataFrame, calcula la
    matriz de correlación correspondiente y exporta el resultado en un archivo
    Parquet en el directorio de salida especificado. El archivo generado mantendrá
    el nombre original pero incluirá el sufijo '_corr'.

    Args:
        path_archivo: Objeto `Path` que apunta al archivo de datos .parquet
        path_output: Objeto `Path` que representa el directorio donde se
          guardará el archivo Parquet resultante.

    Returns:
        None.

    Raises:
        FileNotFoundError: Si el archivo en `path_archivo` no existe.
        ValueError: Si los datos del archivo no son aptos para calcular
          correlaciones.
        IOError: Si ocurre un error al intentar escribir en `path_output`.
    """
    df = pd.read_parquet(path=path_archivo)
    corr_matrix= df.corr(method="pearson")
    metadata = obtener_metadatos_parquet(path_archivo)

    
    guardar_procesamiento_parquet(
        df= corr_matrix,
        path_archivo= path_archivo,
        subfijo_proceso= "corr",
        metadata= metadata,
        path_save= path_output,
    )


def corr_matrices_sujeto_pipeline(sujeto: str, input_data_dir: Path, output_data_dir: Path) -> str:
    """Genera matrices de correlación para todos los archivos de un sujeto.

    Crea el directorio de salida correspondiente al sujeto, localiza todos
    los archivos en formato Parquet dentro de su carpeta de origen y calcula
    la matriz de correlación de cada uno de ellos. Los resultados se guardan
    en el directorio de salida manteniendo la organización por sujeto.

    Args:
        sujeto: Identificador único del sujeto cuyos archivos serán
            procesados.
        input_data_dir: Directorio raíz que contiene las carpetas de entrada
            organizadas por sujeto.
        output_data_dir: Directorio raíz donde se almacenarán las matrices
            de correlación generadas.

    Returns:
        Mensaje indicando que el procesamiento del sujeto ha finalizado
        correctamente.
    """
    path_sujeto = input_data_dir / sujeto
    path_sujeto_guardar = output_data_dir / sujeto
    path_sujeto_guardar.mkdir(parents=True, exist_ok=True)

    archivos = path_sujeto.glob("*.parquet")

    for archivo in archivos:
        guardar_matriz_correlacion(path_archivo= archivo, path_output= path_sujeto_guardar)

    return f"Sujeto {sujeto} finalizado."


def corr_matrix_to_vector(corr_matrix: pd.DataFrame) -> pd.Series:
    """Convierte una matriz de correlación cuadrada en un vector plano.
    
    Extrae los elementos del triángulo superior de la matriz de correlación,
    excluyendo la diagonal principal, y los aplana en un vector unidimensional.
    Los nombres de las nuevas columnas se construyen combinando los nombres
    originales con un guión (ejemplo: 'A-B', 'A-C', 'B-C').
    
    Args:
        corr_matrix: DataFrame cuadrado que representa una matriz de correlación.
            Debe tener los mismos índices en filas y columnas.
    
    Returns:
        pd.Series con los valores del triángulo superior aplanados, donde:
        - El índice contiene los nombres combinados (ej: 'A-B', 'A-C')
        - Los valores son las correlaciones correspondientes
        - El nombre de la serie es 'correlation'
    """

    # Se obtienen los índices del triángulo superior (k=1 excluye la diagonal)
    row_indices, col_indices = np.triu_indices_from(corr_matrix, k=1)
    
    # Se contruyen nombres combinados manteniendo el orden de los índices
    columnas = corr_matrix.columns
    pair_names = [f"{columnas[i]}-{columnas[j]}" for i, j in zip(row_indices, col_indices)]
    
    # Extraer valores usando los mismos índices y se guarda como pd.Series
    valores = corr_matrix.values[row_indices, col_indices]
    serie = pd.Series(data=valores, index=pair_names, name='valores', dtype=float)
    
    return serie


def vectores_corr_pipeline(sujeto: str, input_data_dir: Path, output_data_dir: Path) -> str:
    """Genera un conjunto de vectores de correlación para un sujeto.

    Lee todas las matrices de correlación almacenadas en formato Parquet para
    un sujeto determinado, transforma cada matriz en su representación
    vectorizada, incorpora los metadatos asociados al archivo original y
    consolida toda la información en un único DataFrame. El resultado se
    almacena como un archivo Parquet en el directorio de salida del sujeto.

    Args:
        sujeto: Identificador único del sujeto cuyos datos serán procesados.
        input_data_dir: Directorio raíz que contiene las carpetas de entrada
            organizadas por sujeto.
        output_data_dir: Directorio raíz donde se almacenarán los resultados
            generados.

    Returns:
        Mensaje indicando que el procesamiento del sujeto ha finalizado
        correctamente.
    """
    # Se crean los paths para leer por sujeto y guardar
    path_sujeto= input_data_dir / sujeto 
    path_sujeto_guardar = output_data_dir / sujeto
    path_sujeto_guardar.mkdir(parents= True, exist_ok= True)

    # Se obtienen todos los archivos en esa carpeta
    archivos = path_sujeto.glob("*.parquet")

    lista_dict= []

    for archivo in archivos:
        # Se leen las matrices de correlación y se convierten en vectores
        df_matrix= pd.read_parquet(archivo)
        vector = corr_matrix_to_vector(df_matrix)
        # Se obtienen los metadatos de ese archivo y se pasan a un diccionario
        metadata_obj = obtener_metadatos_parquet(archivo)
        metadata_dict = asdict(metadata_obj)
        # El vector pasa de formato pd.Serie a diccionario
        vector_dict = vector.to_dict()
        # Se crea un solo vector con los metadatos y los valores del vector de correlación
        fila_completa = metadata_dict | vector_dict
        # Se agrega ese vector a una lista
        lista_dict.append(fila_completa)
    
    # Se convierte en un solo pd.DataFrame todos los vectores de la lista
    df = pd.DataFrame(lista_dict)

    path_guardar = path_sujeto_guardar / f"{sujeto}_vector_corr_dataset.parquet"
    df.to_parquet(path_guardar, index=False)

    return f"Sujeto {sujeto} finalizado."


def matriz_promediada(lista_paths: list[Path]) -> pd.DataFrame:
    """Promedia matrices de correlación cargando todas en memoria simultáneamente.

    Lee una lista de archivos Parquet que contienen matrices de correlación,
    los apila y calcula el promedio para cada celda (i, j). Maneja automáticamente 
    los valores nulos (NaN) ignorándolos en el cálculo del promedio.
    Preserva el orden original del índice sin reordenar alfabéticamente.

    Args:
        paths_matrices (list[Path]): Lista de objetos Path que apuntan a los 
            archivos Parquet a promediar.

    Returns:
        pd.DataFrame: Un DataFrame que contiene la matriz de correlación promediada
            con el mismo índice y columnas que las matrices originales.

    Raises:
        ValueError: Si la lista `paths_matrices` está vacía o si las matrices 
            tienen índices/columnas inconsistentes.
    """
    if not lista_paths:
        raise ValueError("La lista de rutas de archivos está vacía.")
        
    # Cargamos todos los DataFrames en una lista
    lista_dfs = [pd.read_parquet(p) for p in lista_paths]
    
    # Validar que todas las matrices tienen el mismo índice y columnas
    primer_indice = lista_dfs[0].index
    primera_columna = lista_dfs[0].columns
    
    for i, df in enumerate(lista_dfs[1:], 1):
        if not df.index.equals(primer_indice):
            raise ValueError(f"La matriz {i} tiene índices diferentes")
        if not df.columns.equals(primera_columna):
            raise ValueError(f"La matriz {i} tiene columnas diferentes")
    
    # Apilamos verticalmente los DataFrames y promediamos basándonos en el índice
    # Usamos sort=False para preservar el orden original del índice
    matriz_promedio = pd.concat(lista_dfs).groupby(level=0, sort=False).mean()
    
    # Reordenar explícitamente al orden original para asegurar que coincida
    matriz_promedio = matriz_promedio.reindex(primer_indice)[primera_columna]
    
    return matriz_promedio


def scp_pipeline(sujeto: str, input_data_dir: Path, output_data_dir: Path) -> str:
    """Genera matrices SCP promedio para un sujeto agrupadas por referencia.

    Recorre todos los archivos Parquet asociados a un sujeto y los clasifica
    en dos grupos según el valor de `type_ref` presente en sus metadatos:
    TRESP/TEMG y TIM/TFLA. Los registros de la tarea "Restin" se incluyen en
    ambos grupos. Posteriormente calcula la matriz promedio de cada conjunto
    y almacena los resultados en archivos Parquet independientes.

    Args:
        sujeto: Identificador único del sujeto cuyos datos serán procesados.
        input_data_dir: Directorio raíz que contiene las carpetas de entrada
            organizadas por sujeto.
        output_data_dir: Directorio raíz donde se almacenarán las matrices
            SCP promedio generadas.

    Returns:
        Mensaje indicando que el procesamiento del sujeto ha finalizado
        correctamente.
    """
    # Se crean los paths para leer los archivos por sujeto y para guardar los scp
    path_sujeto = input_data_dir / sujeto

    path_sujeto_guardar= output_data_dir / sujeto
    path_sujeto_guardar.mkdir(parents=True, exist_ok=True)
    scp_tresp_temg_guardar= path_sujeto_guardar / f"{sujeto}_scp_tresp_temg.parquet"
    scp_tim_tfla_guardar= path_sujeto_guardar / f"{sujeto}_scp_tim_tfla.parquet"

    lista_tresp_temg= []
    lista_tim_tfla= []


    archivos=  path_sujeto.glob("*.parquet")
    for archivo in archivos:
        metadata = obtener_metadatos_parquet(archivo)
        # Las tareas Restin van en ambos scp
        if metadata.task== "Restin":
            lista_tresp_temg.append(archivo)
            lista_tim_tfla.append(archivo)
        # Dependiendo de type_ref se guardan en una lista u otra
        elif metadata.type_ref in {"TRESP", "TEMG"}:
            lista_tresp_temg.append(archivo)
        elif metadata.type_ref in {"TIM", "TFLA"}:
            lista_tim_tfla.append(archivo)
    
    # Se crean ambos SCP dependiento de las combinaciones de type_ref
    scp_tresp_temg= matriz_promediada(lista_paths= lista_tresp_temg)
    scp_tim_tfla= matriz_promediada(lista_paths= lista_tim_tfla)

    scp_tresp_temg.to_parquet(scp_tresp_temg_guardar, index= True)
    scp_tim_tfla.to_parquet(scp_tim_tfla_guardar, index= True)

    return f"Sujeto {sujeto} finalizado."


def matriz_diferencia(corr_matrix: pd.DataFrame, scp: pd.DataFrame):
    """Calcula la diferencia elemento a elemento entre dos matrices.

    Verifica que ambas matrices tengan los mismos índices y columnas antes
    de realizar la resta. El resultado conserva la misma estructura que las
    matrices de entrada.

    Args:
        corr_matrix: Matriz de correlación de referencia.
        scp: Matriz SCP que será sustraída de `corr_matrix`.

    Returns:
        DataFrame que contiene la diferencia elemento a elemento entre
        `corr_matrix` y `scp`.

    Raises:
        ValueError: Si los índices o las columnas de ambas matrices no coinciden.
    """

    if not corr_matrix.index.equals(scp.index):
        raise ValueError("Los índices de las matrices no coinciden.")

    if not corr_matrix.columns.equals(scp.columns):
        raise ValueError("Las columnas de las matrices no coinciden.")


    return corr_matrix - scp


def diff_matrices_pipeline(sujeto: str, corr_matrices_dir: Path, scp_dir: Path, output_data_dir: Path) -> str:
    """Genera matrices diferencia respecto a los SCP de referencia.

    Lee las matrices de correlación de un sujeto y calcula su diferencia
    respecto a la matriz SCP correspondiente según el tipo de referencia
    (`type_ref`). Las tareas "Restin" se comparan contra ambos SCP
    disponibles. Cada matriz diferencia generada se almacena en formato
    Parquet dentro del directorio de salida del sujeto.

    Args:
        sujeto: Identificador único del sujeto cuyos datos serán procesados.
        corr_matrices_dir: Directorio raíz que contiene las matrices de
            correlación organizadas por sujeto.
        scp_dir: Directorio raíz que contiene las matrices SCP previamente
            calculadas.
        output_data_dir: Directorio raíz donde se almacenarán las matrices
            diferencia generadas.

    Returns:
        Mensaje indicando que el procesamiento del sujeto ha finalizado
        correctamente.

    Raises:
        FileNotFoundError: Si alguna matriz SCP requerida no existe.
        ValueError: Si las dimensiones, índices o columnas de una matriz de
            correlación y su SCP asociado no coinciden.
    """
    # Se crean los paths para leer las matrices de correlación y los scp
    path_sujeto_corr = corr_matrices_dir / sujeto
    path_sujeto_scp = scp_dir / sujeto
    # Se crea el path donde guardar los datos
    path_sujeto_guardar = output_data_dir / sujeto
    path_sujeto_guardar.mkdir(parents=True, exist_ok=True)

    scp_tresp_temg= pd.read_parquet(path_sujeto_scp / f"{sujeto}_scp_tresp_temg.parquet")
    scp_tim_tfla= pd.read_parquet(path_sujeto_scp / f"{sujeto}_scp_tim_tfla.parquet")

    archivos = path_sujeto_corr.glob("*.parquet")

    for archivo in archivos:
        # Se carga la matriz de correlación y su metadata
        metadata = obtener_metadatos_parquet(archivo)
        corr_matrix = pd.read_parquet(archivo)

        scps = []

        # Dependiendo del tipo de archivo se carga un scp o el otro, o ambos
        if metadata.task == "Restin":
            scps = [("tresp-temg", scp_tresp_temg), ("tim-tfla", scp_tim_tfla)]
        elif metadata.type_ref in {"TRESP", "TEMG"}:
            scps = [("tresp-temg", scp_tresp_temg)]
        elif metadata.type_ref in {"TIM", "TFLA"}:
            scps = [("tim-tfla", scp_tim_tfla)]

        # Se crean las matrices de diferencia dependiendo del tipo de tarea y referencia
        # obtenida de los metadatos y se guarda como un archivo parquet
        for nombre_scp, scp in scps:
            diff = matriz_diferencia(corr_matrix=corr_matrix,scp=scp)
            path_diff_guardar= path_sujeto_guardar / nombre_scp
            path_diff_guardar.mkdir(parents= True, exist_ok= True)

            guardar_procesamiento_parquet(
                df=diff,
                path_archivo=archivo,
                subfijo_proceso=f"{nombre_scp}_diff",
                metadata=metadata,
                path_save=path_diff_guardar,
            )
            
    return f"Sujeto {sujeto} finalizado."


def vectores_diff_pipeline(sujeto: str, input_data_dir: Path, output_data_dir: Path) -> str:
    """Genera un conjunto de vectores de diferencia para un sujeto.

    Lee todas las matrices de diferencia almacenadas en formato Parquet para
    un sujeto determinado, transforma cada matriz en su representación
    vectorizada, incorpora los metadatos asociados al archivo original y
    consolida toda la información en un único DataFrame. El resultado se
    almacena como un archivo Parquet en el directorio de salida del sujeto.

    Args:
        sujeto: Identificador único del sujeto cuyos datos serán procesados.
        input_data_dir: Directorio raíz que contiene las carpetas de entrada
            organizadas por sujeto.
        output_data_dir: Directorio raíz donde se almacenarán los resultados
            generados.

    Returns:
        Mensaje indicando que el procesamiento del sujeto ha finalizado
        correctamente.
    """
    # Se crean los paths para leer por sujeto y guardar
    path_sujeto= input_data_dir / sujeto 
    path_sujeto_guardar = output_data_dir / sujeto
    path_sujeto_guardar.mkdir(parents= True, exist_ok= True)

    for type_ref in ["tim-tfla", "tresp-temg"]:
        # Se obtienen todos los archivos en esa carpeta
        path_matrices= path_sujeto / type_ref
        archivos = path_matrices.glob("*.parquet")

        lista_dict= []

        for archivo in archivos:
            # Se leen las matrices de correlación y se convierten en vectores
            df_matrix= pd.read_parquet(archivo)
            vector = corr_matrix_to_vector(df_matrix)
            # Se obtienen los metadatos de ese archivo y se pasan a un diccionario
            metadata_obj = obtener_metadatos_parquet(archivo)
            metadata_dict = asdict(metadata_obj)
            # El vector pasa de formato pd.Serie a diccionario
            vector_dict = vector.to_dict()
            # Se crea un solo vector con los metadatos y los valores del vector de correlación
            fila_completa = metadata_dict | vector_dict
            # Se agrega ese vector a una lista
            lista_dict.append(fila_completa)
        
        # Se convierte en un solo pd.DataFrame todos los vectores de la lista
        df = pd.DataFrame(lista_dict)
        path_guardar = path_sujeto_guardar / f"{sujeto}_vector_diff_{type_ref}_dataset.parquet"
        df.to_parquet(path_guardar, index=False)
    return f"Sujeto {sujeto} finalizado."


def correlation_vector_type_ref(df: pd.DataFrame, type_ref: str) -> np.ndarray:
    """Extrae y aplana los valores de correlación para una referencia específica.

    Filtra el DataFrame dado buscando una referencia en particular dentro de 
    la columna 'type_ref'. Luego, selecciona únicamente las columnas de tipo 
    numérico (float64) y devuelve todos sus valores como un único vector 
    unidimensional (aplanado).

    Args:
        df (pd.DataFrame): El DataFrame principal que contiene los datos. 
            Debe incluir una columna llamada 'type_ref' y columnas de 
            tipo float64.
        type_ref (str): El nombre exacto de la referencia que se desea 
            filtrar (por ejemplo, "TIM", "TRESP", "TFLA").

    Returns:
        np.ndarray: Un vector (array de numpy 1D) con todos los valores de 
        las columnas float64 correspondientes a la referencia indicada. Si la 
        referencia no se encuentra en el DataFrame, devolverá un array vacío.

    Raises:
        KeyError: Si la columna 'type_ref' no existe en el DataFrame original.
    """
    if "type_ref" not in df.columns:
        raise KeyError("El DataFrame debe contener una columna llamada 'type_ref'.")

    # Se filtran los datos para la referencia específica
    df_filtered = df[df["type_ref"] == type_ref]

    # Se seleccionan sólo los valores de correlación (columnas float64)
    df_floats = df_filtered.select_dtypes(include=["float64"])

    return df_floats.values.flatten()


def matrices_promediadas_por_tarea(sujeto: str, input_data_dir: Path, output_data_dir: Path) -> str:
    """
    
    """
    path_sujeto = input_data_dir / sujeto
    path_sujeto_guardar = output_data_dir / sujeto
    path_sujeto_guardar.mkdir(parents=True, exist_ok=True)


def dataset_corr_pipeline(
    ruta_archivos: str,
    mapeo_clases: Optional[Dict[str, int]] = None,
    columnas_eliminar: Optional[List[str]] = None,
    type_ref_elegidos: Optional[List[str]] = None,
    ) -> pd.DataFrame:
    """Carga y procesa múltiples archivos Parquet aplicando transformaciones y limpieza para crear el
    dataset para el entrenamiento de los modelos.

    Busca todos los archivos Parquet en la ruta especificada (incluyendo subcarpetas), los concatena
    en un único DataFrame de Pandas, crea una columna objetivo ('target') basada en un diccionario de mapeo,
    reduce la precisión de las columnas flotantes a float32 para optimizar el uso de memoria y 
    elimina las columnas innecesarias.

    Args:
        ruta_archivos (str): Patrón de ruta con comodines (ej. '**/*.parquet')
            para localizar los archivos de forma recursiva.
        dict_classes (dict): Diccionario de mapeo para transformar los valores
            de 'type_task' en identificadores numéricos.
        columnas_a_borrar (list): Lista con los nombres de las columnas que
            se van a eliminar del DataFrame final.
        type_ref_elegido (list): Tipo de referencias elegidas de la columna
            "type_ref". Para la tarea "Restin" se elige la palabra "Restin"

    Returns:
        pd.DataFrame: El DataFrame de Pandas completamente procesado y optimizado.

    Raises:
        ValueError: Si no se encuentra ningún archivo Parquet en la ruta provista.
    """
    # Asignar valores por defecto si no se pasaron argumentos personalizados
    if mapeo_clases is None:
        mapeo_clases = {"0-back": 0, "R-hand": 1, "R-foot": 2, "Restin": 3, "L-hand": 4, "L-foot": 5, "2-back": 6}

    if columnas_eliminar is None:
        columnas_eliminar = ["run", "task", "trial_id", "type_task", "type_ref", "process", "instrumento", "preproc_base"]

    if type_ref_elegidos is None:
        type_ref_elegidos = ["Restin", "TIM", "TFLA"]
    
    # Encontrar todos los archivos Parquet en las subcarpetas
    ruta_archivos = Path(ruta_archivos)
    archivos = list(ruta_archivos.rglob("*.parquet"))

    if not archivos:
        raise ValueError(f"No se encontraron archivos Parquet en la ruta: {ruta_archivos}")

    # Leer y concatenar todos los archivos en un solo DataFrame
    df = pd.concat((pd.read_parquet(archivo) for archivo in archivos), ignore_index=True)

    # Identificar las columnas de tipo float64 para reducir su precisión
    float_cols = df.select_dtypes(include=["float64"]).columns

    # Se rellenan los valores vacíos para poder hacer la selección del tipo de referencia
    df = df[df["type_ref"].fillna("Restin").isin(type_ref_elegidos)]

    # Aplicar el pipeline de transformación y limpieza de datos
    df = (df.assign(target=lambda x: x["type_task"].fillna("Restin").map(mapeo_clases).astype("Int64"))
        .astype({col: "float32" for col in float_cols}).drop(columns=columnas_eliminar))
    
    return df


def dataset_diff_pipeline(
    ruta_archivos: str,
    mapeo_clases: Optional[Dict[str, int]] = None,
    columnas_eliminar: Optional[List[str]] = None,
    type_ref_elegidos: str = None,
    ) -> pd.DataFrame:
    """Carga y procesa múltiples archivos Parquet aplicando transformaciones y limpieza para crear el
    dataset para el entrenamiento de los modelos.

    Busca todos los archivos Parquet en la ruta especificada (incluyendo subcarpetas), los concatena
    en un único DataFrame de Pandas, crea una columna objetivo ('target') basada en un diccionario de mapeo,
    reduce la precisión de las columnas flotantes a float32 para optimizar el uso de memoria y 
    elimina las columnas innecesarias.

    Args:
        ruta_archivos (str): Patrón de ruta con comodines (ej. '**/*.parquet')
            para localizar los archivos de forma recursiva.
        dict_classes (dict): Diccionario de mapeo para transformar los valores
            de 'type_task' en identificadores numéricos.
        columnas_a_borrar (list): Lista con los nombres de las columnas que
            se van a eliminar del DataFrame final.
        type_ref_elegido (str): Tipo de referencias elegidas 

    Returns:
        pd.DataFrame: El DataFrame de Pandas completamente procesado y optimizado.

    Raises:
        ValueError: Si no se encuentra ningún archivo Parquet en la ruta provista.
    """
    # Asignar valores por defecto si no se pasaron argumentos personalizados
    if mapeo_clases is None:
        mapeo_clases = {"0-back": 0, "R-hand": 1, "R-foot": 2, "Restin": 3, "L-hand": 4, "L-foot": 5, "2-back": 6}

    if columnas_eliminar is None:
        columnas_eliminar = ["run", "task", "trial_id", "type_task", "type_ref", "process", "instrumento", "preproc_base"]

    if type_ref_elegidos is None:
        type_ref_elegidos = "tim-tfla"
    
    # Encontrar todos los archivos Parquet en las subcarpetas
    ruta_archivos = Path(ruta_archivos)
    archivos = list(ruta_archivos.rglob("*.parquet"))
    
    if not archivos:
        raise ValueError(f"No se encontraron archivos Parquet en la ruta: {ruta_archivos}")

    # Leer y concatenar todos los archivos en un solo DataFrame
    df = pd.concat((pd.read_parquet(archivo) for archivo in archivos if type_ref_elegidos in str(archivo)), ignore_index=True)

    # Identificar las columnas de tipo float64 para reducir su precisión
    float_cols = df.select_dtypes(include=["float64"]).columns

    # Aplicar el pipeline de transformación y limpieza de datos
    df = (df.assign(target=lambda x: x["type_task"].fillna("Restin").map(mapeo_clases).astype("Int64"))
        .astype({col: "float32" for col in float_cols}).drop(columns=columnas_eliminar))
    
    return df

class EsquemasMEGToEEG:
    """Convierte datos MEG a matrices de correlación en formato EEG.

    Esta clase maneja los mapeos de canales y provee distintos métodos 
    para calcular la correlación entre señales transformadas.

    Attributes:
        MAPEO_C1 (Dict[str, str]): Mapeo directo uno a uno de canales EEG a MEG.
        MAPEO_C2_C3 (Dict[str, List[str]]): Mapeo de un canal EEG a múltiples canales MEG.
        meg_data (pd.DataFrame): DataFrame con los datos crudos de MEG.
    """

    MAPEO_C1 = {
        'Fp1': 'A91', 'F3': 'A40', 'C3': 'A44', 'P3': 'A72',
        'F7': 'A95', 'T3': 'A130', 'T5': 'A160', 'O1': 'A184',
        'Fz': 'A4', 'Cz': 'A10', 'Pz': 'A49', 'Fp2': 'A151',
        'F4': 'A58', 'C4': 'A54', 'P4': 'A78', 'F8': 'A115',
        'T4': 'A144', 'T6': 'A169', 'O2': 'A167'
    }

    MAPEO_C2_C3 = {
        'Fp1': ['A92', 'A91'],
        'F3': ['A64', 'A39', 'A21', 'A22', 'A40', 'A65', 'A66'],
        'C3': ['A23', 'A24', 'A25', 'A26', 'A42', 'A43', 'A44', 'A67', 'A69'],
        'P3': ['A46', 'A47', 'A71', 'A72', 'A100', 'A101', 'A103'],
        'F7': ['A95', 'A127', 'A93', 'A125', 'A154'],
        'T3': ['A97', 'A98', 'A99', 'A130', 'A131', 'A158', 'A96', 'A156'],
        'T5': ['A132', 'A133', 'A134', 'A181', 'A160', 'A161'],
        'O1': ['A135', 'A163', 'A184'],
        'Fz': ['A7', 'A4'],
        'Cz': ['A3', 'A9', 'A10', 'A14', 'A16'],
        'Pz': ['A28', 'A29', 'A48', 'A49', 'A50', 'A74', 'A75', 'A76'],
        'Fp2': ['A151'],
        'F4': ['A86', 'A35', 'A58', 'A85', 'A34', 'A57', 'A84'],
        'C4': ['A30', 'A31', 'A32', 'A33', 'A53', 'A54', 'A55', 'A56', 'A80', 'A82', 'A83'],
        'P4': ['A51', 'A77', 'A78', 'A79', 'A107', 'A108', 'A109', 'A110'],
        'F8': ['A117', 'A115'],
        'T4': ['A113', 'A114', 'A144', 'A143', 'A171'],
        'T6': ['A140', 'A141', 'A142', 'A170', 'A168', 'A169', 'A191'],
        'O2': ['A139', 'A166', 'A167', 'A168']
    }

    def __init__(self, meg_data: pd.DataFrame):
        """Inicializa el convertidor almacenando los datos MEG a procesar.

        Args:
            meg_data (pd.DataFrame): Matriz de datos MEG donde las columnas representan
                los canales y las filas las muestras temporales.
        """
        self.meg_data = meg_data

    def convert(self, method: str = 'c1') -> Tuple[Optional[pd.DataFrame], pd.DataFrame]:
        """Ejecuta la conversión de canales aplicando el método especificado.

        Args:
            method (str, optional): Método de conversión a utilizar ('c1', 'c2' o 'c3').
                Por defecto es 'c1'.

        Returns:
            Tuple[Optional[pd.DataFrame], pd.DataFrame]: Una tupla que contiene:
                - DataFrame con las señales EEG mapeadas (None si el método es 'c3').
                - DataFrame con la matriz de correlación de Pearson.

        Raises:
            ValueError: Si el método de conversión asignado no está soportado.
        """
        if method == 'c1':
            return self._process_c1()
        elif method == 'c2':
            return self._process_c2()
        elif method == 'c3':
            return self._process_c3()
        else:
            raise ValueError(f"El método '{method}' no está soportado. Use 'c1', 'c2' o 'c3'.")

    def _process_c1(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Procesa los datos mediante mapeo directo de un canal MEG por canal EEG.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Señales EEG extraídas y su matriz de correlación.
        """
        eeg_data = {}
        for eeg_channel, meg_channel in self.MAPEO_C1.items():
            if meg_channel in self.meg_data.columns:
                eeg_data[eeg_channel] = self.meg_data[meg_channel]
                
        df_eeg = pd.DataFrame(eeg_data)
        df_corr = df_eeg.corr(method='pearson')
        
        return df_eeg, df_corr

    def _process_c2(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Procesa los datos promediando múltiples canales MEG para formar un canal EEG.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Señales EEG promediadas y su matriz de correlación.
        """
        eeg_data = {}
        for eeg_channel, meg_channels in self.MAPEO_C2_C3.items():
            valid_meg_channels = [chan for chan in meg_channels if chan in self.meg_data.columns]
            if valid_meg_channels:
                eeg_data[eeg_channel] = np.mean(self.meg_data[valid_meg_channels], axis=1)
                
        df_eeg = pd.DataFrame(eeg_data)
        df_corr = df_eeg.corr(method='pearson')
        
        return df_eeg, df_corr

    def _process_c3(self) -> Tuple[None, pd.DataFrame]:
        """Procesa los datos promediando las correlaciones individuales de pares de canales MEG.

        A diferencia de c1 y c2, este método no genera una señal temporal EEG consolidada,
        sino que calcula directamente la matriz de conectividad (correlación).

        Returns:
            Tuple[None, pd.DataFrame]: Tupla con None en el espacio de señales temporales 
            y el DataFrame correspondiente a la matriz de correlación final.
        """
        eeg_channels = list(self.MAPEO_C2_C3.keys())
        n_channels = len(eeg_channels)
        corr_matrix = np.zeros((n_channels, n_channels))
        
        for i, eeg_ch1 in enumerate(eeg_channels):
            for j, eeg_ch2 in enumerate(eeg_channels):
                meg_ch1 = [ch for ch in self.MAPEO_C2_C3[eeg_ch1] if ch in self.meg_data.columns]
                meg_ch2 = [ch for ch in self.MAPEO_C2_C3[eeg_ch2] if ch in self.meg_data.columns]
                
                if meg_ch1 and meg_ch2:
                    correlations = []
                    for m1 in meg_ch1:
                        for m2 in meg_ch2:
                            corr = self.meg_data[m1].corr(self.meg_data[m2])
                            correlations.append(corr)
                            
                    corr_matrix[i, j] = np.mean(correlations)
                else:
                    corr_matrix[i, j] = np.nan
                    
        df_corr = pd.DataFrame(corr_matrix, index=eeg_channels, columns=eeg_channels)
        
        return None, df_corr
    
def guardar_matriz_esquema(path_archivo: Path, path_output: Path) -> None:
    """Calcula y guarda la matriz de correlación según el esquema especificado.

    Args:
        path_archivo (Path): Ruta al archivo Parquet que contiene los datos MEG.
        path_output (Path): Directorio donde se guardará la matriz de correlación resultante.
        esquema (str): Esquema de correlación a utilizar ('C1', 'C2' o 'C3').

    Raises:
        ValueError: Si el esquema proporcionado no es válido.
    """
    meg_data = pd.read_parquet(path_archivo)
    convertidor = EsquemasMEGToEEG(meg_data)

    # Se determina el esquema a utilizar a partir del nombre del archivo
    esquema = path_archivo.stem.split('_')[-1].upper()

    _, corr_matrix = convertidor.convert(method=esquema.lower())
    
    metadata = obtener_metadatos_parquet(path_archivo)
    
    guardar_procesamiento_parquet(
        df= corr_matrix,
        path_archivo= path_archivo,
        subfijo_proceso= "corr",
        metadata= metadata,
        path_save= path_output,
    )

def esquemas_sujeto_pipeline(sujeto: str, input_data_dir: Path, output_data_dir: Path, esquema: str) -> str:
    """Genera matrices de correlación para todos los archivos de un sujeto.

    Crea el directorio de salida correspondiente al sujeto, localiza todos
    los archivos en formato Parquet dentro de su carpeta de origen y calcula
    la matriz de correlación de cada uno de ellos. Los resultados se guardan
    en el directorio de salida manteniendo la organización por sujeto.

    Args:
        sujeto: Identificador único del sujeto cuyos archivos serán
            procesados.
        input_data_dir: Directorio raíz que contiene las carpetas de entrada
            organizadas por sujeto.
        output_data_dir: Directorio raíz donde se almacenarán las matrices
            de correlación generadas.
        esquema: Esquema de correlación a utilizar (C1, C2 o C3).

    Returns:
        Mensaje indicando que el procesamiento del sujeto ha finalizado
        correctamente.
    """
    path_sujeto = input_data_dir / sujeto
    path_sujeto_guardar = output_data_dir / sujeto
    path_sujeto_guardar.mkdir(parents=True, exist_ok=True)

    archivos = path_sujeto.glob("*.parquet")

    for archivo in archivos:
        guardar_matriz_esquema(path_archivo= archivo, path_output= path_sujeto_guardar)

    return f"Sujeto {sujeto} finalizado."
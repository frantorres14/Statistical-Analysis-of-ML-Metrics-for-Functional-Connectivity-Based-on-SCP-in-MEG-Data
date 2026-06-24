from pathlib import Path
import pandas as pd
from tesis.tools import guardar_procesamiento_parquet, obtener_metadatos_parquet
import numpy as np
from dataclasses import asdict


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
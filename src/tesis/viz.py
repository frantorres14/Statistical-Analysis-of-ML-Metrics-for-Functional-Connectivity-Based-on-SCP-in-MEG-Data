import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Union

from tesis.features import corr_matrix_to_vector


def load_subject_vectors(base_path: Union[str, Path], feature_type: str) -> pd.DataFrame:
    """Lee y extrae los vectores SCP para todos los sujetos en un directorio.

    Itera sobre los directorios de los sujetos, lee los archivos parquet
    correspondientes y convierte las matrices de correlación en vectores.

    Args:
        base_path (Union[str, Path]): Ruta del directorio principal que 
            contiene las carpetas de los sujetos.
        feature_type (str): Tipo de característica a extraer.

    Returns:
        pd.DataFrame: DataFrame consolidado donde cada columna representa a 
        un sujeto y contiene su vector SCP extraído.
    """
    base_path = Path(base_path)
    datos_sujetos = {}

    for path_sujeto in base_path.iterdir():
        if path_sujeto.is_dir():
            sujeto = path_sujeto.name
            archivo = path_sujeto / f"{sujeto}_scp_{feature_type}.parquet"
            
            if archivo.exists():
                df_scp = pd.read_parquet(archivo)
                datos_sujetos[sujeto] = corr_matrix_to_vector(df_scp)
                
    return pd.DataFrame(datos_sujetos)


def plot_scp_correlation(
    correlation_matrix: pd.DataFrame, 
    feature_type: str, 
    vmin: float = 0.86,
    save: str = None
) -> None:
    """Genera y muestra las gráficas de la matriz de correlación.

    Crea una figura con dos subgráficas: un mapa de calor (heatmap) para 
    visualizar la correlación entre sujetos y un diagrama de caja (boxplot) 
    para ver la distribución de dichas correlaciones.

    Args:
        correlation_matrix (pd.DataFrame): Matriz de correlación calculada 
            entre los vectores de los sujetos.
        feature_type (str): Identificador del tipo de matriz, utilizado para 
            el título principal de la figura.
        vmin (float, optional): Valor mínimo para la escala de colores del 
            mapa de calor. Por defecto es 0.86.
        save (str, optional): Ruta para guardar la figura generada.
        Si es None, la figura se mostrará en pantalla. Por defecto es None.
    """
    fig, (ax_heatmap, ax_boxplot) = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
    plt.suptitle(f"Matrices SCP {feature_type}")

    sns.heatmap(correlation_matrix, cmap="Reds", vmin=vmin, ax=ax_heatmap)
    ax_heatmap.set_title("Correlación del SCP por sujeto")

    sns.boxplot(data=correlation_matrix, ax=ax_boxplot)
    ax_boxplot.set_title("Distribución de Correlaciones por Sujeto")
    ax_boxplot.tick_params(axis='x', rotation=90)

    plt.tight_layout()
    plt.show()

    # Guardar la figura si se proporciona una ruta en alta resolución
    if save:
        plt.savefig(save, dpi=300, bbox_inches='tight')



def _calcular_correlacion_por_pares_de_tareas(df):
    """Calcula el triángulo superior de la matriz de correlación para las tareas.

    Agrupa los datos por tarea, calcula la media, genera la matriz de correlación 
    y extrae el triángulo superior para evitar redundancias, aplanando el resultado.

    Args:
        df (pd.DataFrame): DataFrame que contiene al menos la columna 'type_task' 
            y los datos numéricos a correlacionar.

    Returns:
        pd.Series: Serie con los pares de correlación aplanados y un índice 
        en formato string 'Tarea1 - Tarea2'.
    """
    df_mean_tareas = df.groupby("type_task").mean(numeric_only=True).T
    matriz_correlacion = df_mean_tareas.corr()
    
    mascara = np.triu(np.ones(matriz_correlacion.shape), k=1).astype(bool)
    triangulo_superior = matriz_correlacion.where(mascara)
    
    pares_correlacion = triangulo_superior.stack()
    pares_correlacion.index = pares_correlacion.index.map(lambda x: f"{x[0]} - {x[1]}")
    
    return pares_correlacion


def cargar_vectores_datasets(path, type_refs, dataset_type):
    """Carga y procesa los datasets de vectores (correlación o diferencia).

    Itera sobre los directorios de los sujetos, carga los archivos parquet 
    correspondientes según el tipo de dataset indicado, aplica filtros de tareas 
    específicos en caso de ser datos de correlación y extrae las correlaciones 
    por pares.

    Args:
        base_path (pathlib.Path): Ruta base del directorio con los datos.
        type_refs (list of str): Lista con los tipos de referencia a procesar.
        dataset_type (str): Tipo de dataset a cargar. Acepta 'corr' para datasets 
            de correlación y 'diff' para datasets de diferencia.

    Returns:
        dict: Diccionario con los datos consolidados donde las llaves principales 
        son los tipos de referencia y las llaves secundarias los sujetos.
        
    Raises:
        ValueError: Si el argumento dataset_type no es 'corr' ni 'diff'.
    """
    datos_correlacionados = {ref: {} for ref in type_refs}

    for path_sujeto in path.iterdir():
        if not path_sujeto.is_dir():
            continue
            
        sujeto = path_sujeto.name
        
        for type_ref in type_refs:
            if dataset_type == "corr":
                archivo = path / f"{sujeto}/{sujeto}_vector_corr_dataset.parquet"
            elif dataset_type == "diff":
                archivo = path / f"{sujeto}/{sujeto}_vector_diff_{type_ref}_dataset.parquet"
            else:
                raise ValueError("dataset_type debe ser 'corr' o 'diff'")

            if not archivo.exists():
                continue
                
            df = pd.read_parquet(archivo)
            df["type_task"] = df["type_task"].fillna("Restin")
            
            if dataset_type == "corr":
                df["type_ref"] = df["type_ref"].fillna("Restin")
                
                if type_ref == "tim-tfla":
                    df = df[df["type_ref"].isin(["Restin", "TIM", "TFLA"])]
                elif type_ref in ["tresp-temg", "tresp_temg"]: 
                    df = df[df["type_ref"].isin(["Restin", "TRESP", "TEMG"])]
            
            datos_correlacionados[type_ref][sujeto] = _calcular_correlacion_por_pares_de_tareas(df)

    return datos_correlacionados

def heatmaps_correlaciones_por_pares_de_tareas(datos_consolidados, type_refs, cmap, vmin, vmax, save=None):
    """Genera y muestra heatmaps a partir de datos correlacionados por pares de tareas
    para cada sujeto de las matrices de correlación promediadas por tarea.

    Convierte los diccionarios de correlación a DataFrames, elimina filas 
    vacías y crea un heatmap de Seaborn por cada tipo de referencia suministrado.

    Args:
        datos_consolidados (dict): Diccionario con los datos procesados.
        type_refs (list of str): Lista con los tipos de referencia (determina los subplots).
        cmap (str): Mapa de colores utilizado por Seaborn.
        vmin (float): Valor mínimo para la escala de color.
        vmax (float): Valor máximo para la escala de color.
        save (str, optional): Ruta para guardar la figura generada.
    """
    fig, axes = plt.subplots(nrows=len(type_refs), ncols=1, figsize=(16, 12))
    
    if len(type_refs) == 1:
        axes = [axes]

    for ax, type_ref in zip(axes, type_refs):
        df_heatmap = pd.DataFrame(datos_consolidados[type_ref])
        df_heatmap = df_heatmap.dropna(how='all')
        
        sns.heatmap(df_heatmap, cmap=cmap, vmin=vmin, vmax=vmax, ax=ax, cbar=True)
        
        ax.set_title(f"Correlaciones para matrices de correlación promediadas por tareas : {type_ref}", fontsize=14, pad=15)
        ax.set_xlabel("Sujetos", fontsize=12)
        ax.set_ylabel("Pares de Tareas", fontsize=12)
        
        ax.tick_params(axis='x', rotation=90) 
        ax.tick_params(axis='y', rotation=0)

    plt.tight_layout()
    plt.show()

    if save:
        plt.savefig(save, dpi=300, bbox_inches='tight')


def calcular_correlaciones_entre_referencias(path, ref_1, ref_2):
    """Calcula la correlación de Pearson entre dos tipos de referencia por tarea.

    Itera sobre los directorios de sujetos, carga los datasets de diferencia 
    para las dos referencias indicadas, calcula el promedio agrupado por 
    tarea y obtiene la correlación entre los vectores resultantes para 
    las tareas comunes.

    Args:
        base_path (pathlib.Path): Ruta base del directorio con los datos.
        ref_1 (str): Nombre de la primera referencia.
        ref_2 (str): Nombre de la segunda referencia.

    Returns:
        pd.DataFrame: DataFrame con las columnas 'Sujeto', 'Tarea' y 
        'Correlacion' consolidando los resultados de todos los sujetos.
    """
    correlaciones_por_tarea = []

    for path_sujeto in path.iterdir():
        if not path_sujeto.is_dir():
            continue
            
        sujeto = path_sujeto.name
        
        archivo_ref1 = path / f"{sujeto}/{sujeto}_vector_diff_{ref_1}_dataset.parquet"
        archivo_ref2 = path / f"{sujeto}/{sujeto}_vector_diff_{ref_2}_dataset.parquet"
        
        if not archivo_ref1.exists() or not archivo_ref2.exists():
            continue
            
        df_ref1 = pd.read_parquet(archivo_ref1)
        df_ref2 = pd.read_parquet(archivo_ref2)
        
        df_ref1["type_task"] = df_ref1["type_task"].fillna("Restin")
        df_ref2["type_task"] = df_ref2["type_task"].fillna("Restin")
        
        df_mean_ref1 = df_ref1.groupby("type_task").mean(numeric_only=True)
        df_mean_ref2 = df_ref2.groupby("type_task").mean(numeric_only=True)
        
        tareas_comunes = df_mean_ref1.index.intersection(df_mean_ref2.index)
        
        for tarea in tareas_comunes:
            vector_ref1 = df_mean_ref1.loc[tarea]
            vector_ref2 = df_mean_ref2.loc[tarea]
            
            correlacion = vector_ref1.corr(vector_ref2)
            
            correlaciones_por_tarea.append({
                "Sujeto": sujeto,
                "Tarea": tarea,
                "Correlacion": correlacion
            })

    return pd.DataFrame(correlaciones_por_tarea)


def graficar_boxplot_correlaciones(df_resultados, ref_1, ref_2, save=None):
    """Genera un boxplot con un stripplot superpuesto de las correlaciones por tarea.

    Muestra la distribución de las correlaciones de Pearson obtenidas 
    entre dos referencias a lo largo de los diferentes sujetos, 
    agrupadas por el tipo de tarea.

    Args:
        df_resultados (pd.DataFrame): DataFrame con los resultados. Debe contener 
            las columnas 'Tarea' y 'Correlacion'.
        ref_1 (str): Nombre de la primera referencia utilizada.
        ref_2 (str): Nombre de la segunda referencia utilizada.
        save (str, optional): Ruta para guardar la figura generada.
    """
    plt.figure(figsize=(12, 6))

    sns.boxplot(
        data=df_resultados, 
        x="Tarea", 
        y="Correlacion",
        hue="Tarea",
        palette="Set2",
        legend=False
    )

    sns.stripplot(
        data=df_resultados, 
        x="Tarea", 
        y="Correlacion", 
        color="black", 
        alpha=0.4, 
        size=4,
        jitter=True
    )

    plt.title(f"Correlación entre vectores promedio ({ref_1} vs {ref_2}) por Tarea", fontsize=14, pad=15)
    plt.xlabel("Tipo de Tarea", fontsize=12)
    plt.ylabel("Correlación de Pearson", fontsize=12)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    if save:
        plt.savefig(save, dpi=300, bbox_inches='tight')
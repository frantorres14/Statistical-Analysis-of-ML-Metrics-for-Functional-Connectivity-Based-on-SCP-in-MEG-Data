import numpy as np
import pandas as pd
import scipy.io as sio
import matplotlib.pyplot as plt
import re
from typing import List, Optional, Union

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
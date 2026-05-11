from pathlib import Path

# --- RUTAS DE DIRECTORIOS ---
# Esto encuentra la raíz del proyecto dinámicamente
BASE_DIR = Path(__file__).resolve().parent.parent

# Rutas estándar para los datos
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# --- PARÁMETROS DEL EEG / NEUROIMAGEN ---
FS = 508.6275  # Frecuencia de muestreo original

# --- PARÁMETROS DEL FILTRO ---
FILTER_ORDER = 4
FREQ_LOW = 1.0
FREQ_HIGH = 40.0
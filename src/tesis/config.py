from pathlib import Path

# --- RUTAS DE DIRECTORIOS ---
# Esto encuentra la raíz del proyecto dinámicamente
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Rutas estándar para los datos
DATA_RAW_DIR = BASE_DIR / "data" / "raw_data"
DATA_INTERMEDIATE_DIR = BASE_DIR / "data" / "intermediate_data"

# --- PARÁMETROS DEL MEG  ---
FS = 508.6275  # Frecuencia de muestreo original
CANALES_VALIDOS=  ['A56', 'A215', 'A178', 'A125', 'A81', 'A130', 'A207', 'A200', 'A180', 'A49', 'A118', 'A138', 'A181',
                   'A195', 'A131', 'A114', 'A66', 'A221', 'A30', 'A141', 'A167', 'A166', 'A97', 'A44', 'A216', 'A40',
                   'A69', 'A192', 'A144', 'A206', 'A12', 'A25', 'A224', 'A46', 'A239', 'A65', 'A168', 'A31', 'A101',
                   'A117', 'A80', 'A14', 'A194', 'A86', 'A57', 'A54', 'A11', 'A219', 'A161', 'A109', 'A234', 'A51',
                   'A135', 'A199', 'A208', 'A3', 'A151', 'A92', 'A93', 'A72', 'A115', 'A110', 'A78', 'A136', 'A107',
                   'A10', 'A142', 'A185', 'A209', 'A133', 'A82', 'A58', 'A84', 'A95', 'A100', 'A140', 'A48', 'A132',
                   'A89', 'A13', 'A7', 'A134', 'A83', 'A127', 'A71', 'A169', 'A186', 'A184', 'A106', 'A42', 'A171',
                   'A26', 'A105', 'A202', 'A35', 'A174', 'A96', 'A158', 'A67', 'A108', 'A213', 'A24', 'A218', 'A79',
                   'A23', 'A149', 'A160', 'A242', 'A39', 'A32', 'A191', 'A156', 'A179', 'A21', 'A47', 'A16', 'A64',
                   'A55', 'A98', 'A163', 'A165', 'A139', 'A233', 'A4', 'A22', 'A43', 'A77', 'A85', 'A76', 'A50', 'A9',
                   'A29', 'A137', 'A143', 'A204', 'A99', 'A53', 'A240', 'A188', 'A75', 'A28', 'A33', 'A203', 'A34',
                   'A74', 'A170', 'A103', 'A91', 'A27', 'A220', 'A154', 'A164', 'A113'] # Canales que aparecen en todos los registros


# --- PARÁMETROS DEL FILTRO ---
FILTER_ORDER = 4
FREQ_LOW = 1.0
FREQ_HIGH = 40.0


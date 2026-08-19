from pathlib import Path
from scipy.stats import randint, uniform, loguniform
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


# --- RUTAS DE DIRECTORIOS ---
# Esto encuentra la raíz del proyecto dinámicamente
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Rutas estándar para los datos
DATA_RAW_DIR = BASE_DIR / "data" / "raw_data"
DATA_INTERMEDIATE_DIR = BASE_DIR / "data" / "intermediate_data"

# --- PARÁMETROS DEL MEG  ---
FS = 508.6275  # Frecuencia de muestreo original

CANALES_VALIDOS = [ # Canales que aparecen en los registros de todos los sujetos
    'A91', 'A92', 'A64', 'A39', 'A21', 'A22', 'A40', 'A65', 'A66', 'A23', 
    'A24', 'A25', 'A26', 'A42', 'A43', 'A44', 'A67', 'A69', 'A46', 'A47', 
    'A71', 'A72', 'A100', 'A101', 'A103', 'A135', 'A136', 'A163', 'A164', 
    'A184', 'A185', 'A186', 'A218', 'A202', 'A219', 'A203', 'A220', 'A95', 
    'A127', 'A93', 'A125', 'A154', 'A178', 'A213', 'A179', 'A97', 'A98', 
    'A99', 'A130', 'A131', 'A158', 'A96', 'A156', 'A233', 'A180', 'A132', 
    'A133', 'A134', 'A181', 'A160', 'A161', 'A215', 'A199', 'A234', 'A216', 
    'A200', 'A4', 'A7', 'A89', 'A3', 'A9', 'A10', 'A11', 'A12', 'A13', 
    'A14', 'A16', 'A27', 'A28', 'A29', 'A48', 'A49', 'A50', 'A74', 'A75', 
    'A76', 'A105', 'A137', 'A151', 'A118', 'A86', 'A35', 'A58', 'A85', 
    'A34', 'A57', 'A84', 'A30', 'A31', 'A32', 'A33', 'A53', 'A54', 'A55', 
    'A56', 'A80', 'A81', 'A82', 'A83', 'A51', 'A77', 'A78', 'A79', 'A107', 
    'A108', 'A109', 'A110', 'A106', 'A138', 'A139', 'A165', 'A166', 'A167', 
    'A188', 'A204', 'A239', 'A221', 'A240', 'A206', 'A149', 'A117', 'A115', 
    'A174', 'A194', 'A195', 'A113', 'A114', 'A144', 'A143', 'A171', 'A192', 
    'A209', 'A140', 'A141', 'A142', 'A170', 'A168', 'A169', 'A191', 'A207', 
    'A208', 'A224', 'A242'
]

# Mapeos de canales de MEG a EEG
MAPEO_C1 = {
    'Fp1': 'A91', 
    'F3': 'A40', 
    'C3': 'A44', 
    'P3': 'A72', 
    'O1': 'A184', 
    'F7': 'A95', 
    'T3': 'A130', 
    'T5': 'A160', 
    'Fz': 'A4', 
    'Cz': 'A10', 
    'Pz': 'A49', 
    'Fp2': 'A151', 
    'F4': 'A58', 
    'C4': 'A54', 
    'P4': 'A78', 
    'O2': 'A167',
    'F8': 'A115', 
    'T4': 'A144', 
    'T6': 'A169', 
}

MAPEO_C2_C3 = {
    'Fp1': ['A91', 'A92'], 
    'F3': ['A64', 'A39', 'A21', 'A22', 'A40', 'A65', 'A66'], 
    'C3': ['A23', 'A24', 'A25', 'A26', 'A42', 'A43', 'A44', 'A67', 'A69'], 
    'P3': ['A46', 'A47', 'A71', 'A72', 'A100', 'A101', 'A103'], 
    'O1': ['A135', 'A136', 'A163', 'A164', 'A184', "A185"], 
    'F7': ['A95', 'A127', 'A93', 'A125', 'A154'], 
    'T3': ['A97', 'A98', 'A99', 'A130', 'A131', 'A158', 'A96', 'A156'], 
    'T5': ['A132', 'A133', 'A134', 'A181', 'A160', 'A161'], 
    'Fz': ['A4', 'A7'], 
    'Cz': ['A3', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A16'], 
    'Pz': ['A27','A28', 'A29', 'A48', 'A49', 'A50', 'A74', 'A75', 'A76'], 
    'Fp2': ['A151', 'A118'], 
    'F4': ['A86', 'A35', 'A58', 'A85', 'A34', 'A57', 'A84'], 
    'C4': ['A30', 'A31', 'A32', 'A33', 'A53', 'A54', 'A55', 'A56', 'A80', 'A81', 'A82', 'A83'], 
    'P4': ['A51', 'A77', 'A78', 'A79', 'A107', 'A108', 'A109', 'A110'], 
    'O2': ['A106', 'A138', 'A139', 'A165', 'A166', 'A167', 'A188'],
    'F8': ['A149', 'A117', 'A115'], 
    'T4': ['A113', 'A114', 'A144', 'A143', 'A171'], 
    'T6': ['A140', 'A141', 'A142', 'A170', 'A168', 'A169', 'A191']
}

# --- PARÁMETROS DEL FILTRO ---
FILTER_ORDER = 4
FREQ_LOW = 1.0
FREQ_HIGH = 40.0


# --- PARÁMETROS DE TRIALINFO ---
COLUMNAS_TRIALINFO_WRKMEM= [
    "run", "block", "id_nan", "img_type", "mem_type", 
    "target_type", "trigger_onset", "trigger_offset", "seq_of_img", "is_pressed",
    "is_pressed_late", "is_double_resp", "pressed_code", "is_correct", "is_lure_correct",
    "resp_time", "resp_duration", "is_first_block", "is_last_block", "prev_run",
    "prev_block", "prev_id_nan", "prev_img_type", "prev_mem_type", "prev_target_type",
    "prev_trigger_onset", "prev_trigger_offset", "prev_seq_of_img", "prev_is_pressed", "prev_is_pressed_late",
    "prev_is_double_resp", "prev_pressed_code", "prev_is_correct", "prev_is_lure_correct", "prev_resp_time",
    "prev_resp_duration", "prev_is_first_block", "prev_is_last_block", "press_on_onset", "has_trial_nans"
]


configs_models = {
    "XGBoost": {
        "estimator":XGBClassifier(),
        "search_type":"random",
        "params": {
            "objective":["multi:softprob"], 
            "num_class":[7],
            "eval_metric":["mlogloss"],
            "n_estimators": [100, 300, 500, 800],
            "eta": [0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3],
            "max_depth": [3, 4, 5, 6, 7, 8, 9, 10, 12],
            "min_child_weight": [1, 2, 3, 5, 7, 10, 15, 20],
            "gamma": [0, 0.1, 0.3, 0.5, 1, 2, 3, 5, 10],
            "subsample":[0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            "colsample_bytree": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            "reg_alpha": [0, 0.01, 0.1, 0.5, 1, 2, 5, 10],
            "reg_lambda": [0.1, 0.5, 1, 2,5, 10, 20, 50]
        }
    },
    "LogisticRegression":{
        "estimator":LogisticRegression(),
        "search_type":"grid",
        "params":{
            "solver":["lbfgs"],
            "max_iter":[2000],
            "C":[0.01, 0.1, 1, 10, 100]
        }
    }
}
"""
VALORES DE HIPERPARAMETROS POR DEFECTO para XGboost
"booster":"gbtree",
"tree_metod":"auto",
"colsample_bylevel":1.0,
"colsample_bynode":1.0,
"scale_pos_weight":1.0,
"max_delta_step":0
"""
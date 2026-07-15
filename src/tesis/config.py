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

# --- HIPERPARAMETROS DE LOS MODELOS
XGBOOST_HIPERPARAMETERS = {
    "eta": [0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3],
    "max_depth": [3, 4, 5, 6, 7, 8, 9, 10, 12],
    "min_child_weight": [1, 2, 3, 5, 7, 10, 15, 20],
    "gamma": [0, 0.1, 0.3, 0.5, 1, 2, 3, 5, 10],
    "subsample": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "reg_alpha": [0, 0.01, 0.1, 0.5, 1, 2, 5, 10],
    "reg_lambda": [0.1, 0.5, 1, 2,5, 10, 20, 50]
}


configs_models = {
    "XGBoost": {
        "estimator":XGBClassifier,
        "search_type":"random",
        "params": {
            "n_estimators":[1000],
            "objective":["multi:softprob"], 
            "num_class":[7],
            "eval_metric":["mlogloss"],
            "eta": loguniform(1e-3, 3e-1),
            "max_depth": randint(3, 13),
            "min_child_weight": randint(1, 21),
            "gamma": uniform(0, 10),
            "subsample": uniform(0.5, 0.5),
            "colsample_bytree": uniform(0.4, 0.6),
            "reg_alpha": loguniform(1e-3, 10),
            "reg_lambda": loguniform(1e-1, 50),
        }
    },
    "LogisticRegression":{
        "estimator":LogisticRegression,
        "search_type":"grid",
        "params":{
            "random_state":[714],
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
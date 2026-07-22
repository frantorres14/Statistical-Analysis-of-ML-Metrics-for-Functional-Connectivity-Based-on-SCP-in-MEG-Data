import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.model_selection import GroupKFold, GridSearchCV, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from tesis.evaluate import evaluate_and_log_fold
import wandb

def load_and_split_data(filepath: str) -> tuple:
    """Carga el dataset particionado y separa las características, la variable objetivo y los grupos.

    Args:
        filepath (str): Ruta al archivo parquet procesado.

    Returns:
        tuple: Una tupla que contiene:
            - X (pd.DataFrame): Matriz de características.
            - y (pd.Series): Variable objetivo.
            - groups (pd.Series): Identificadores de los sujetos (grupos).
    """
    df = pd.read_parquet(filepath)
    X = df.drop(columns=["target", "sujeto"])
    y = df["target"]
    groups = df["sujeto"]
    
    return X, y, groups

def build_pipeline(estimator, pca: bool = True, n_components: int = 400, random_state: int = 14) -> Pipeline:
    """Construye un pipeline de scikit-learn con PCA y el estimador proporcionado.

    Args:
        estimator: Instancia de un modelo de scikit-learn.
        pca (bool, optional): Indica si se debe aplicar PCA antes del estimador. Por defecto es True.
        n_components (int, optional): Número de componentes principales a retener. Por defecto es 400.
        random_state (int, optional): Semilla para la reproducibilidad. Por defecto es 14.

    Returns:
        Pipeline: El pipeline configurado.
    """
    if not pca:
        pipeline = Pipeline([
            ('clf', estimator)
        ])
    else:
        pipeline = Pipeline([
            ('pca', PCA(n_components=n_components, random_state=random_state)),
            ('clf', estimator)
        ])
    
    return pipeline

def run_nested_cv(X: pd.DataFrame,
                  y: pd.Series,
                  groups: pd.Series,
                  pipeline: Pipeline,
                  param_grid: dict,
                  model_name:str,
                  search_type: str = "random",
                  n_iter: int = 60,
                  n_outer: int = 6,
                  n_inner: int = 5,
                  start_fold: int = 1,
                  data_name: str = "dataset",
                  n_jobs: int = 1) -> list:
    """Ejecuta validación cruzada anidada soportando Grid Search y Random Search dinámicamente.

    Args:
        X (pd.DataFrame): Matriz de características.
        y (pd.Series): Variable objetivo.
        groups (pd.Series): Identificadores de grupo.
        pipeline (Pipeline): Pipeline estimador a evaluar.
        param_grid (dict): Diccionario con la grilla o distribución de hiperparámetros.
        model_name (str): Nombre del modelo.
        raw_params (dict): Parámetros originales.
        search_type (str, optional): Tipo de búsqueda ('grid' o 'random'). Por defecto 'grid'.
        n_iter (int, optional): Número de iteraciones para Random Search. Por defecto 10.
        n_outer (int, optional): Folds externos. Por defecto 6.
        n_inner (int, optional): Folds internos. Por defecto 5.

    Returns:
        list: Scores del bucle externo.
    """
    cv_outer = GroupKFold(n_splits=n_outer)
    cv_inner = GroupKFold(n_splits=n_inner)
    outer_scores = []
    
    for fold, (train_idx, test_idx) in enumerate(cv_outer.split(X, y, groups)):

        if (fold + 1) < start_fold:
            print(f"Saltando Fold {fold + 1}...")
            continue
        
        wandb.init(
            entity="frantorresia",
            project="tesis_hcp",
            group=f"NestedCV_{model_name}_{data_name}", 
            name=f"{model_name}_Fold_{fold + 1}_{data_name}",
            config={
                "model": model_name,
                "fold": fold + 1,
                "search_type": search_type,
                "data_name": data_name,
                "k_inner_folds": n_inner
            }
        )
        
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        groups_train = groups.iloc[train_idx]
        groups_test = groups.iloc[test_idx]
        
        if search_type == "random":
            search = RandomizedSearchCV(
                estimator=pipeline,
                param_distributions=param_grid,
                n_iter=n_iter,
                cv=cv_inner,
                scoring='neg_log_loss',
                n_jobs=n_jobs,
                random_state=714
            )
        else:
            search = GridSearchCV(
                estimator=pipeline,
                param_grid=param_grid,
                cv=cv_inner,
                scoring='neg_log_loss',
                n_jobs=n_jobs
            )
        
        search.fit(X_train, y_train, groups=groups_train)
        
        best_model = search.best_estimator_
        y_pred = best_model.predict(X_test)

        best_params = {k.replace('clf__', ''): v for k, v in search.best_params_.items()}
        
        wandb.config.update(best_params)
        
        test_score = evaluate_and_log_fold(
            fold=fold + 1,
            y_true=y_test,
            y_pred=y_pred,
            groups_test=groups_test,
            best_params=best_params 
        )
        
        outer_scores.append(test_score)
        print(f"Fold {fold + 1}/{n_outer} | Mejores params: {best_params} | Score: {test_score:.4f}")
        
        wandb.finish()
        
    return outer_scores
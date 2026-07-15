import numpy as np
import pandas as pd
import wandb
from sklearn.metrics import accuracy_score, classification_report

def evaluate_and_log_fold(fold: int, y_true: pd.Series, y_pred: np.ndarray, groups_test: pd.Series, best_params: dict) -> float:
    """Calcula y registra en WandB las métricas de un fold específico y su matriz de confusión.

    Args:
        fold (int): Número del fold actual.
        y_true (pd.Series): Valores reales de la variable objetivo.
        y_pred (np.ndarray): Valores predichos por el modelo.
        groups_test (pd.Series): Identificadores de los grupos en el conjunto de prueba.
        best_params (dict): Diccionario con los mejores hiperparámetros encontrados.

    Returns:
        float: El accuracy global del fold para almacenar en el historial externo.
    """
    test_score = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    
    log_metrics = {
        "fold": fold,
        "outer_fold_accuracy": test_score
    }
        
    for g in groups_test.unique():
        mask = (groups_test == g)
        group_acc = accuracy_score(y_true[mask], y_pred[mask])
        log_metrics[f"accuracy_group_{g}"] = group_acc
        
    for class_label, metrics in report.items():
        if isinstance(metrics, dict):
            log_metrics[f"precision_class_{class_label}"] = metrics["precision"]
            log_metrics[f"recall_class_{class_label}"] = metrics["recall"]
            log_metrics[f"f1_class_{class_label}"] = metrics["f1-score"]
            
    wandb.log({
        **log_metrics,
        "confusion_matrix": wandb.plot.confusion_matrix(
            preds=y_pred, 
            y_true=y_true.values, 
            title=f"Confusion Matrix Fold {fold}"
        )
    })
    
    return test_score

def print_summary(scores: list) -> None:
    """Imprime un resumen estadístico global en la consola local.

    Args:
        scores (list): Lista de métricas de rendimiento por cada fold.
    """
    mean_score = np.mean(scores)
    std_score = np.std(scores)
    
    print("Rendimiento global (Promedio ± Desviación Estándar):")
    print(f"{mean_score:.4f} ± {std_score:.4f}\n")
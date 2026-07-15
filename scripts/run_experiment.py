import argparse
from dotenv import load_dotenv
from tesis.train import load_and_split_data, build_pipeline, run_nested_cv
from tesis.evaluate import print_summary
from tesis.config import configs_models

load_dotenv() #Carga las variables de entornos, en específico la API de W&B para iniciar sesión

def parse_args() -> argparse.Namespace:
    """Parsea los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(description="Entrenamiento con Nested CV")
    parser.add_argument("--data_path", type=str, help="Ruta al archivo de datos")
    parser.add_argument("--model", type=str, required=True, help="Nombre del modelo")
    parser.add_argument("--search_type", type=str, required=True, choices=["grid", "random"], help="Tipo de búsqueda de hiperparámetros")

    return parser.parse_args()

def main():
    args = parse_args()
    model_name = args.model
    
    if model_name not in configs_models:
        raise ValueError(f"El modelo '{model_name}' no existe en config.py")
        
    config = configs_models[model_name]
    estimator = config["estimator"]
    raw_params = config["params"]
    
    filepath = args.data_path
    X, y, groups = load_and_split_data(filepath)
    
    pipeline_params = {f"clf__{key}": value for key, value in raw_params.items()}
    pipeline = build_pipeline(estimator=estimator)
    
    outer_scores = run_nested_cv(
        X=X, 
        y=y, 
        groups=groups, 
        pipeline=pipeline, 
        param_grid=pipeline_params,
        model_name=model_name,
        raw_params=raw_params,
        search_type=args.search_type
    )
    
    print_summary(outer_scores)

if __name__ == "__main__":
    main()
# Comando para correrlo: uv run scripts/run_experiment.py --data_path "data/processed/HCP_corr_dataset.parquet" --model "LogisticRegression" --search_type "grid"
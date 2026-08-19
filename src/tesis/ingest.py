import os
from pathlib import Path
from typing import Union
import wandb


def download_wandb_artifacts(
    project_path: str, output_dir: Union[str, Path]
) -> None:
    """Descarga todos los artifacts registrados de un proyecto de WandB.

    Itera sobre las ejecuciones (runs) de un proyecto de Weights & Biases y
    descarga sus artifacts en carpetas organizadas por el nombre del run.
    Limpia los nombres de los artifacts para evitar caracteres no válidos.

    Args:
        project_path: Ruta del proyecto en WandB con formato 'entidad/proyecto'.
        output_dir: Directorio base donde se guardarán los artifacts descargados.
    """
    api = wandb.Api()
    base_dir = Path(output_dir)

    print(f"Obteniendo runs del proyecto: {project_path}...")
    runs = api.runs(project_path)

    # Procesar las ejecuciones del proyecto
    for run in runs:
        print(f"\nRevisando run: {run.name} (ID: {run.id})")

        artifacts = run.logged_artifacts()
        if not artifacts:
            print("  -> No hay artifacts en este run.")
            continue

        # Descargar cada artifact registrado
        for artifact in artifacts:
            # Sanitizar el nombre para compatibilidad con el sistema de archivos
            artifact_name_safe = artifact.name.replace(":", "_")
            download_path = base_dir / run.name / artifact_name_safe

            print(
                f"  -> Descargando artifact: {artifact.name} (v{artifact.version})"
            )
            artifact.download(root=str(download_path))
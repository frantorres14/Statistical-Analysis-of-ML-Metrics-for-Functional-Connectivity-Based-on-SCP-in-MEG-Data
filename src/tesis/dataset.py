import pandas as pd
import numpy as np
import scipy.io as sio
import boto3
import os

def listar_subcarpetas_s3(bucket_nombre, ruta_padre):
    """
    Función que imprime todas las carpetas dentro de una carpeta
    de un bucket de s3
    """
    s3 = boto3.client('s3', 
        aws_access_key_id='AKIAXO65CT57BZZXU7U2',
        aws_secret_access_key='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'
    )

    # Asegurarse de que la ruta padre termine en /
    if not ruta_padre.endswith('/') and ruta_padre != "":
        ruta_padre += '/'

    # Usamos Delimiter='/' para que S3 agrupe los resultados por carpetas
    response = s3.list_objects_v2(
        Bucket=bucket_nombre, 
        Prefix=ruta_padre, 
        Delimiter='/'
    )

    # Los nombres de las carpetas vienen en 'CommonPrefixes'
    print(f"Subcarpetas encontradas en '{ruta_padre}':")
    
    if 'CommonPrefixes' in response:
        for obj in response['CommonPrefixes']:
            # El nombre viene completo, lo limpiamos para mostrar solo el final
            nombre_carpeta = obj['Prefix'].replace(ruta_padre, "").replace("/", "")
            print(f"{nombre_carpeta}")
    else:
        print(" No se encontraron subcarpetas.")


def descargar_carpeta_s3(bucket_nombre, s3_ruta_carpeta, local_ruta_destino):
    """
    Función para descargar una carpeta de algún bucket de s3
    """
    # Inicializar el cliente de S3
    s3 = boto3.client('s3', 
        aws_access_key_id='AKIAXO65CT57BZZXU7U2',
        aws_secret_access_key='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'
    )

    # Listar objetos dentro del "directorio" de S3
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_nombre, Prefix=s3_ruta_carpeta):
        if 'Contents' in page:
            for obj in page['Contents']:
                # Obtener la ruta del archivo
                s3_key = obj['Key']
                
                if s3_key.lower().endswith(".mat"):
                    # Definir dónde se guardará localmente
                    # (Quitamos el prefijo de S3 para que no cree carpetas extra innecesarias)
                    relative_path = os.path.relpath(s3_key, s3_ruta_carpeta)
                    local_file_path = os.path.join(local_ruta_destino, relative_path)

                    # Crear los directorios locales si no existen
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                    # No descargar si es un "directorio" vacío en S3
                    if not s3_key.endswith('/'):
                        print(f"Descargando: {s3_key}...")
                        s3.download_file(bucket_nombre, s3_key, local_file_path)
                else:
                    continue
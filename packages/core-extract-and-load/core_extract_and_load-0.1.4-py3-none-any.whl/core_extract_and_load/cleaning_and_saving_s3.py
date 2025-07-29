import sqlite3
import boto3
from dataclasses import dataclass
import pandas as pd
from botocore.exceptions import ClientError
import os
from typing import Optional

global REGION_NAME, S3_FILENAME, BUCKETNAME, DB_PATH
REGION_NAME: str = "us-east-1"
S3_FILENAME: str = "archivo.csv"
BUCKET_NAME: str = "COREANDSTRACT"
DB_PATH: str = "demo.db"


def obtener_ultima_fila_sqlite(db_path: str, tabla: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {tabla} ORDER BY id DESC LIMIT 1"  
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def descargar_csv_de_s3(client, bucket_name: str, s3_filename: str, local_path: str, headers=None) -> bool:
    try:
        client.download_file(bucket_name, s3_filename, local_path)
        print(f"Descargado: s3://{bucket_name}/{s3_filename}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(f"Archivo no existe en S3. Se creará uno nuevo en {local_path}")
            if headers is not None and len(headers) > 0:
                df_vacio = pd.DataFrame(columns=headers)
                df_vacio.to_csv(local_path, index=False)
            return False
        else:
            raise

def agregar_fila_al_csv(nueva_fila: pd.DataFrame, local_path: str):
    df_csv = pd.read_csv(local_path)
    df_actualizado = pd.concat([df_csv, nueva_fila], ignore_index=True)
    df_actualizado.to_csv(local_path, index=False)

def subir_csv_a_s3(client, bucket_name: str, s3_filename: str, local_path: str):
    client.upload_file(local_path, bucket_name, s3_filename)
    print(f"Subido a s3://{bucket_name}/{s3_filename}")

@dataclass()
class MainDTO:
    aws_access_key_id: str
    aws_secret_access_key: str
    bucket_name: Optional[str]
    region_name: Optional[str]
    s3_filename: Optional[str]
    db_path: Optional[str]

def actualizar_csv_s3_con_sqlite(dto: MainDTO) -> None:
    
    local_csv_path = "/tmp/tmp.csv"
    db_path = dto.db_path or DB_PATH
    bucket_name = dto.bucket_name or BUCKET_NAME
    s3_filename = dto.s3_filename or S3_FILENAME

    client = boto3.client(
        's3',
        aws_access_key_id = dto.aws_access_key_id,
        aws_secret_access_key = dto.aws_secret_access_key,
        region_name = dto.region_name or REGION_NAME
    )

    nueva_fila = obtener_ultima_fila_sqlite(
        db_path=db_path, 
        tabla="cotizacion"
    )

    descargar_csv_de_s3(
        client=client, 
        bucket_name=bucket_name, 
        s3_filename=s3_filename, 
        local_path=local_csv_path, 
        headers=nueva_fila.columns
    )

    agregar_fila_al_csv(nueva_fila, local_csv_path)

  
    subir_csv_a_s3(client, bucket_name, s3_filename, local_csv_path)

## Develop
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()  

    dto = MainDTO(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        bucket_name=None, #os.getenv("BUCKET_NAME")
        region_name=None, #os.getenv("AWS_REGION")
        s3_filename=None, #os.getenv("S3_FILENAME")
        db_path=os.getenv("DB_PATH")   
    )

    if os.getenv("AWS_BUCKET_NAME"):
        dto.bucket_name = os.getenv("AWS_BUCKET_NAME")

    if os.getenv("AWS_REGION"):
        dto.bucket_name = os.getenv("AWS_REGION")

    #dto.aws_access_key_id = ""
    #dto.aws_secret_access_key = ""

    actualizar_csv_s3_con_sqlite(dto)
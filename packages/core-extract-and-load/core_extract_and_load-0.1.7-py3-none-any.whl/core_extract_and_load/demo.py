import os
from dotenv import load_dotenv
from .main import extract_and_load
from .cleaning_and_saving_s3 import MainDTO, actualizar_csv_s3_con_sqlite

load_dotenv()  

def demo():
    DB_PATH = os.getenv('DB_PATH')
    extract_and_load(DB_PATH)

    dto = MainDTO(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        bucket_name=os.getenv("AWS_BUCKET_NAME"),
        region_name=None, #os.getenv("AWS_REGION"),
        s3_filename=os.getenv("S3_FILENAME"),
        db_path=DB_PATH  
    )

    actualizar_csv_s3_con_sqlite(dto)

    print("programa finalizado")

if __name__ == "__main__":
    demo()

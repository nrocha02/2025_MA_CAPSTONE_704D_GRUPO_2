# database.py
from sqlmodel import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

mysql_url = f"mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}"

engine = create_engine(
    mysql_url, 
    connect_args={
        "ssl": {
            "ca": os.getenv("SSL_CERT_PATH")
        }
    }, echo=True
)

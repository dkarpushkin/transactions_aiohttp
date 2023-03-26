import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG: bool = True
    HOST: str = 'localhost'
    PORT: int = '8000'
    DATABASE_URI: str = f'postgres://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_SERVER"]}/{os.environ["POSTGRES_DB"]}'

import dotenv 
import os

dotenv.dotenv_path = ("../.env")
dotenv.load_dotenv(dotenv.find_dotenv())


INIT_DB=True

SECRET_KEY=os.environ.get('SECRET_KEY')
ALGORITHM=os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))

DBNAME=os.environ.get('DBNAME')
DB_USER=os.environ.get('DB_USER')
DB_PASSWORD=os.environ.get('DB_PASSWORD')
HOST=os.environ.get('HOST')

import psycopg2

from app.settings import DBNAME, DB_USER, DB_PASSWORD, HOST


def get_connection():
    conn = psycopg2.connect(dbname=DBNAME, user=DB_USER, 
                password=DB_PASSWORD, host=HOST)
    
    return conn
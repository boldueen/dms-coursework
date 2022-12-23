from fastapi import FastAPI, Depends
import psycopg2

from app.routes import api_router

app = FastAPI(title="web shop")

app.include_router(api_router, prefix="/api")

# origins = ["*"]
# app.add_middleware(
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



@app.on_event("startup")
def startup():
    conn = psycopg2.connect(dbname='postgres', user='postgres', 
                        password='postgres', host='db')
    
    ini_script = open("app/ini_coursework.sql", "r").read()
    cursor = conn.cursor()
    cursor.execute(ini_script)
    conn.commit()

    roles_ini_script = open("app/roles.sql", "r").read()
    cursor.execute(roles_ini_script)
    cursor.close()

    conn.commit()
    conn.close()
    print("database initialize")
    pass

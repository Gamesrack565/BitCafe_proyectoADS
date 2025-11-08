#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerías y módulos
from sqlmodel import SQLModel, create_engine, Session
from typing_extensions import Annotated
from fastapi import Depends

#Base de datos:
sql_url = "mysql+pymysql://root:1999456@localhost:3306/bitcafe_db?charset=utf8mb4"

engine = create_engine(sql_url, echo=True)

#Define un generador para gestionar las sesiones de la base de datos.
def get_session():
    #Crea una nueva sesion usando el motor.
    with Session(engine) as session:
        #Proporciona la sesion a la funcion del endpoint.
        yield session
        #El bloque 'with' asegura que la sesion se cierre automaticamente.

#Crea un alias 'SessionDep' para la inyeccion de dependencias de la sesion.
SessionDep=Annotated[Session, Depends(get_session)] 

def create_db_and_tables():
    """
    Crea todas las tablas en la base de datos que 
    hereden de SQLModel (definidas en Modelos/models.py).
    """
    SQLModel.metadata.create_all(engine)

#Para checar si se conecto la base de datos
#if __name__ == "__main__":
#    try:
#        with engine.connect() as conn:
#            print("Conexion correcta")
#    except Exception as e:
#        print("error de conexion:")
#        print(e)

# BITCAFE - VERSION 1.1
# By: Angel A. Higuera & Gemini Partner

# Librerías y módulos
from sqlmodel import SQLModel, create_engine, Session
from typing_extensions import Annotated
from fastapi import Depends

# Base de datos:
# Se agrega pool_pre_ping para evitar errores de 'MySQL server has gone away' 
# y se asegura el charset utf8mb4.
sql_url = "mysql+pymysql://root:@localhost:3306/bitcafe_db?charset=utf8mb4"

engine = create_engine(
    sql_url, 
    echo=True,
    pool_pre_ping=True,  # Verifica que la conexión esté viva antes de usarla
    pool_recycle=3600    # Reinicia conexiones viejas para evitar bloqueos
)

# Define un generador para gestionar las sesiones de la base de datos.
def get_session():
    # Crea una nueva sesion usando el motor.
    with Session(engine) as session:
        # Proporciona la sesion a la funcion del endpoint.
        yield session
        # El bloque 'with' asegura que la sesion se cierre automaticamente.

# Crea un alias 'SessionDep' para la inyeccion de dependencias de la sesion.
SessionDep = Annotated[Session, Depends(get_session)] 

def create_db_and_tables():
    """
    Crea todas las tablas en la base de datos que 
    hereden de SQLModel.
    """
    SQLModel.metadata.create_all(engine)

# Bloque de prueba de conexión opcional
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("--- CONEXIÓN EXITOSA A MYSQL (BITCAFE) ---")
    except Exception as e:
        print(f"--- ERROR DE CONEXIÓN: {e} ---")
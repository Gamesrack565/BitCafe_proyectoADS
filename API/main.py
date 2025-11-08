#BITCAFE
#VERSION 1
#By: Angel A. Higuera

#Modulos y librerias
from fastapi import FastAPI
from Servicios.base_Datos import create_db_and_tables
from contextlib import asynccontextmanager
from Rutas import categorias, productos, usuarios, auth, carritos, pedidos, pagos

#COSAS A CORREGIR, se encuentra en el txt 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando API... Creando tablas si no existen.")
    create_db_and_tables()
    yield
    print("Apagando API.")

#Titulo de la API y descripcion
app = FastAPI(
    title="API de BitCafé",
    description="API para gestionar la cafetería BitCafé.",
    version="1.2.0",
    lifespan=lifespan
)

app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios")
app.include_router(categorias.router, prefix="/categorias", tags=["Categorías"])
app.include_router(productos.router, prefix="/productos", tags=["Productos"])
app.include_router(carritos.router)
app.include_router(pedidos.router)
app.include_router(pagos.router)

#Verificacion de funcionamiento e inicio de la API
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de BitCafé v1.0"}


#BITCAFE
#VERSION 2
#By: Angel A. Higuera

#Modulos y librerias
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from Servicios.base_Datos import create_db_and_tables
from contextlib import asynccontextmanager
from Rutas import categorias, productos, usuarios, auth, carritos, pedidos, pagos, pedidos_caja, configuracion
import os

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


if not os.path.exists("static_images"):
    os.makedirs("static_images")

#Montamos la carpeta para guardar imagenes
#Esto significa que todo lo que esté en la carpeta "static_images"
#será accesible en la dirección: http://localhost:8000/imagenes/nombre_archivo.jpg
app.mount("/imagenes", StaticFiles(directory="static_images"), name="imagenes")


app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios")
app.include_router(categorias.router, prefix="/categorias", tags=["Categorías"])
app.include_router(productos.router, prefix="/productos", tags=["Productos"])
app.include_router(carritos.router)
app.include_router(pedidos.router)
app.include_router(pedidos_caja.router)
app.include_router(pagos.router)
app.include_router(configuracion.router)


#Verificacion de funcionamiento e inicio de la API
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de BitCafé v1.0"}


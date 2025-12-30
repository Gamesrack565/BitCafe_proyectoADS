#BITCAFE
#VERSION 1.2
#By: Angel A. Higuera

#Librerías y módulos
import uuid
import os
import shutil
from decimal import Decimal
from typing import List, Optional

#Importa las clases de FastAPI
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form

#Importas de SQLAlchemy y SQLModel
from sqlalchemy.orm import joinedload
from sqlmodel import select

#Importa dependencias y modelos propios
from Servicios.base_Datos import SessionDep
from Modelos import modelos
from Esquemas import esquemas

#Crea una nueva instancia de APIRouter, definiendo el prefijo y la etiqueta.
router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("/", 
              response_model=esquemas.ProductoLecturaConCategoria,
              status_code=status.HTTP_201_CREATED)
def crear_producto(
    session: SessionDep,
    nombre: str = Form(...),
    descripcion: str = Form(None),
    precio: Decimal = Form(...),
    esta_disponible: bool = Form(True),
    id_categoria: int = Form(...),
    maneja_stock: bool = Form(False),
    cantidad_stock: int = Form(0),
    imagen: UploadFile = File(None), 
):
    # 1. Validar categoría
    categoria = session.get(modelos.Categoria, id_categoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # 2. Procesar la imagen
    url_imagen_final = None
    if imagen:
        nombre_archivo_unico = f"{uuid.uuid4()}_{imagen.filename}"
        ruta_guardado = f"static_images/{nombre_archivo_unico}"
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        url_imagen_final = f"static_images/{nombre_archivo_unico}"

    # 3. Crear el objeto Producto
    nuevo_producto = modelos.Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        esta_disponible=esta_disponible,
        id_categoria=id_categoria,
        maneja_stock=maneja_stock,
        cantidad_stock=cantidad_stock,
        url_imagen=url_imagen_final
    )

    session.add(nuevo_producto)
    session.commit()
    session.refresh(nuevo_producto)
    session.refresh(nuevo_producto, attribute_names=["categoria"])
    
    return nuevo_producto


@router.get("/", response_model=List[esquemas.ProductoLecturaConCategoria])
def obtener_todos_productos(session: SessionDep):
    statement = (
        select(modelos.Producto)
        .options(joinedload(modelos.Producto.categoria))
    )
    productos = session.exec(statement).all()
    return productos


@router.get("/{id_producto}", response_model=esquemas.ProductoLecturaConCategoria)
def obtener_producto_por_id(id_producto: int, session: SessionDep):
    statement = (
        select(modelos.Producto)
        .options(joinedload(modelos.Producto.categoria))
        .where(modelos.Producto.id_producto == id_producto)
    )
    producto = session.exec(statement).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


@router.patch("/{producto_id}", response_model=esquemas.ProductoLecturaConCategoria)
def actualizar_producto(
    producto_id: int, 
    session: SessionDep,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio: Optional[Decimal] = Form(None),
    esta_disponible: Optional[bool] = Form(None),
    id_categoria: Optional[int] = Form(None),
    maneja_stock: Optional[bool] = Form(None),
    cantidad_stock: Optional[int] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    # 1. Buscar el producto base
    db_producto = session.get(modelos.Producto, producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # 2. Validación silenciosa de Categoría
    if id_categoria is not None and id_categoria > 0:
        categoria = session.get(modelos.Categoria, id_categoria)
        if categoria:
            db_producto.id_categoria = id_categoria
        else:
            # En lugar de lanzar error 404, imprimimos en consola para que sepas qué ID falla
            print(f"ADVERTENCIA: El ID de categoría {id_categoria} no existe. Se ignoró este campo.")

    # 3. Procesar Imagen
    if imagen and imagen.filename:
        nombre_archivo_unico = f"{uuid.uuid4()}_{imagen.filename}"
        ruta_guardado = f"static_images/{nombre_archivo_unico}"
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        db_producto.url_imagen = f"static_images/{nombre_archivo_unico}"

    # 4. Actualizar campos de texto/número
    if nombre is not None: db_producto.nombre = nombre
    if descripcion is not None: db_producto.descripcion = descripcion
    if precio is not None: db_producto.precio = precio
    if esta_disponible is not None: db_producto.esta_disponible = esta_disponible
    if maneja_stock is not None: db_producto.maneja_stock = maneja_stock
    if cantidad_stock is not None: db_producto.cantidad_stock = cantidad_stock
    
    session.add(db_producto)
    session.commit()
    session.refresh(db_producto)
    session.refresh(db_producto, attribute_names=["categoria"])
    
    return db_producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, session: SessionDep):
    producto = session.get(modelos.Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    
    session.delete(producto)
    session.commit()
    return
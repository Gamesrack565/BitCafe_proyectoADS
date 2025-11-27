#BITCAFE
#VERSION 1.2
#By: Angel A. Higuera

#Librerías y módulos
import uuid
import os
import shutil
from decimal import Decimal
from typing import List

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

    # Ya no usamos "producto_in: esquemas.ProductoCreacion" como Body JSON.
    # Ahora definimos los campos uno por uno como Formulario:
    nombre: str = Form(...),
    descripcion: str = Form(None),
    precio: Decimal = Form(...),
    esta_disponible: bool = Form(True),
    id_categoria: int = Form(...),
    maneja_stock: bool = Form(False),
    cantidad_stock: int = Form(0),
    # AQUÍ RECIBIMOS EL ARCHIVO
    imagen: UploadFile = File(None), 
    
):
    # 1. Validar categoría
    categoria = session.get(modelos.Categoria, id_categoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # 2. Procesar la imagen (Si el usuario subió una)
    url_imagen_final = None
    
    if imagen:
        # Generamos un nombre único para que no se sobreescriban fotos con el mismo nombre
        # Ej: "cafe.jpg" se convierte en "a3b1-42c1-cafe.jpg"
        nombre_archivo_unico = f"{uuid.uuid4()}_{imagen.filename}"
        ruta_guardado = f"static_images/{nombre_archivo_unico}"
        
        # Guardamos el archivo físico en la carpeta
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
            
        # Creamos la URL que guardaremos en la BD
        # Esta URL apunta al "mount" que hicimos en main.py
        url_imagen_final = f"imagenes/{nombre_archivo_unico}"

    # 3. Crear el objeto Producto
    nuevo_producto = modelos.Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        esta_disponible=esta_disponible,
        id_categoria=id_categoria,
        maneja_stock=maneja_stock,
        cantidad_stock=cantidad_stock,
        url_imagen=url_imagen_final # <--- AQUÍ GUARDAMOS LA RUTA
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

        #QUITAR EL COMENTARIO CUANDO YA ESTE LA VERSION FINAL
        #Filtro (comentado) para mostrar solo productos disponibles.
        #.where(modelos.Producto.esta_disponible == True)
    )
    #Ejecuta la consulta y obtiene todos los resultados como una lista.
    productos = session.exec(statement).all()
    #Devuelve la lista de productos (con sus categorias anidadas).
    return productos


@router.get("/{id_producto}", response_model=esquemas.ProductoLecturaConCategoria)
def obtener_producto_por_id(id_producto: int, session: SessionDep):
    statement = (
        select(modelos.Producto)
        .options(joinedload(modelos.Producto.categoria))
        .where(modelos.Producto.id_producto == id_producto)
    )
    #Ejecuta la consulta y obtiene el primer resultado (o None).
    producto = session.exec(statement).first()
    
    #Si no se encontro un producto con ese ID.
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    #Devuelve el producto encontrado.
    return producto



@router.patch("/{producto_id}", response_model=esquemas.ProductoLecturaConCategoria)
def actualizar_producto(producto_id: int, producto_data: esquemas.ProductoActualizacion, session: SessionDep):
    #Busca el producto en la BD usando su clave primaria (ID).
    db_producto = session.get(modelos.Producto, producto_id)
    #Si el producto no se encuentra.
    if not db_producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    
    #VERIFICACION DE LA CATEGORIA SI EXISTE
    if producto_data.id_categoria:
        categoria = session.get(modelos.Categoria, producto_data.id_categoria)
        #Si la nueva categoria no existe.
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    #Convierte los datos de entrada a un diccionario, excluyendo campos no enviados (unset).
    update_data = producto_data.model_dump(exclude_unset=True)
    #Itera sobre los datos enviados (ej. 'nombre', 'precio').
    for key, value in update_data.items():
        #Actualiza el campo ('key') en el objeto de la BD con el nuevo valor ('value').
        setattr(db_producto, key, value)
    
    #Anade el objeto modificado a la sesion.
    session.add(db_producto)
    session.commit()
    
    #Refresca el objeto desde la BD.
    session.refresh(db_producto)
    session.refresh(db_producto, attribute_names=["categoria"])
    
    #Devuelve el producto actualizado.
    return db_producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, session: SessionDep):
    # 1. Buscar el producto
    producto = session.get(modelos.Producto, producto_id)
    
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    
    # 2. Validar si está en carritos o pedidos (Opcional pero recomendado)
    # Si intentas borrar algo que ya se vendió, SQL lanzará error si no tienes 'cascade' configurado.
    # Por ahora, confiamos en la eliminación simple:
    
    session.delete(producto)
    session.commit()
    return
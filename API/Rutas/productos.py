#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerías y módulos
#Importa las clases de FastAPI: APIRouter, HTTPException, status.
from fastapi import APIRouter, HTTPException, status
#Importa 'joinedload' para optimizar consultas cargando relaciones (JOINs).
from sqlalchemy.orm import joinedload
#Importa la funcion 'select' de SQLModel para crear consultas.
from sqlmodel import select
#Importa el tipo 'List' para las definiciones de modelos de respuesta.
from typing import List
#Importa la dependencia 'SessionDep' para la sesion de BD.
from Servicios.base_Datos import SessionDep
#Importa el modulo de modelos de la BD (tablas).
from Modelos import modelos
#Importa el modulo de esquemas (Pydantic).
from Esquemas import esquemas

#Crea una nueva instancia de APIRouter, definiendo el prefijo y la etiqueta.
router = APIRouter(prefix="/productos", tags=["Productos"])



@router.post("/", 
             response_model=esquemas.ProductoLecturaConCategoria,
             status_code=status.HTTP_201_CREATED)
def crear_producto(producto_in: esquemas.ProductoCreacion, session: SessionDep):
    #Comprueba si se proporciono un 'id_categoria' en la solicitud.
    if producto_in.id_categoria:
        #Busca la categoria en la BD usando el ID proporcionado.
        categoria = session.get(modelos.Categoria, producto_in.id_categoria)
        #Si no se encuentra la categoria.
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        

    db_producto = modelos.Producto.model_validate(producto_in)
    session.add(db_producto)
    session.commit()
    session.refresh(db_producto)
    session.refresh(db_producto, attribute_names=["categoria"])
    return db_producto


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
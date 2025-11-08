#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerías y modulos
#Importa las clases de FastAPI: APIRouter, HTTPException, status y Depends.
from fastapi import APIRouter, HTTPException, status#, Depends
#Importa la funcion 'select' de SQLModel para crear consultas.
from sqlmodel import select
#Importa el tipo 'List' para definir listas en los modelos de respuesta.
from typing import List
#Importa la dependencia 'SessionDep' para la sesion de BD.
from Servicios.base_Datos import SessionDep
#Importa el modulo de modelos de la BD (tablas).
from Modelos import modelos
#Importa el modulo de esquemas (Pydantic).
from Esquemas import esquemas

#Crea una nueva instancia de APIRouter.
router = APIRouter(prefix="/categoria", tags=["Categorías"])


"""
Rutas para gestionar las categorías de productos en BitCafe.
Permite crear, consultar, actualizar y eliminar categorías, 
asegurando la integridad referencial con los productos asociados.
"""


@router.post("/", response_model=esquemas.CategoriaLectura, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria_in: esquemas.CategoriaCreacion, session: SessionDep):
    #Crea una consulta para buscar si ya existe una categoria con ese nombre.
    statement = select(modelos.Categoria).where(modelos.Categoria.nombre == categoria_in.nombre)
    #Ejecuta la consulta y obtiene el primer resultado.
    db_categoria_existente = session.exec(statement).first()

    #Si se encontro una categoria con ese nombre.
    if db_categoria_existente:
        #Lanza un error 400 (Bad Request) indicando que el nombre ya existe.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la categoria ya existe")

    #Convierte el esquema de entrada (Pydantic) al modelo de BD (SQLModel).
    db_categoria = modelos.Categoria(**categoria_in.model_dump())
    #Anade el nuevo objeto de categoria a la sesion.
    session.add(db_categoria)
    #Confirma (guarda) la transaccion en la BD.
    session.commit()
    #Refresca el objeto para obtener el ID asignado por la BD.
    session.refresh(db_categoria)
    #Devuelve la categoria recien creada.
    return db_categoria


@router.get("/", response_model=List[esquemas.CategoriaLectura])
def obtener_todas_categorias(session: SessionDep):
    #Crea una consulta para seleccionar todos los registros de la tabla Categoria.
    statement = select(modelos.Categoria)
    #Ejecuta la consulta y obtiene todos los resultados como una lista.
    categorias = session.exec(statement).all()
    #Devuelve la lista de categorias.
    return categorias


@router.get("/{categoria_id}", response_model=esquemas.CategoriaLectura)
def obtener_categoria_by_id(categoria_id: int, session: SessionDep):
    #Busca la categoria en la BD usando su clave primaria (ID).
    categoria = session.get(modelos.Categoria, categoria_id)
    #Si la categoria no se encontro (es None).
    if not categoria:
        #Lanza un error 404 (Not Found).
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    #Devuelve la categoria encontrada.
    return categoria


@router.patch("/{categoria_id}", response_model=esquemas.CategoriaLectura)
def actualizar_categoria(categoria_id: int, categoria_data: esquemas.CategoriaActualizacion, session: SessionDep):
    #Busca la categoria que se va a actualizar.
    db_categoria = session.get(modelos.Categoria, categoria_id)
    #Si no se encuentra, lanza un error 404.
    if not db_categoria:
        #Lanza el error 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    
    #Convierte los datos de entrada a un diccionario, excluyendo campos no enviados (unset).
    update_data =categoria_data.model_dump(exclude_unset=True)

    #Si el cliente esta intentando actualizar el 'nombre'.
    if "nombre" in update_data:
        #Crea una consulta para ver si el *nuevo* nombre ya esta en uso por *otra* categoria.
        statement = select(modelos.Categoria).where(modelos.Categoria.nombre == update_data["nombre"])
        #Ejecuta la consulta.
        categoria_existente = session.exec(statement).first()
        #Si se encontro otra categoria con ese nombre.
        if categoria_existente and categoria_existente.id_categoria != categoria_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la categoría ya existe")

    #Itera sobre los datos enviados (ej. 'nombre', 'descripcion').
    for key, value in update_data.items():
        #Actualiza el campo ('key') en el objeto de la BD con el nuevo valor ('value').
        setattr(db_categoria, key, value)
    
    #Anade el objeto modificado a la sesion.
    session.add(db_categoria)
    #Guarda los cambios en la BD.
    session.commit()
    #Refresca el objeto desde la BD.
    session.refresh(db_categoria)
    #Devuelve la categoria actualizada.
    return db_categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, session: SessionDep):
    #Busca la categoria que se va a eliminar.
    db_categoria = session.get(modelos.Categoria, categoria_id)
    #Si no se encuentra, lanza un error 404.
    if not db_categoria:
        #Lanza el error 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    
    #Comprueba si la relacion 'productos' de la categoria no esta vacia (si tiene productos asociados).
    if db_categoria.productos:
        #Si hay productos, lanza un error 400 para evitar la eliminacion (integridad referencial).
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar la categoría porque hay productos asociados a ella")
    
    #Marca la categoria para ser eliminada.
    session.delete(db_categoria)
    #Ejecuta la eliminacion en la BD.
    session.commit()
    #Devuelve la respuesta 204 (No Content) por defecto.
    return
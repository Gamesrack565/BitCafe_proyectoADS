#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerías y módulos
#Importa las clases necesarias de FastAPI (APIRouter, HTTPException, etc.).
from fastapi import APIRouter, HTTPException, status, Depends
#Importa la función 'select' de SQLModel para construir consultas.
from sqlmodel import select
#Importa 'joinedload' para optimizar consultas cargando relaciones (JOINs).
from sqlalchemy.orm import joinedload
#Importa el tipo 'List' para las definiciones de modelos.
#from typing import List
#Importa la dependencia de sesión de la base de datos ('SessionDep').
from Servicios.base_Datos import SessionDep
#Importa la función 'get_current_user' para proteger los endpoints.
from Servicios.seguridad import get_current_user
#Importa los modelos de la base de datos (tablas).
from Modelos import modelos
#Importa los esquemas Pydantic/SQLModel (para entrada/salida de API).
from Esquemas import esquemas

#Crea una instancia de APIRouter.
#Para evitar repetir el prefijo, lo definimos aquí.
router = APIRouter(
    prefix="/carrito",
    tags=["Carrito (Protegido)"]
)



"""
Obtiene el carrito completo del usuario autenticado actualmente.
Carga todos los items y la información de los productos.
"""

@router.get("/", response_model=esquemas.CarritoLectura)
def dame_mi_carrito(
    #Inyecta la dependencia de la sesión de la base de datos.
    session: SessionDep, 
    #Inyecta la dependencia del usuario actual, protegiendo la ruta.
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #Usamos joinedload para cargar el carrito, sus items, y 
    #los productos de esos items, todo en una sola consulta eficiente.
    #Inicia la construcción de una consulta compleja.
    statement = (
        #Indica que queremos seleccionar un objeto Carrito.
        select(modelos.Carrito)
        #Añade un filtro WHERE para encontrar el carrito del usuario autenticado.
        .where(modelos.Carrito.id_usuario == current_user.id_usuario)
        #Define las opciones de carga (JOINs) para la consulta.
        .options(
            #Carga la relación items (los CarritoItem) del carrito.
            joinedload(modelos.Carrito.items)
            #Anida una carga: por cada item, carga su producto.
            .joinedload(modelos.CarritoItem.producto)
            #Anida otra carga: por cada producto, carga su categoria.
            .joinedload(modelos.Producto.categoria)
        )
    )
    
    #Ejecuta la consulta en la sesión y obtiene el primer resultado (o None).
    carrito = session.exec(statement).first()
    
    #Comprueba si no se encontró un carrito para este usuario.
    if not carrito:
        # Esto no debería pasar si el registro de usuario funciona bien,
        # pero es una buena comprobación.
        #Lanza un error 404 (No Encontrado) si no hay carrito.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")
        
    #Devuelve el objeto 'carrito' completo, con 'items', 'producto' y 'categoria' cargados.
    return carrito


"""
Añade un producto al carrito del usuario actual.
Si el producto ya existe en el carrito, actualiza su cantidad.
"""

@router.post("/items", response_model=esquemas.CarritoLectura)
def anadir_producto_al_carrito(
    item_in: esquemas.CarritoItemCrear,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #1. Obtenemos el carrito del usuario
    #Accede al carrito del usuario (que ya está cargado gracias a la relación en el modelo Usuario).
    carrito = current_user.carrito
    #Si, por alguna razón, el usuario no tiene carrito.
    if not carrito:
         #Lanza un error 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

    #2. Verificamos que el producto exista y esté disponible
    #Busca el producto en la BD usando el ID proporcionado en 'item_in'.
    producto = session.get(modelos.Producto, item_in.id_producto)
    #Si el producto no existe en la BD.
    if not producto:
        #Lanza un error 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    #Si el producto existe pero no está marcado como disponible.
    if not producto.esta_disponible:
        #Lanza un error 400 (Mala Petición).
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El producto no está disponible")
        
    #3. Verificamos si este producto YA ESTÁ en el carrito
    #Inicia una consulta para buscar en la tabla 'CarritoItem'.
    statement = (
        select(modelos.CarritoItem)
        #Filtra por el ID del carrito del usuario.
        .where(modelos.CarritoItem.id_carrito == carrito.id_carrito)
        #Y filtra por el ID del producto que se está intentando añadir.
        .where(modelos.CarritoItem.id_producto == item_in.id_producto)
    )
    #Ejecuta la consulta y obtiene el primer resultado.
    item_existente = session.exec(statement).first()
    
    #Si se encontró un 'CarritoItem' (el producto ya estaba en el carrito).
    if item_existente:
        #Si ya existe, actualizamos la cantidad
        #Suma la cantidad nueva a la cantidad que ya existía.
        item_existente.cantidad += item_in.cantidad
        #Si se enviaron notas nuevas en la solicitud.
        if item_in.notas:
            #Actualiza las notas del item existente (sobrescribe las anteriores).
            item_existente.notas = item_in.notas
        #Añade el item modificado a la sesión.
        session.add(item_existente)
    #Si 'item_existente' es None (el producto no estaba en el carrito).
    else:
        #Si no existe, creamos un nuevo CarritoItem
        #Crea una nueva instancia del modelo 'CarritoItem'.
        nuevo_item = modelos.CarritoItem(
            id_carrito=carrito.id_carrito,
            id_producto=item_in.id_producto,
            cantidad=item_in.cantidad,
            notas=item_in.notas
        )
        #Añade el nuevo item a la sesión.
        session.add(nuevo_item)
        
    #Guarda los cambios (ya sea la actualización o la creación) en la base de datos.
    session.commit()
    
    #Devolvemos el carrito completo actualizado
    return dame_mi_carrito(session, current_user)


"""
Actualiza la cantidad o notas de un item específico en el carrito.
"""

@router.patch("/items/{item_id}", response_model=esquemas.CarritoItemLectura)
def actualizar_item_carrito(
    item_id: int,
    item_update: esquemas.CarritoItemActualizar,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #1. Obtenemos el item
    #Busca el CarritoItem específico por su clave primaria.
    db_item = session.get(modelos.CarritoItem, item_id)
    #Si no se encuentra ese CarritoItem en la BD.
    if not db_item:
        #Lanza un error 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item del carrito no encontrado")
        
    #2. COMPROBACIÓN DE SEGURIDAD
    #Verificamos que el item pertenezca al carrito del usuario actual.
    #Compara el id_carrito del item con el id_carrito del usuario que hace la petición.
    if db_item.id_carrito != current_user.carrito.id_carrito:
        #Si no coinciden, lanza un error 403 (Prohibido), el usuario no puede modificar items de otros carritos.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acción no permitida")
        
    #3. Actualizamos los datos
    #Convierte los datos de entrada a un diccionario, excluyendo campos no enviados (unset).
    update_data = item_update.model_dump(exclude_unset=True)
    #Si el diccionario está vacío (el cliente envió un JSON vacío {}).
    if not update_data:
        #Lanza un error 400 (Mala Petición).
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay datos para actualizar")

    #Itera sobre los datos enviados (ej. "cantidad", "notas").
    for key, value in update_data.items():
        #Actualiza el campo (key) en el objeto de la BD (db_item) con el nuevo 'value'.
        setattr(db_item, key, value)
        
    #Añade el objeto modificado a la sesión.
    session.add(db_item)
    #Guarda los cambios en la BD.
    session.commit()
    #Refresca el objeto desde la BD para confirmar los cambios.
    session.refresh(db_item)
    
    #Devuelve el 'CarritoItem' ya actualizado.
    return db_item



"""
Elimina un item del carrito.
"""

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_carrito_item(
    item_id: int,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #1. Obtenemos el item
    #Busca el CarritoItem por su ID.
    db_item = session.get(modelos.CarritoItem, item_id)
    #Si el item no se encuentra,
    if not db_item:
        #Termina
        return
        
    #2. COMPROBACI0N DE SEGURIDAD
    #Verifica que el item pertenezca al carrito del usuario actual.
    if db_item.id_carrito != current_user.carrito.id_carrito:
        #Si no, lanza un error 403 (Prohibido).
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acción no permitida")
        
    #3. Eliminamos
    #Marca el objeto db_item para ser eliminado de la BD.
    session.delete(db_item)
    #Ejecuta la eliminación en la BD.
    session.commit()
    return
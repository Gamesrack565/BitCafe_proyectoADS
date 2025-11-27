#BITCAFE
#VERSION 1.2
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

    cantidad_a_agregar = item_in.cantidad
    
    cantidad_actual_en_carrito = item_existente.cantidad if item_existente else 0
    cantidad_total_deseada = cantidad_actual_en_carrito + cantidad_a_agregar

    # Si el producto maneja stock Y la cantidad deseada supera lo que hay
    if producto.maneja_stock and cantidad_total_deseada > producto.cantidad_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Stock insuficiente. Solo quedan {producto.cantidad_stock} unidades y quieres llevar {cantidad_total_deseada}."
        )
    # ---------------------------------------

    if item_existente:
        item_existente.cantidad += item_in.cantidad
        if item_in.notas:
            item_existente.notas = item_in.notas
        session.add(item_existente)
    else:
        nuevo_item = modelos.CarritoItem(
            id_carrito=carrito.id_carrito,
            id_producto=item_in.id_producto,
            cantidad=item_in.cantidad,
            notas=item_in.notas
        )
        session.add(nuevo_item)
        
    session.commit()
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
    # 1. Obtenemos el item
    db_item = session.get(modelos.CarritoItem, item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item del carrito no encontrado")
        
    # 2. Seguridad
    if db_item.id_carrito != current_user.carrito.id_carrito:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acción no permitida")
        
    # 3. Actualizamos
    update_data = item_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay datos para actualizar")

    #--- VALIDACIÓN DE STOCK EN PATCH (NUEVO) ---
    #Si el usuario está intentando actualizar la cantidad
    if "cantidad" in update_data:
        nueva_cantidad = update_data["cantidad"]
        #Obtenemos el producto original para ver su stock
        producto = db_item.producto #Ya debería estar cargado por la relación, o lo buscamos
        if not producto:
             producto = session.get(modelos.Producto, db_item.id_producto)

        if producto.maneja_stock and nueva_cantidad > producto.cantidad_stock:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Stock insuficiente. No puedes actualizar a {nueva_cantidad} unidades porque solo hay {producto.cantidad_stock}."
            )
    # --------------------------------------------

    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    
    return db_item


"""
Elimina un item del carrito.
"""

# --- CORRECCIÓN: ALERTA AL ELIMINAR ---
# Cambiamos el status 204 (No Content) por 200 (OK) para poder devolver un JSON
@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
def remover_carrito_item(
    item_id: int,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    db_item = session.get(modelos.CarritoItem, item_id)
    if not db_item:
        # Si no existe, retornamos mensaje igual para no dar error feo
        return {"mensaje": "El item no existía o ya fue eliminado"}
        
    if db_item.id_carrito != current_user.carrito.id_carrito:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acción no permitida")
        
    session.delete(db_item)
    session.commit()
    
    # Devolvemos un mensaje JSON
    return {"mensaje": "Producto eliminado del carrito correctamente"}
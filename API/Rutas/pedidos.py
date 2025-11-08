#BITCAFE
#VERSION 1.0
#By: Angel A. Higuera

#Librerías y módulos
#Importa las clases de FastAPI: APIRouter, HTTPException, status y Depends.
from fastapi import APIRouter, HTTPException, status, Depends
#Importa la funcion 'select' de SQLModel para crear consultas.
from sqlmodel import select
#Importa 'joinedload' para optimizar consultas cargando relaciones (JOINs).
from sqlalchemy.orm import joinedload
#Importa el tipo 'List' para las definiciones de modelos.
from typing import List#, Optional
#Importa 'uuid' para generar identificadores unicos (para los numeros de orden).
import uuid
#Importa la dependencia de sesión de la base de datos ('SessionDep').
from Servicios.base_Datos import SessionDep
#Importa la función 'get_current_user' para proteger los endpoints.
from Servicios.seguridad import get_current_user
#Importa las enumeraciones de EstadoPedido y UserRole.
from Servicios.numeraciones import EstadoPedido, UserRole 
#Importa los modelos de la base de datos (tablas).
from Modelos import modelos
#Importa los esquemas Pydantic/SQLModel (para entrada/salida de API).
from Esquemas import esquemas

#Crea una instancia de APIRouter, definiendo que todas las rutas comienzan con /pedidos.
router = APIRouter(prefix="/pedidos", tags=["Pedidos (Protegido)"])



"""
Crea un nuevo pedido a partir del carrito del usuario autenticado.
Calcula el total, transfiere los items y vacía el carrito.
"""

@router.post("/from-cart", response_model=esquemas.PedidoLectura)
def crear_nuevo_pedido_carrito(
    pedido_in: esquemas.PedidoCrearDesdeCarrito,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):

    #1. Cargar el carrito completo del usuario (con items y productos)
    cart_statement = (
        #Selecciona el modelo Carrito.
        select(modelos.Carrito)
        #Filtra por el ID del usuario autenticado.
        .where(modelos.Carrito.id_usuario == current_user.id_usuario)
        #Define las opciones de carga (JOINs) para eficiencia.
        .options(
            #Carga la relacion items
            joinedload(modelos.Carrito.items)
            .joinedload(modelos.CarritoItem.producto)
        )
    )
    #Ejecuta la consulta y obtiene el primer resultado.
    cart = session.exec(cart_statement).first()
    
    #2. Validar el carrito
    #Comprueba si el carrito no existe o si la lista de items del carrito esta vacia.
    if not cart or not cart.items:
        #Lanza un error 400 (Mala Peticion) si el carrito esta vacio.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El carrito está vacío"
        )
        
    #Inicializa el total del pedido en 0.
    total_calculado = 0
    #Crea una lista vacia para guardar los nuevos 'PedidoItem'.
    items_para_db = []
    
    #3. Procesar cada item del carrito
    for item in cart.items:
        #Verifica si el producto asociado al item (cargado por el JOIN) no existe.
        if not item.producto:
            #Lanza un error 404.
            raise HTTPException(status_code=404, detail=f"Producto con id {item.id_producto} no encontrado. No se puede completar el pedido.")
        
        # (Logica de stock - aun por revisar
        # if item.producto.maneja_stock and item.producto.cantidad_stock < item.cantidad:
        #     raise HTTPException(status_code=400, detail=f"Stock insuficiente para {item.producto.nombre}")
        
        #Calcula el precio total de este item, usando el precio de la BD.
        precio_item = item.producto.precio * item.cantidad
        #Suma el precio de este item al total general del pedido.
        total_calculado += precio_item
        
        #Crea una nueva instancia del modelo 'PedidoItem' (la tabla de la BD).
        nuevo_item_pedido = modelos.PedidoItem(
            #Id_pedido se asignará automáticamente por la relación
            id_producto=item.id_producto,
            #Asigna la cantidad desde el item del carrito.
            cantidad=item.cantidad,
            #Guarda el precio unitario *en el momento de la compra*.
            precio_unitario_compra=item.producto.precio,
            #Asigna las notas desde el item del carrito.
            notas=item.notas
        )
        #Añade el 'PedidoItem' recien creado a la lista temporal.
        items_para_db.append(nuevo_item_pedido)
        
        # (Descontar - stock - aun por revisar
        # if item.producto.maneja_stock:
        #     item.producto.cantidad_stock -= item.cantidad
        #     session.add(item.producto)

    #4. Generar número de orden único
    num_orden_nuevo = f"BITCAFE-{str(uuid.uuid4())[:8].upper()}"

    #5. Crear el Pedido principal
    nuevo_pedido = modelos.Pedido(
        id_usuario=current_user.id_usuario,
        num_orden=num_orden_nuevo,
        #Asigna el total calculado del pedido.
        total_pedido=total_calculado,
        #Asigna el metodo de pago enviado por el cliente.
        metodo_pago=pedido_in.metodo_pago,
        # 'estado_pedido' y 'estado_pago' usan sus defaults ('pendiente')
        items=items_para_db
    )
    
    #6. Vaciar el carrito (eliminando los CarritoItems)
    for item in cart.items:
        session.delete(item)

    #7. Guardar todo en una transacción
    session.add(nuevo_pedido)
    #Confirma la transaccion (Crea el Pedido, crea los PedidoItem, borra los CarritoItem).
    session.commit()
    
    # 8. Refrescar para obtener el objeto completo
    session.refresh(nuevo_pedido)
    session.refresh(nuevo_pedido, attribute_names=["items"])
    
    return nuevo_pedido


"""
Obtiene el historial de pedidos del usuario autenticado.
"""

@router.get("/me", response_model=List[esquemas.PedidoLectura])
def mi_pedidos(
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):

    #Inicia la construccion de una consulta.
    statement = (
        #Selecciona los 'Pedido'.
        select(modelos.Pedido)
        #Filtra para obtener solo los pedidos del usuario autenticado.
        .where(modelos.Pedido.id_usuario == current_user.id_usuario)
        #Ordena los resultados por fecha de creacion descendente (los mas nuevos primero).
        .order_by(modelos.Pedido.fecha_creacion.desc())
        #Define las opciones de carga (JOINs) para eficiencia.
        .options(
            #Carga la relacion item
            joinedload(modelos.Pedido.items)
            .joinedload(modelos.PedidoItem.producto)
        )
    )
    #Ejecuta la consulta, aplica 'unique()' (por los JOINs) y obtiene todos los resultados.
    pedidos = session.exec(statement).unique().all()
    #Devuelve la lista de pedidos encontrados.
    return pedidos


"""
Ruta para el cajero/staff.
Obtiene todos los pedidos que están 'pendiente' o 'preparacion'.
"""

@router.get("/pendientes", response_model=List[esquemas.PedidoLectura])
def ordenes_pendientes(
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #VALIDCACIÓN DE ROL
    #Comprueba si el rol del usuario NO es STAFF o ADMIN.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        #Lanza un error 403 (Prohibido) si no tiene el rol adecuado.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para realizar esta acción"
        )

    #Define la lista de estados que se consideran "activos" o "pendientes".
    estados_activos = [EstadoPedido.PENDIENTE, EstadoPedido.PREPARACION]

    
    #Inicia la construccion de una consulta.
    statement = (
        #Selecciona los 'Pedido'.
        select(modelos.Pedido)
        #Filtra donde el 'estado_pedido' este EN la lista 'estados_activos'.
        .where(modelos.Pedido.estado_pedido.in_(estados_activos))
        #Ordena por fecha de creacion ascendente (los mas antiguos primero, FIFO).
        .order_by(modelos.Pedido.fecha_creacion.asc())
        #Define las opciones de carga (JOINs).
        .options(
            joinedload(modelos.Pedido.items)
            .joinedload(modelos.PedidoItem.producto)
        )
    )
    #Ejecuta la consulta, aplica 'unique()' y obtiene todos los resultados.
    pedidos = session.exec(statement).unique().all()
    #Devuelve la lista de pedidos pendientes.
    return pedidos


"""
Ruta para el cajero/staff.
Actualiza el estado de un pedido (ej. 'pendiente' -> 'preparacion').
"""
    
@router.patch("/{pedido_id}/status", response_model=esquemas.PedidoLectura)
def actualizar_ordenes_estado(
    pedido_id: int,
    status_update: esquemas.PedidoActualizar,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):

    #VALIDACIÓN DE ROL
    #Comprueba si el rol del usuario NO es STAFF o ADMIN.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        #Lanza un error 403 (Prohibido).
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para realizar esta acción"
        )
    
    #Busca el pedido en la BD por su clave primaria.
    db_pedido = session.get(modelos.Pedido, pedido_id)
    #Si el pedido no se encuentra.
    if not db_pedido:
        #Lanza un error 404 (No Encontrado).
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    #Convierte los datos de entrada a un diccionario, excluyendo campos no enviados.
    update_data = status_update.model_dump(exclude_unset=True)
    #Si no se enviaron datos para actualizar.
    if not update_data:
        #Lanza un error 400 (Mala Peticion).
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        
    #Itera sobre los datos enviados (ej. 'estado_pedido', 'estado_pago').
    for key, value in update_data.items():
        #Actualiza el campo ('key') en el objeto 'db_pedido' con el nuevo 'value'.
        setattr(db_pedido, key, value)
        
    #Añade el objeto modificado a la sesion.
    session.add(db_pedido)
    session.commit()
    session.refresh(db_pedido)
    
    #Devuelve el pedido ya actualizado.
    return db_pedido
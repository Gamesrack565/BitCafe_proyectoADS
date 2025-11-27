#BITCAFE
#VERSION 2.3 DIVIDIDO PARA AHORA TENER CAJA Y CLIENTE
#By: Angel A. Higuera

#Librerías y modulos
#Importa las clases y funciones principales de FastAPI.
from fastapi import APIRouter, HTTPException, status, Depends
#Importa la funcion 'select' de SQLModel para consultas.
from sqlmodel import select
#Importa 'joinedload' de SQLAlchemy para cargar relaciones (Eager Loading).
from sqlalchemy.orm import joinedload
#Importa clases para manejo de fechas y horas.
from datetime import datetime, timedelta 
#Importa el tipo List para tipado estatico.
from typing import List
#Importa la libreria uuid para generar identificadores unicos.
import uuid

#Importa la dependencia 'SessionDep' para la sesion de BD.
from Servicios.base_Datos import SessionDep
#Importa la funcion de seguridad para obtener el usuario actual.
from Servicios.seguridad import get_current_user
#Importa las enumeraciones de estados y roles.
from Servicios.numeraciones import EstadoPedido, UserRole 
#Importa los modelos de la base de datos.
from Modelos import modelos
#Importa los esquemas de datos (Pydantic).
from Esquemas import esquemas

#Crea una instancia del enrutador para pedidos de cliente.
router = APIRouter(prefix="/pedidos", tags=["Pedidos (Cliente)"])

# --- FUNCIÓN AUXILIAR ---
def actualizar_automaticamente_pendientes(session: SessionDep):
    """
    Revisa si los pedidos pendientes ya cumplieron su tiempo de espera
    y los pasa a PREPARACIÓN automáticamente.
    """
    #Crea una consulta para buscar pedidos en estado 'PENDIENTE'.
    statement = select(modelos.Pedido).where(modelos.Pedido.estado_pedido == EstadoPedido.PENDIENTE)
    #Ejecuta la consulta y obtiene todos los pedidos pendientes.
    pedidos_pendientes = session.exec(statement).all()
    
    #Obtiene la fecha y hora actual.
    ahora = datetime.now()
    #Bandera para saber si hubo cambios y hacer commit al final.
    cambios_realizados = False
    
    #Itera sobre cada pedido pendiente encontrado.
    for pedido in pedidos_pendientes:
        #Calcula el tiempo transcurrido desde la creacion del pedido.
        tiempo_transcurrido = ahora - pedido.fecha_creacion
        #Si han pasado mas de 120 segundos (2 minutos de buffer).
        if tiempo_transcurrido.total_seconds() > 120:
            #Cambia el estado del pedido a 'PREPARACION'.
            pedido.estado_pedido = EstadoPedido.PREPARACION
            #Anade el pedido modificado a la sesion.
            session.add(pedido)
            #Marca que se realizo un cambio.
            cambios_realizados = True
            
    #Si se realizaron cambios en la base de datos.
    if cambios_realizados:
        #Confirma los cambios (commit).
        session.commit()


# --- CREAR PEDIDO DESDE CARRITO (APP CLIENTE) ---
@router.post("/from-cart", response_model=esquemas.PedidoLectura)
def crear_nuevo_pedido_carrito(
    pedido_in: esquemas.PedidoCrearDesdeCarrito,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    # 0. --- VALIDACIÓN DE TIENDA ABIERTA ---
    #Busca la configuracion del sistema correspondiente al estado de la tienda.
    config_tienda = session.get(modelos.ConfiguracionSistema, "ESTADO_TIENDA")
    
    #Si existe la configuracion y el valor es "CERRADO".
    if config_tienda and config_tienda.valor == "CERRADO":
        #Lanza una excepcion 503 indicando que el servicio no esta disponible.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, # Código 503: Servicio no disponible
            detail="Lo sentimos, la tienda está cerrada en este momento. No se reciben pedidos."
        )
    # ---------------------------------------

    # 1. Cargar carrito
    #Construye la consulta para obtener el carrito del usuario actual con sus relaciones.
    cart_statement = (
        select(modelos.Carrito)
        .where(modelos.Carrito.id_usuario == current_user.id_usuario)
        .options(
            joinedload(modelos.Carrito.items)
            .joinedload(modelos.CarritoItem.producto)
            .joinedload(modelos.Producto.categoria)
        )
    )
    #Ejecuta la consulta y obtiene el primer resultado (el carrito).
    cart = session.exec(cart_statement).first()
    
    #Si no existe el carrito o no tiene items dentro.
    if not cart or not cart.items:
        #Lanza error 400 indicando carrito vacio.
        raise HTTPException(status_code=400, detail="El carrito está vacío")
        
    #Inicializa el total calculado del pedido.
    total_calculado = 0
    #Lista para almacenar los items que se guardaran en la tabla de pedidos.
    items_para_db = []
    #Bandera para identificar si el pedido contiene productos de preparacion lenta.
    tiene_comida_lenta = False
    
    #Itera sobre cada item presente en el carrito.
    for item in cart.items:
        #Si el item no tiene un producto asociado (error de integridad).
        if not item.producto:
            #Lanza error 404.
            raise HTTPException(status_code=404, detail=f"Producto {item.id_producto} no encontrado.")
        
        #Si el producto maneja stock y la cantidad disponible es menor a la solicitada.
        if item.producto.maneja_stock and item.producto.cantidad_stock < item.cantidad:
             #Lanza error 400 por stock insuficiente.
             raise HTTPException(status_code=400, detail=f"Stock insuficiente para {item.producto.nombre}")
        
        #Si el producto tiene una categoria asignada.
        if item.producto.categoria:
            #Normaliza el nombre de la categoria (minusculas y guiones bajos).
            nombre_cat = item.producto.categoria.nombre.lower().replace(" ", "_")
            #Si la categoria es comida preparada.
            if "comida_preparada" in nombre_cat:
                #Marca el pedido como lento.
                tiene_comida_lenta = True

        #Calcula el precio total por linea (precio unitario * cantidad).
        precio_item = item.producto.precio * item.cantidad
        #Suma al total general del pedido.
        total_calculado += precio_item
        
        #Crea el objeto PedidoItem basado en el item del carrito.
        nuevo_item_pedido = modelos.PedidoItem(
            id_producto=item.id_producto,
            cantidad=item.cantidad,
            precio_unitario_compra=item.producto.precio,
            notas=item.notas
        )
        #Agrega el nuevo item a la lista para guardar.
        items_para_db.append(nuevo_item_pedido)
        
        #Si el producto maneja inventario.
        if item.producto.maneja_stock:
             #Resta la cantidad comprada del stock.
             item.producto.cantidad_stock -= item.cantidad
             #Anade el producto actualizado a la sesion.
             session.add(item.producto)

    #Genera un nuevo numero de orden unico.
    num_orden_nuevo = f"BITCAFE-{str(uuid.uuid4())[:8].upper()}"

    #Define el tiempo buffer base.
    tiempo_buffer = 2 
    #Define el tiempo de preparacion dependiendo del tipo de comida.
    tiempo_preparacion = 15 if tiene_comida_lenta else 5
    #Calcula el tiempo total en minutos.
    tiempo_total_minutos = tiempo_buffer + tiempo_preparacion
    
    #Obtiene la hora actual.
    ahora = datetime.now()
    #Calcula la fecha y hora estimada de entrega.
    tiempo_entrega_estimado = ahora + timedelta(minutes=tiempo_total_minutos)

    #Crea la instancia del nuevo Pedido.
    nuevo_pedido = modelos.Pedido(
        id_usuario=current_user.id_usuario,
        num_orden=num_orden_nuevo,
        total_pedido=total_calculado,
        metodo_pago=pedido_in.metodo_pago,
        items=items_para_db,
        tiempo_estimado=tiempo_entrega_estimado 
    )
    
    #Itera sobre los items del carrito para eliminarlos (vaciar carrito).
    for item in cart.items:
        #Marca el item para eliminar.
        session.delete(item)

    #Anade el nuevo pedido a la sesion.
    session.add(nuevo_pedido)
    #Confirma la transaccion (guarda pedido, actualiza stock, vacia carrito).
    session.commit()
    #Refresca el objeto pedido para obtener IDs generados.
    session.refresh(nuevo_pedido)
    #Refresca la relacion items para devolver la respuesta completa.
    session.refresh(nuevo_pedido, attribute_names=["items"])
    
    #Devuelve el pedido creado.
    return nuevo_pedido


# --- VER MIS PEDIDOS (CLIENTE) ---
@router.get("/me", response_model=List[esquemas.PedidoLectura])
def mi_pedidos(
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #Llama a la funcion auxiliar para actualizar estados pendientes antes de consultar.
    actualizar_automaticamente_pendientes(session)
    
    #Construye la consulta de pedidos del usuario actual.
    statement = (
        select(modelos.Pedido)
        .where(modelos.Pedido.id_usuario == current_user.id_usuario)
        .order_by(modelos.Pedido.fecha_creacion.desc())
        .options(
            joinedload(modelos.Pedido.items)
            .joinedload(modelos.PedidoItem.producto)
        )
    )
    #Ejecuta la consulta y obtiene resultados unicos.
    pedidos_db = session.exec(statement).unique().all()
    
    #Lista para procesar la respuesta.
    pedidos_respuesta = []
    #Obtiene hora actual.
    ahora = datetime.now()

    #Itera sobre los pedidos obtenidos de la BD.
    for p in pedidos_db:
        #Valida y convierte el modelo SQL a esquema Pydantic.
        p_esquema = esquemas.PedidoLectura.model_validate(p)
        
        #Lista de estados que se consideran finalizados.
        estados_finalizados = [EstadoPedido.LISTO, EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO]
        
        #Si el pedido aun no ha finalizado y tiene un tiempo estimado.
        if p.estado_pedido not in estados_finalizados and p.tiempo_estimado:
            #Si la hora actual supera la estimada (hay retraso).
            if ahora > p.tiempo_estimado:
                #Calcula la diferencia de tiempo.
                retraso = ahora - p.tiempo_estimado
                #Convierte a minutos enteros (minimo 1).
                minutos_retraso = max(1, int(retraso.total_seconds() / 60))
                #Asigna mensaje de retraso al esquema de respuesta.
                p_esquema.mensaje_retraso = f"Tu pedido está retrasado por {minutos_retraso} min. Estamos agilizando tu orden."
        
        #Agrega el esquema procesado a la lista final.
        pedidos_respuesta.append(p_esquema)

    #Devuelve la lista de pedidos.
    return pedidos_respuesta
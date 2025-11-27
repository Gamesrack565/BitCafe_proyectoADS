#BITCAFE
#VERSION 2.3 DIVIDIDO PARA AHORA TENER CAJA Y CLIENTE
#By: Angel A. Higuera

#Librerías y modulos
#Importa las clases y funciones principales de FastAPI.
from fastapi import APIRouter, HTTPException, status, Depends
#Importa la clase StreamingResponse para enviar archivos (PDF) como respuesta.
from fastapi.responses import StreamingResponse 
#Importa la funcion 'select' de SQLModel para consultas.
from sqlmodel import select
#Importa 'joinedload' de SQLAlchemy para cargar relaciones (Eager Loading).
from sqlalchemy.orm import joinedload
#Importa funciones de agregacion SQL (count, sum).
from sqlalchemy import func
#Importa clases para manejo de fechas y horas.
from datetime import date, datetime, time, timedelta 
#Importa el tipo List para tipado estatico.
from typing import List
#Importa la libreria uuid para generar identificadores unicos.
import uuid
#Importa el modulo io para manejar flujos de bytes en memoria.
import io
#Importa el objeto canvas de ReportLab para generar PDFs.
from reportlab.pdfgen import canvas
#Importa unidades de medida para el PDF.
from reportlab.lib.units import mm

#Importa la dependencia 'SessionDep' para la sesion de BD.
from Servicios.base_Datos import SessionDep
#Importa la funcion de seguridad para obtener el usuario actual.
from Servicios.seguridad import get_current_user
#Importa las enumeraciones de estados y roles.
from Servicios.numeraciones import EstadoPedido, EstadoPago, MetodoPago, UserRole 
#Importa los modelos de la base de datos.
from Modelos import modelos
#Importa los esquemas de datos (Pydantic).
from Esquemas import esquemas

#Crea una instancia del enrutador para pedidos de caja.
router = APIRouter(prefix="/pedidos_caja", tags=["Pedidos (Caja/Staff)"])

def actualizar_automaticamente_pendientes(session: SessionDep):
    #Crea una consulta para buscar pedidos en estado 'PENDIENTE'.
    statement = select(modelos.Pedido).where(modelos.Pedido.estado_pedido == EstadoPedido.PENDIENTE)
    #Ejecuta la consulta y obtiene todos los pedidos pendientes.
    pedidos_pendientes = session.exec(statement).all()
    #Obtiene la fecha y hora actual.
    ahora = datetime.now()
    #Bandera para saber si hubo cambios y hacer commit al final.
    cambios = False
    
    #Itera sobre cada pedido pendiente.
    for pedido in pedidos_pendientes:
        #Calcula el tiempo transcurrido desde la creacion del pedido.
        tiempo = ahora - pedido.fecha_creacion
        #Si han pasado mas de 120 segundos (2 minutos).
        if tiempo.total_seconds() > 120:
            #Cambia el estado del pedido a 'PREPARACION'.
            pedido.estado_pedido = EstadoPedido.PREPARACION
            #Anade el pedido modificado a la sesion.
            session.add(pedido)
            #Marca que hubo cambios.
            cambios = True
            
    #Si hubo algun cambio en los pedidos.
    if cambios: 
        #Guarda los cambios en la base de datos.
        session.commit()


# --- CREACIÓN MANUAL (CAJA/POS) ---
@router.post("/manual", response_model=esquemas.PedidoLectura)
def crear_pedido_manual(
    pedido_in: esquemas.PedidoManualCrear,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    """
    Crea un pedido desde Caja recibiendo lista de items, total y método de pago.
    """
    #Verifica si el usuario tiene rol de STAFF o ADMIN.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        #Lanza error 403 si no tiene permisos.
        raise HTTPException(status_code=403, detail="No tienes permisos.")

    #Verifica si la lista de items esta vacia.
    if not pedido_in.items:
        #Lanza error 400 si no hay productos.
        raise HTTPException(status_code=400, detail="El pedido no tiene productos.")

    #Inicializa el total calculado del pedido.
    total_calculado = 0
    #Lista para almacenar los objetos PedidoItem antes de guardar.
    items_para_db = []
    #Bandera para detectar productos que tardan mas en prepararse.
    tiene_comida_lenta = False
    
    #Itera sobre cada item recibido en el esquema de entrada.
    for item_in in pedido_in.items:
        #Busca el producto en la BD por su ID.
        producto = session.get(modelos.Producto, item_in.id_producto)
        
        #Si el producto no existe.
        if not producto:
            #Lanza error 404.
            raise HTTPException(status_code=404, detail=f"Producto ID {item_in.id_producto} no encontrado")
        
        #Si el producto esta marcado como no disponible.
        if not producto.esta_disponible:
            #Lanza error 400.
            raise HTTPException(status_code=400, detail=f"Producto '{producto.nombre}' no disponible.")

        #Si el producto maneja inventario y el stock es menor a la cantidad solicitada.
        if producto.maneja_stock and producto.cantidad_stock < item_in.cantidad:
            #Lanza error 400 por falta de stock.
            raise HTTPException(status_code=400, detail=f"Stock insuficiente '{producto.nombre}'.")

        #Si el producto tiene una categoria asignada.
        if producto.id_categoria:
             #Obtiene la categoria del producto.
             categoria = session.get(modelos.Categoria, producto.id_categoria)
             #Si la categoria existe y contiene "comida_preparada" en su nombre (normalizado).
             if categoria and "comida_preparada" in categoria.nombre.lower().replace(" ", "_"):
                 #Marca que el pedido incluye comida lenta.
                 tiene_comida_lenta = True

        #Calcula el subtotal del item (precio x cantidad).
        precio_item = producto.precio * item_in.cantidad
        #Suma el subtotal al total del pedido.
        total_calculado += precio_item

        #Crea una instancia de PedidoItem para la BD.
        nuevo_item = modelos.PedidoItem(
            id_producto=item_in.id_producto,
            cantidad=item_in.cantidad,
            precio_unitario_compra=producto.precio,
            notas=item_in.notas
        )
        #Agrega el item a la lista temporal.
        items_para_db.append(nuevo_item)

        #Si el producto maneja stock.
        if producto.maneja_stock:
            #Resta la cantidad vendida del stock actual.
            producto.cantidad_stock -= item_in.cantidad
            #Agrega el producto actualizado a la sesion.
            session.add(producto)

    #Define un tiempo buffer base en minutos.
    tiempo_buffer = 2 
    #Define el tiempo de preparacion segun si hay comida lenta o no.
    tiempo_preparacion = 15 if tiene_comida_lenta else 5
    #Calcula el tiempo total estimado.
    tiempo_total = tiempo_buffer + tiempo_preparacion
    #Calcula la fecha/hora exacta de entrega estimada.
    tiempo_entrega = datetime.now() + timedelta(minutes=tiempo_total)
    
    #Genera un numero de orden unico.
    num_orden = f"BITCAFE-{str(uuid.uuid4())[:8].upper()}"
    
    # --- LÓGICA DE PAGO INTELIGENTE ---
    # Si es Efectivo -> Nace PAGADO (Caja cierra la venta ahí mismo)
    # Si es Transferencia -> Nace PENDIENTE (Para validar después)
    
    #Evalua el metodo de pago seleccionado.
    if pedido_in.metodo_pago == MetodoPago.EFECTIVO:
        #Establece estado PAGADO inmediatamente.
        estado_pago_inicial = EstadoPago.PAGADO
    else:
        #Establece estado PENDIENTE para verificacion posterior.
        estado_pago_inicial = EstadoPago.PENDIENTE

    #Crea la instancia del Pedido principal.
    nuevo_pedido = modelos.Pedido(
        id_usuario=current_user.id_usuario,
        num_orden=num_orden,
        total_pedido=total_calculado,
        metodo_pago=pedido_in.metodo_pago,
        estado_pago=estado_pago_inicial, # <--- Asignamos el estado condicional
        items=items_para_db,
        tiempo_estimado=tiempo_entrega,
        referencia_pago=pedido_in.referencia_pago # <--- Guardamos la referencia
    )

    #Anade el nuevo pedido a la sesion.
    session.add(nuevo_pedido)
    #Confirma la transaccion y guarda todo en la BD.
    session.commit()
    #Refresca el objeto pedido para obtener su ID.
    session.refresh(nuevo_pedido)
    #Refresca explicitamente la relacion 'items' para la respuesta.
    session.refresh(nuevo_pedido, attribute_names=["items"])

    #Devuelve el objeto pedido creado.
    return nuevo_pedido


# --- TICKET PDF ---
@router.get("/{pedido_id}/ticket")
def descargar_ticket_pdf(
    pedido_id: int,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    #Construye la consulta cargando relaciones de items y productos.
    statement = (
        select(modelos.Pedido)
        .where(modelos.Pedido.id_pedido == pedido_id)
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto))
    )
    #Ejecuta la consulta para obtener el pedido.
    pedido = session.exec(statement).first()
    
    #Si no encuentra el pedido.
    if not pedido:
        #Lanza error 404.
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    #Verifica permisos: debe ser STAFF/ADMIN o el dueno del pedido.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN] and pedido.id_usuario != current_user.id_usuario:
        #Lanza error 403.
        raise HTTPException(status_code=403, detail="No autorizado")

    #Crea un buffer en memoria para el archivo PDF.
    buffer = io.BytesIO()
    #Define el ancho del papel (formato ticket termico).
    ancho_papel = 80 * mm
    #Define el alto del papel (fijo por simplicidad, idealmente dinamico).
    alto_papel = 200 * mm 
    #Inicializa el objeto canvas de ReportLab.
    c = canvas.Canvas(buffer, pagesize=(ancho_papel, alto_papel))
    #Establece la posicion inicial Y (vertical).
    y = alto_papel - 10 * mm 
    #Establece el margen izquierdo X.
    x = 5 * mm
    
    #Configura la fuente para el titulo.
    c.setFont("Helvetica-Bold", 12)
    #Escribe el nombre del negocio.
    c.drawString(x + 20*mm, y, "BITCAFE")
    #Mueve el cursor hacia abajo.
    y -= 5 * mm
    #Configura fuente normal pequena.
    c.setFont("Helvetica", 8)
    #Escribe el folio.
    c.drawString(x, y, f"Folio: {pedido.num_orden}")
    #Mueve el cursor.
    y -= 4 * mm
    #Escribe la fecha formateada.
    c.drawString(x, y, f"Fecha: {pedido.fecha_creacion.strftime('%Y-%m-%d %H:%M')}")
    #Mueve el cursor.
    y -= 4 * mm
    #Escribe el ID del usuario que atendio.
    c.drawString(x, y, f"Atendido por ID: {pedido.id_usuario}")
    #Mueve el cursor.
    y -= 4 * mm
    #Escribe el metodo de pago.
    c.drawString(x, y, f"Pago: {pedido.metodo_pago.upper()}")
    #Mueve el cursor para la linea divisora.
    y -= 6 * mm
    #Dibuja una linea horizontal.
    c.line(x, y, ancho_papel - 5*mm, y)
    #Mueve el cursor.
    y -= 4 * mm
    
    #Configura fuente negrita para encabezados de tabla.
    c.setFont("Helvetica-Bold", 7)
    #Escribe encabezados de columnas.
    c.drawString(x, y, "CANT")
    c.drawString(x + 10*mm, y, "PRODUCTO")
    c.drawString(x + 55*mm, y, "TOTAL")
    #Mueve el cursor.
    y -= 4 * mm
    
    #Configura fuente normal para items.
    c.setFont("Helvetica", 7)
    #Itera sobre los items del pedido.
    for item in pedido.items:
        #Trunca el nombre del producto si es muy largo.
        nombre_prod = item.producto.nombre[:20] 
        #Calcula el costo total de la linea.
        costo_item = item.cantidad * item.precio_unitario_compra
        #Escribe cantidad.
        c.drawString(x, y, str(item.cantidad))
        #Escribe nombre del producto.
        c.drawString(x + 10*mm, y, nombre_prod)
        #Escribe costo formateado.
        c.drawString(x + 55*mm, y, f"${costo_item:.2f}")
        #Mueve el cursor para la siguiente linea.
        y -= 4 * mm
        #Si el item tiene notas.
        if item.notas:
             #Cambia fuente a cursiva.
             c.setFont("Helvetica-Oblique", 6)
             #Escribe la nota debajo del producto.
             c.drawString(x + 10*mm, y, f"({item.notas})")
             #Restaura la fuente normal.
             c.setFont("Helvetica", 7)
             #Mueve el cursor extra.
             y -= 4 * mm

    #Mueve el cursor antes de la linea final.
    y -= 2 * mm
    #Dibuja linea final.
    c.line(x, y, ancho_papel - 5*mm, y)
    #Mueve el cursor.
    y -= 5 * mm
    #Configura fuente grande para el total.
    c.setFont("Helvetica-Bold", 10)
    #Escribe el total del pedido.
    c.drawString(x + 30*mm, y, f"TOTAL: ${pedido.total_pedido:.2f}")
    #Mueve el cursor al pie.
    y -= 10 * mm
    #Configura fuente normal.
    c.setFont("Helvetica", 8)
    #Escribe mensaje de agradecimiento.
    c.drawString(x + 15*mm, y, "¡Gracias por su compra!")
    #Guarda y finaliza el dibujo en el canvas.
    c.save()
    #Mueve el puntero del buffer al inicio.
    buffer.seek(0)
    #Define el nombre del archivo.
    filename = f"ticket_{pedido.num_orden}.pdf"
    
    #Retorna el archivo PDF como flujo de datos para descarga.
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/pendientes", response_model=List[esquemas.PedidoLectura])
def ordenes_pendientes(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    #Verifica que el usuario sea STAFF o ADMIN.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        #Lanza error 403 si no tiene permiso.
        raise HTTPException(status_code=403, detail="No autorizado")
    
    #Ejecuta la funcion auxiliar para actualizar estados automaticos.
    actualizar_automaticamente_pendientes(session)
    
    #Define los estados que se consideran pendientes de atencion.
    estados = [EstadoPedido.PENDIENTE, EstadoPedido.PREPARACION]
    
    #Construye la consulta filtrando por estados y ordenando por fecha.
    statement = (select(modelos.Pedido).where(modelos.Pedido.estado_pedido.in_(estados))
        .order_by(modelos.Pedido.fecha_creacion.asc())
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto)))
        
    #Ejecuta la consulta y obtiene resultados unicos.
    pedidos_db = session.exec(statement).unique().all()
    #Lista para almacenar los pedidos procesados para respuesta.
    pedidos_resp = []
    #Obtiene hora actual.
    ahora = datetime.now()
    
    #Itera sobre los pedidos obtenidos.
    for p in pedidos_db:
        #Valida y convierte el modelo SQL a esquema Pydantic.
        p_esq = esquemas.PedidoLectura.model_validate(p)
        #Si el pedido tiene tiempo estimado y ya paso la hora.
        if p.tiempo_estimado and ahora > p.tiempo_estimado:
             #Calcula el tiempo de retraso.
             retraso = ahora - p.tiempo_estimado
             #Calcula los minutos de retraso (minimo 1).
             minutos = max(1, int(retraso.total_seconds() / 60))
             #Agrega un mensaje de alerta al esquema.
             p_esq.mensaje_retraso = f"¡RETRASO DE {minutos} MIN!"
        #Agrega el esquema a la lista de respuesta.
        pedidos_resp.append(p_esq)
        
    #Devuelve la lista de pedidos pendientes.
    return pedidos_resp

@router.get("/listos", response_model=List[esquemas.PedidoLectura])
def ordenes_listas(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    #Verifica que el usuario sea STAFF o ADMIN.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        #Lanza error 403.
        raise HTTPException(status_code=403, detail="No autorizado")
    
    #Consulta pedidos con estado 'LISTO'.
    statement = (select(modelos.Pedido).where(modelos.Pedido.estado_pedido == EstadoPedido.LISTO)
        .order_by(modelos.Pedido.fecha_creacion.asc())
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto)))
        
    #Devuelve la lista de pedidos listos para entrega.
    return session.exec(statement).unique().all()

@router.patch("/{pedido_id}/status", response_model=esquemas.PedidoLectura)
def actualizar_ordenes_estado(pedido_id: int, status_update: esquemas.PedidoActualizar, session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    #Verifica permisos de usuario.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        #Lanza error 403.
        raise HTTPException(status_code=403, detail="No autorizado")
    
    #Busca el pedido por ID.
    db_pedido = session.get(modelos.Pedido, pedido_id)
    #Si no existe el pedido.
    if not db_pedido: 
        #Lanza error 404.
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    #Convierte los datos de actualizacion a diccionario excluyendo nulos.
    update_data = status_update.model_dump(exclude_unset=True)
    #Si no se enviaron datos validos.
    if not update_data: 
        #Lanza error 400.
        raise HTTPException(status_code=400, detail="No hay datos")
    
    #Itera y actualiza los atributos del pedido.
    for key, value in update_data.items(): setattr(db_pedido, key, value)
    
    #Anade a sesion, confirma y refresca.
    session.add(db_pedido); session.commit(); session.refresh(db_pedido)
    #Devuelve el pedido actualizado.
    return db_pedido

@router.get("/historial", response_model=List[esquemas.PedidoLectura])
def historial_pedidos_completados(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    #Verifica permisos.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        #Lanza error 403.
        raise HTTPException(status_code=403, detail="No autorizado")
    
    #Define estados finales de pedido.
    estados = [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO]
    #Consulta historial ordenado por fecha descendente (mas reciente primero).
    statement = (select(modelos.Pedido).where(modelos.Pedido.estado_pedido.in_(estados))
        .order_by(modelos.Pedido.fecha_creacion.desc())
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto)))
        
    #Devuelve el historial.
    return session.exec(statement).unique().all()

@router.get("/resumen-dia", response_model=dict)
def resumen_ventas_dia(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    #Verifica permisos.
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        #Lanza error 403.
        raise HTTPException(status_code=403, detail="No autorizado")
    
    #Define el inicio del dia actual (00:00).
    hoy_inicio = datetime.combine(date.today(), time.min)
    #Define el fin del dia actual (23:59).
    hoy_fin = datetime.combine(date.today(), time.max)
    
    #Cuenta el total de pedidos generados hoy.
    total_gen = session.exec(select(func.count(modelos.Pedido.id_pedido)).where(modelos.Pedido.fecha_creacion >= hoy_inicio).where(modelos.Pedido.fecha_creacion <= hoy_fin)).one()
    #Cuenta el total de pedidos que ya estan pagados hoy.
    pagados_count = session.exec(select(func.count(modelos.Pedido.id_pedido)).where(modelos.Pedido.fecha_creacion >= hoy_inicio).where(modelos.Pedido.fecha_creacion <= hoy_fin).where(modelos.Pedido.estado_pago == EstadoPago.PAGADO)).one()
    #Suma el monto total de ventas pagadas hoy (si es None pone 0).
    dinero_total = session.exec(select(func.sum(modelos.Pedido.total_pedido)).where(modelos.Pedido.fecha_creacion >= hoy_inicio).where(modelos.Pedido.fecha_creacion <= hoy_fin).where(modelos.Pedido.estado_pago == EstadoPago.PAGADO)).one() or 0
    
    #Devuelve el diccionario con el resumen.
    return {"pedidos_generados_hoy": total_gen, "pedidos_pagados_hoy": pagados_count, "total_ventas_hoy": dinero_total}
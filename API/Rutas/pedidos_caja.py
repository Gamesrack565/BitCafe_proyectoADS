# BITCAFE
# VERSION 2.4 - DISEÑO DE TICKET ACTUALIZADO
# By: Angel A. Higuera / Gemini

#Librerías y modulos
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse 
from sqlmodel import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import date, datetime, time, timedelta 
from typing import List
import uuid
import io
from reportlab.pdfgen import canvas
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
    statement = select(modelos.Pedido).where(modelos.Pedido.estado_pedido == EstadoPedido.PENDIENTE)
    pedidos_pendientes = session.exec(statement).all()
    ahora = datetime.now()
    cambios = False
    
    for pedido in pedidos_pendientes:
        tiempo = ahora - pedido.fecha_creacion
        if tiempo.total_seconds() > 120:
            pedido.estado_pedido = EstadoPedido.PREPARACION
            session.add(pedido)
            cambios = True
            
    if cambios: 
        session.commit()

# --- CREACIÓN MANUAL (CAJA/POS) ---
@router.post("/manual", response_model=esquemas.PedidoLectura)
def crear_pedido_manual(
    pedido_in: esquemas.PedidoManualCrear,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="No tienes permisos.")

    if not pedido_in.items:
        raise HTTPException(status_code=400, detail="El pedido no tiene productos.")

    total_calculado = 0
    items_para_db = []
    tiene_comida_lenta = False
    
    for item_in in pedido_in.items:
        producto = session.get(modelos.Producto, item_in.id_producto)
        
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto ID {item_in.id_producto} no encontrado")
        
        if not producto.esta_disponible:
            raise HTTPException(status_code=400, detail=f"Producto '{producto.nombre}' no disponible.")

        if producto.maneja_stock and producto.cantidad_stock < item_in.cantidad:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente '{producto.nombre}'.")

        if producto.id_categoria:
             categoria = session.get(modelos.Categoria, producto.id_categoria)
             if categoria and "comida_preparada" in categoria.nombre.lower().replace(" ", "_"):
                 tiene_comida_lenta = True

        precio_item = producto.precio * item_in.cantidad
        total_calculado += precio_item

        nuevo_item = modelos.PedidoItem(
            id_producto=item_in.id_producto,
            cantidad=item_in.cantidad,
            precio_unitario_compra=producto.precio,
            notas=item_in.notas
        )
        items_para_db.append(nuevo_item)

        if producto.maneja_stock:
            producto.cantidad_stock -= item_in.cantidad
            session.add(producto)

    tiempo_buffer = 2 
    tiempo_preparacion = 15 if tiene_comida_lenta else 5
    tiempo_total = tiempo_buffer + tiempo_preparacion
    tiempo_entrega = datetime.now() + timedelta(minutes=tiempo_total)
    
    # Mantenemos el formato BITCAFE-XXXX
    num_orden = f"BITCAFE-{str(uuid.uuid4())[:8].upper()}"
    
    if pedido_in.metodo_pago == MetodoPago.EFECTIVO:
        estado_pago_inicial = EstadoPago.PAGADO
    else:
        estado_pago_inicial = EstadoPago.PENDIENTE

    nuevo_pedido = modelos.Pedido(
        id_usuario=current_user.id_usuario,
        num_orden=num_orden,
        total_pedido=total_calculado,
        metodo_pago=pedido_in.metodo_pago,
        estado_pago=estado_pago_inicial, 
        items=items_para_db,
        tiempo_estimado=tiempo_entrega,
        referencia_pago=pedido_in.referencia_pago 
    )

    session.add(nuevo_pedido)
    session.commit()
    session.refresh(nuevo_pedido)
    session.refresh(nuevo_pedido, attribute_names=["items"])

    return nuevo_pedido


# --- TICKET PDF (DISEÑO ACTUALIZADO) ---
@router.get("/{pedido_id}/ticket")
def descargar_ticket_pdf(
    pedido_id: int,
    session: SessionDep,
    current_user: modelos.Usuario = Depends(get_current_user)
):
    raise HTTPException(status_code=500, detail="¡ESTE ES EL ARCHIVO CORRECTO!") 
    statement = (
        select(modelos.Pedido)
        .where(modelos.Pedido.id_pedido == pedido_id)
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto))
    )
    pedido = session.exec(statement).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN] and pedido.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")

    buffer = io.BytesIO()
    ancho_papel = 80 * mm
    alto_papel = 200 * mm # Alto suficiente para varios productos
    c = canvas.Canvas(buffer, pagesize=(ancho_papel, alto_papel))
    
    y = alto_papel - 15 * mm 
    x = 5 * mm
    centro = ancho_papel / 2

    # --- ENCABEZADO CENTRADO ---
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(centro, y, "BITCAFE")
    
    y -= 10 * mm
    c.setFont("Helvetica", 11)
    # Folio formateado como en la imagen
    c.drawString(x, y, f"Folio: {pedido.num_orden}")
    
    y -= 5 * mm
    c.drawString(x, y, f"Fecha: {pedido.fecha_creacion.strftime('%Y-%m-%d %H:%M')}")
    
    y -= 5 * mm
    c.drawString(x, y, f"Cliente ID: {pedido.id_usuario}")
    
    y -= 5 * mm
    # Pago en mayúsculas
    c.drawString(x, y, f"Pago: {pedido.metodo_pago.value.upper()}")
    
    # --- LÍNEA DIVISORIA GRUESA ---
    y -= 6 * mm
    c.setLineWidth(1.2)
    c.line(x, y, ancho_papel - 5*mm, y)
    
    # --- ENCABEZADOS DE TABLA ---
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "CANT")
    c.drawString(x + 15*mm, y, "PRODUCTO")
    c.drawRightString(ancho_papel - 5*mm, y, "TOTAL")
    
    # --- LISTA DE PRODUCTOS ---
    y -= 2 * mm
    c.setFont("Helvetica", 10)
    for item in pedido.items:
        y -= 6 * mm
        # Cantidad
        c.drawString(x, y, str(item.cantidad))
        # Nombre Producto
        c.drawString(x + 15*mm, y, item.producto.nombre[:20])
        # Total por item
        subtotal = item.cantidad * item.precio_unitario_compra
        c.drawRightString(ancho_papel - 5*mm, y, f"${subtotal:.2f}")
        
        # Notas del producto (Cursiva y entre paréntesis justo debajo)
        if item.notas:
            y -= 5 * mm
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(x + 15*mm, y, f"({item.notas})")
            c.setFont("Helvetica", 10)

    # --- LÍNEA FINAL DIVISORIA ---
    y -= 7 * mm
    c.setLineWidth(1.2)
    c.line(x, y, ancho_papel - 5*mm, y)
    
    # --- TOTAL DESTACADO ---
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(ancho_papel - 5*mm, y, f"TOTAL: ${pedido.total_pedido:.2f}")
    
    # --- PIE DE PÁGINA ---
    y -= 15 * mm
    c.setFont("Helvetica", 10)
    c.drawCentredString(centro, y, "¡Gracias por su compra!")
    
    c.save()
    buffer.seek(0)
    filename = f"ticket_{pedido.num_orden}.pdf"
    
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/pendientes", response_model=List[esquemas.PedidoLectura])
def ordenes_pendientes(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        raise HTTPException(status_code=403, detail="No autorizado")
    
    actualizar_automaticamente_pendientes(session)
    estados = [EstadoPedido.PENDIENTE, EstadoPedido.PREPARACION]
    
    statement = (select(modelos.Pedido).where(modelos.Pedido.estado_pedido.in_(estados))
        .order_by(modelos.Pedido.fecha_creacion.asc())
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto)))
        
    pedidos_db = session.exec(statement).unique().all()
    pedidos_resp = []
    ahora = datetime.now()
    
    for p in pedidos_db:
        p_esq = esquemas.PedidoLectura.model_validate(p)
        if p.tiempo_estimado and isinstance(p.tiempo_estimado, datetime) and ahora > p.tiempo_estimado:
             retraso = ahora - p.tiempo_estimado
             minutos = max(1, int(retraso.total_seconds() / 60))
             p_esq.mensaje_retraso = f"¡RETRASO DE {minutos} MIN!"
        pedidos_resp.append(p_esq)
        
    return pedidos_resp

@router.get("/listos", response_model=List[esquemas.PedidoLectura])
def ordenes_listas(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        raise HTTPException(status_code=403, detail="No autorizado")
    
    statement = (select(modelos.Pedido).where(modelos.Pedido.estado_pedido == EstadoPedido.LISTO)
        .order_by(modelos.Pedido.fecha_creacion.asc())
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto)))
        
    return session.exec(statement).unique().all()

@router.patch("/{pedido_id}/status", response_model=esquemas.PedidoLectura)
def actualizar_ordenes_estado(pedido_id: int, status_update: esquemas.PedidoActualizar, session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        raise HTTPException(status_code=403, detail="No autorizado")
    
    db_pedido = session.get(modelos.Pedido, pedido_id)
    if not db_pedido: 
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    update_data = status_update.model_dump(exclude_unset=True)
    if not update_data: 
        raise HTTPException(status_code=400, detail="No hay datos")
    
    for key, value in update_data.items(): setattr(db_pedido, key, value)
    
    session.add(db_pedido); session.commit(); session.refresh(db_pedido)
    return db_pedido

@router.get("/historial", response_model=List[esquemas.PedidoLectura])
def historial_pedidos_completados(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        raise HTTPException(status_code=403, detail="No autorizado")
    
    estados = [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO]
    statement = (select(modelos.Pedido).where(modelos.Pedido.estado_pedido.in_(estados))
        .order_by(modelos.Pedido.fecha_creacion.desc())
        .options(joinedload(modelos.Pedido.items).joinedload(modelos.PedidoItem.producto)))
        
    return session.exec(statement).unique().all()

@router.get("/resumen-dia", response_model=dict)
def resumen_ventas_dia(session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    if current_user.rol not in [UserRole.STAFF, UserRole.ADMIN]: 
        raise HTTPException(status_code=403, detail="No autorizado")
    
    hoy_inicio = datetime.combine(date.today(), time.min)
    hoy_fin = datetime.combine(date.today(), time.max)
    
    total_gen = session.exec(select(func.count(modelos.Pedido.id_pedido)).where(modelos.Pedido.fecha_creacion >= hoy_inicio).where(modelos.Pedido.fecha_creacion <= hoy_fin)).one()
    pagados_count = session.exec(select(func.count(modelos.Pedido.id_pedido)).where(modelos.Pedido.fecha_creacion >= hoy_inicio).where(modelos.Pedido.fecha_creacion <= hoy_fin).where(modelos.Pedido.estado_pago == EstadoPago.PAGADO)).one()
    dinero_total = session.exec(select(func.sum(modelos.Pedido.total_pedido)).where(modelos.Pedido.fecha_creacion >= hoy_inicio).where(modelos.Pedido.fecha_creacion <= hoy_fin).where(modelos.Pedido.estado_pago == EstadoPago.PAGADO)).one() or 0
    
    return {"pedidos_generados_hoy": total_gen, "pedidos_pagados_hoy": pagados_count, "total_ventas_hoy": dinero_total}
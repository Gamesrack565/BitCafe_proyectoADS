#BITCAFE
#VERSION 1.1 
#By: Angel A. Higuera


from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlmodel import select
from Servicios.base_Datos import SessionDep
from Servicios.seguridad import get_current_user
from Servicios.mercado_pago_s import crear_preferencia_de_pago
from Modelos import modelos
from Esquemas import esquemas

router = APIRouter(prefix="/pagos", tags=["Pagos (Mercado Pago)"])

"""
Crea una preferencia de pago en Mercado Pago para un pedido existente.
"""

@router.post("/crear-preferencia/{pedido_id}", response_model=dict)
def crear_pago_pedido(pedido_id: int, session: SessionDep, current_user: modelos.Usuario = Depends(get_current_user)):
    # 1. Busca el pedido
    db_pedido = session.get(modelos.Pedido, pedido_id)
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    # 2. Verifica usuario
    if db_pedido.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")
        
    # 3. Verifica pago previo
    if db_pedido.estado_pago == "pagado":
        raise HTTPException(status_code=400, detail="Este pedido ya fue pagado")

    # 4. Llama al servicio
    respuesta_mp = crear_preferencia_de_pago(db_pedido.model_dump(), pedido_id)
    
    if not respuesta_mp:
        raise HTTPException(status_code=500, detail="Error al crear la preferencia de pago")

    # --- CORRECCIÓN DE SEGURIDAD ---
    # A veces el servicio devuelve el diccionario completo de MP, a veces el string.
    # Aquí nos aseguramos de mandar SOLO LA URL.
    url_final = ""
    
    if isinstance(respuesta_mp, dict):
        # Intentamos obtener init_point (producción) o sandbox_init_point (pruebas)
        url_final = respuesta_mp.get("init_point") or respuesta_mp.get("sandbox_init_point")
    elif isinstance(respuesta_mp, str):
        url_final = respuesta_mp
    
    if not url_final:
        raise HTTPException(status_code=500, detail="No se encontró el link 'init_point' en la respuesta de MP")

    return {"init_point": url_final}



"""
Endpoint PÚBLICO que Mercado Pago usará para notificarte
sobre el estado de un pago.
NO TERMINADO, NI PROBADO.
"""
@router.post("/webhook")
async def recibir_webhook_mercadopago(request: Request, session: SessionDep):

    body = await request.json()
    action = body.get("action")
    
    
    if action == "payment.updated":
        payment_id = body["data"]["id"]
        #(Aquí, usarías el SDK de MP para obtener los detalles de ese pago)
        #resultado_pago = sdk.payment().get(payment_id)
        
        #Obtenemos el ID de nuestro pedido que guardamos
        #external_reference = resultado_pago["response"]["external_reference"]
        #estado = resultado_pago["response"]["status"]
        
        #--- Simulación 
        print(f"Notificación recibida para pago: {payment_id}")
        
        # if estado == "approved":
        #    db_pedido = session.get(modelos.Pedido, int(external_reference))
        #    if db_pedido:
        #        db_pedido.estado_pago = "pagado"
        #        db_pedido.estado_pedido = "preparacion" # O el estado que quieras
        #        session.add(db_pedido)
        #        session.commit()
        #        print(f"Pedido {external_reference} actualizado a PAGADO")

    return {"status": "ok"}
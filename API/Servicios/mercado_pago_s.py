#BITCAFE
#VERSION 0.2
#By: Angel A. Higuera

#AUN NO ESTA TERMINAD Y FUE PROBADO A MEDIAS

#Librerías y módulos
#Importa el SDK DE MERCADO PAGO
import mercadopago
import os

#PASOS:
#1. Crea una cuenta de Vendedor en Mercado Pago.           -LISTO
#2. Ve a "Tu Negocio" -> "Configuración" -> "Credenciales"  -LISTO
#3. Copia tu "Access Token" de PRUEBA (sandbox) aquí.      -LISTO
#¡NUNCA pongas este token directamente en el código, usa variables de entorno! -POR HACER

#GENERADO TEMPORALMENTE PARA PRUEBAS
MP_ACCESS_TOKEN = "APP_USR-4529932902759037-110800-c17d067071e03225afbe11b7371d3173-2974538155"

#Inicializa el SDK de Mercado Pago, autenticandose con el Access Token.
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

"""
Crea una preferencia de pago en Mercado Pago.
"""
def crear_preferencia_de_pago(pedido: dict, pedido_id_interno: int):
    
    #URL de tu API donde Mercado Pago enviará las notificaciones
    #Debe ser una URL pública (https) para que MP pueda verla
    #(Para desarrollo, puedes usar 'ngrok' para exponer tu localhost)
    #Construye la URL de notificacion (webhook) leyendo la URL base desde una variable de entorno.

    url_notificacion = f"https{os.getenv('API_URL')}/pagos/webhook"

    #Crea un diccionario para almacenar todos los datos de la preferencia de pago.
    preferencia_data = {
        #Inicia la lista de items que se van a cobrar.
        "items": [
            {
                #Establece el titulo que el cliente vera (ej. "Pedido #123 en BitCafé").
                "title": f"Pedido #{pedido_id_interno} en BitCafé",
                #Define la cantidad de este item (1, porque es el pedido total).
                "quantity": 1,
                #Establece el precio, convirtiendo el total del pedido a float.
                "unit_price": float(pedido['total_pedido']),
                "currency_id": "MXN"
            }
        ],
        #Define las URLs a las que el cliente sera redirigido despues del pago.
        "back_urls": {

            #CAMBIAR EN VERSION FINAL -----
            
            #URL si el pago es exitoso.
            "success": "https://mi-app.com/pago-exitoso",
            #URL si el pago falla.
            "failure": "https://mi-app.com/pago-fallido",
        },
        #Indica que se debe redirigir al cliente automaticamente solo si el pago es aprobado.
        "auto_return": "approved",
        #Asigna la URL de webhook definida anteriormente para notificaciones del servidor.
        "notification_url": url_notificacion,
        #Asigna el ID de tu pedido interno como referencia externa (crucial para identificar el pago).
        "external_reference": str(pedido_id_interno) 
    }
    
    #Inicia un bloque try-except para manejar posibles errores con la API de Mercado Pago.
    try:
        #Llama al SDK para crear la preferencia de pago en los servidores de MP.
        resultado = sdk.preference().create(preferencia_data)
        #Comprueba si la respuesta de la API indica una creacion exitosa (HTTP 201).
        if resultado["status"] == 201:
            #KOTLIN DEBE ABRIR ESTO:
            #Obtiene la URL de pago (en modo de prueba/sandbox) desde la respuesta.
            url_pago = resultado["response"]["sandbox_init_point"] 
            #Devuelve la URL a la que se debe redirigir al cliente para que pague.
            return url_pago
        else:
            #Imprime la respuesta completa del error para depuracion.
            print(resultado)
            #Devuelve None para indicar que la creacion fallo.
            return None
    #Captura cualquier otra excepcion que ocurra (ej. error de red).
    except Exception as e:
        #Imprime el mensaje de la excepcion.
        print(f"Error creando preferencia: {e}")
        #Devuelve None para indicar que ocurrio un error.
        return None
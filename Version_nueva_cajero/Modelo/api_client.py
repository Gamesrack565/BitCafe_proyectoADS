#BITCAFE
#VERSION 2.0 (Cliente API Optimizado)
#By: Angel A. Higuera

#Librerías y modulos
#Importa la libreria requests para realizar peticiones HTTP.
import requests
#Importa el modulo os para manejo de rutas y archivos del sistema.
import os

class APIClient:
    def __init__(self):
        #Define la URL base donde esta alojada la API (ngrok en este caso).
        self.BASE_URL = "https://acorned-contemningly-drema.ngrok-free.dev" 
        #Inicializa la variable para almacenar el token de autenticacion.
        self.token = None
        
        # --- OPTIMIZACIÓN: SESIÓN PERSISTENTE ---
        #Crea un objeto Session para mantener la conexion TCP abierta y reutilizarla.
        self.session = requests.Session()

    def set_token(self, token):
        """Guarda el token y configura los headers globales de la sesión"""
        #Guarda el token en la instancia.
        self.token = token
        #Actualiza los headers de la sesion para incluir la autorizacion en todas las peticiones futuras.
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })

    # ==========================================
    # LECTURA (GET) - Usamos self.session
    # ==========================================
    def obtener_pedidos_pendientes(self):
        #Inicia bloque de manejo de errores.
        try:
            #Realiza una peticion GET al endpoint de pedidos pendientes.
            response = self.session.get(f"{self.BASE_URL}/pedidos_caja/pendientes")
            #Devuelve el JSON si el estatus es 200, si no devuelve lista vacia.
            return response.json() if response.status_code == 200 else []
        #En caso de error de conexion.
        except: return []

    def obtener_resumen_dia(self):
        #Inicia bloque try.
        try:
            #Peticion GET para obtener el resumen financiero del dia.
            response = self.session.get(f"{self.BASE_URL}/pedidos_caja/resumen-dia")
            #Devuelve el diccionario JSON o vacio.
            return response.json() if response.status_code == 200 else {}
        #Retorna diccionario vacio en error.
        except: return {}
        
    def obtener_pedidos_listos(self):
        #Inicia bloque try.
        try:
            #Peticion GET para obtener pedidos listos para entrega.
            response = self.session.get(f"{self.BASE_URL}/pedidos_caja/listos")
            #Devuelve la lista JSON o vacia.
            return response.json() if response.status_code == 200 else []
        #Retorna lista vacia en error.
        except: return []

    def obtener_productos(self):
        #Inicia bloque try.
        try:
            #Peticion GET para descargar el catalogo completo de productos.
            response = self.session.get(f"{self.BASE_URL}/productos/productos/")
            #Devuelve la lista de productos o vacia.
            return response.json() if response.status_code == 200 else []
        #Retorna lista vacia en error.
        except: return []

    # ==========================================
    # ESCRITURA (POST, PATCH, DELETE)
    # ==========================================
    def login(self, username, password):
        #Inicia bloque try.
        try:
            # Login usa form-data estándar, usamos requests puro o session sin el header json forzado
            #Realiza peticion POST al endpoint de token enviando credenciales.
            response = requests.post(f"{self.BASE_URL}/auth/token", data={
                "username": username, "password": password
            })
            #Si la autenticacion fue exitosa (200 OK).
            if response.status_code == 200:
                #Extrae el token de acceso de la respuesta.
                token = response.json().get("access_token")
                #Configura la sesion con el nuevo token.
                self.set_token(token) 
                #Devuelve el token.
                return token
            #Si fallo el login.
            return None
        #Captura errores generales.
        except Exception as e:
            #Imprime el error.
            print(f"Error Login: {e}")
            #Retorna None.
            return None

    def actualizar_estado_pedido(self, id_pedido, nuevo_estado):
        #Inicia bloque try.
        try:
            #Construye la URL especifica para el status del pedido.
            url = f"{self.BASE_URL}/pedidos_caja/{id_pedido}/status"
            #Realiza peticion PATCH enviando el nuevo estado en JSON.
            response = self.session.patch(url, json={"estado_pedido": nuevo_estado})
            #Devuelve True si el codigo es 200 o 204.
            return response.status_code in [200, 204]
        #Retorna False en error.
        except: return False

    def actualizar_producto(self, producto_id, datos):
        #Inicia bloque try.
        try:
            #Construye la URL del producto.
            url = f"{self.BASE_URL}/productos/productos/{producto_id}"
            #Realiza peticion PATCH con los datos a actualizar.
            response = self.session.patch(url, json=datos)
            #Devuelve True si fue exitoso.
            return response.status_code == 200
        #Retorna False en error.
        except: return False

    def eliminar_producto(self, producto_id):
        #Inicia bloque try.
        try:
            #Construye la URL del producto.
            url = f"{self.BASE_URL}/productos/productos/{producto_id}"
            #Realiza peticion DELETE.
            response = self.session.delete(url)
            #Devuelve True si se elimino correctamente.
            return response.status_code in [200, 204]
        #Retorna False en error.
        except: return False

    def crear_producto(self, datos_dict, ruta_imagen=None):
        """POST con Multipart (Imagen). Requiere manejo especial de headers."""
        #Define la URL para crear productos.
        url = f"{self.BASE_URL}/productos/productos/"
        
        #Prepara el diccionario de datos convirtiendo tipos para asegurar compatibilidad.
        data_payload = {
            "nombre": datos_dict["nombre"],
            "descripcion": datos_dict.get("descripcion", ""),
            "precio": str(datos_dict["precio"]),
            "esta_disponible": str(datos_dict["esta_disponible"]).lower(),
            "id_categoria": int(datos_dict["id_categoria"]),
            "maneja_stock": str(datos_dict["maneja_stock"]).lower(),
            "cantidad_stock": int(datos_dict.get("cantidad_stock", 0))
        }

        # Header solo Auth (requests calculará el multipart boundary)
        #Prepara headers manuales solo con auth (requests pone el Content-Type multipart).
        headers_auth = {"Authorization": f"Bearer {self.token}"}
        #Inicializa la variable de archivo.
        archivo = None
        
        #Inicia bloque try.
        try:
            #Inicializa payload de archivos como None.
            files_payload = None
            #Si se proporciono ruta de imagen y el archivo existe.
            if ruta_imagen and os.path.exists(ruta_imagen):
                #Abre el archivo en modo lectura binaria.
                archivo = open(ruta_imagen, 'rb')
                #Prepara el diccionario para el parametro 'files' de requests.
                files_payload = {'imagen': (os.path.basename(ruta_imagen), archivo, 'image/jpeg')}

            #Realiza peticion POST enviando datos y archivos, usando headers especificos.
            response = requests.post(url, data=data_payload, files=files_payload, headers=headers_auth)
            #Devuelve True si se creo (200 o 201).
            return response.status_code in [200, 201]
        #Captura errores.
        except Exception as e:
            #Imprime error en consola.
            print(f"Error crear: {e}")
            return False
        #Bloque finally para asegurar limpieza de recursos.
        finally:
            #Cierra el archivo si fue abierto.
            if archivo: archivo.close()

    def crear_pedido_manual(self, lista_items, total, metodo_pago, referencia=""):
        """
        Conecta con: POST /pedidos_caja/manual
        Envía el esquema PedidoManualCrear
        """
        #Define la URL para pedidos manuales.
        url = f"{self.BASE_URL}/pedidos_caja/manual"
        
        #Construimos el payload exacto que espera tu esquema de Pydantic.
        payload = {
            "items": lista_items,            # Lista de diccionarios {id_producto, cantidad, notas}
            "total": float(total),           # Decimal en backend, float en JSON
            "metodo_pago": metodo_pago,      # "efectivo" o "transferencia"
            "referencia_pago": referencia    # String opcional
        }
        
        #Inicia bloque try.
        try:
            #Imprime payload para depuracion.
            print(f"Enviando a API: {payload}") 
            #Realiza peticion POST usando la sesion persistente.
            response = self.session.post(url, json=payload)
            
            #Si la respuesta es exitosa.
            if response.status_code in [200, 201]:
                #Confirma en consola.
                print("Caja: Venta registrada correctamente.")
                return True
            #Si la respuesta es error.
            else:
                #Imprime el error devuelto por la API.
                print(f"Error API ({response.status_code}): {response.text}")
                return False
        #Captura errores de conexion.
        except Exception as e:
            #Imprime error.
            print(f"Error de conexión: {e}")
            return False

    def obtener_link_mercadopago(self, pedido_id):
        """
        POST /pagos/crear-preferencia/{id}
        Retorna la URL de pago (init_point)
        """
        #Construye la URL para generar preferencia de pago.
        url = f"{self.BASE_URL}/pagos/crear-preferencia/{pedido_id}"
        #Inicia bloque try.
        try:
            #Realiza peticion POST (sin body, el ID va en URL).
            response = self.session.post(url)
            #Si la respuesta es exitosa.
            if response.status_code == 200:
                #Obtiene el JSON de respuesta.
                datos = response.json()
                #Retorna el link de pago (init_point).
                return datos.get("init_point") 
            #Si hubo error.
            else:
                #Imprime error.
                print(f"Error MP ({response.status_code}): {response.text}")
                return None
        #Captura excepciones.
        except Exception as e:
            #Imprime error de conexion.
            print(f"Error conexión MP: {e}")
            return None

    def confirmar_pago_pedido(self, pedido_id):
        """
        PATCH /pedidos_caja/{id}/status
        Fuerza el estado a PAGADO (usado cuando el cajero confirma visualmente)
        """
        #Construye la URL para actualizar estado.
        url = f"{self.BASE_URL}/pedidos_caja/{pedido_id}/status"
        #Prepara el payload para marcar como pagado.
        payload = {"estado_pago": "pagado"}
        
        #Inicia bloque try.
        try:
            #Realiza peticion PATCH.
            response = self.session.patch(url, json=payload)
            #Devuelve True si fue exitoso.
            return response.status_code == 200
        #En caso de error.
        except:
            return False

    def crear_pedido_manual_retorna_datos(self, lista_items, total, metodo_pago, referencia=""):
        """
        Crea el pedido y RETORNA EL JSON COMPLETO (necesitamos el ID del pedido)
        """
        #Define la URL.
        url = f"{self.BASE_URL}/pedidos_caja/manual"
        
        #Prepara el payload con los datos del pedido.
        payload = {
            "items": lista_items,
            "total": float(total),
            "metodo_pago": metodo_pago,
            "referencia_pago": referencia
        }
        
        #Inicia bloque try.
        try:
            #Realiza peticion POST.
            response = self.session.post(url, json=payload)
            #Si la creacion fue exitosa.
            if response.status_code in [200, 201]:
                #Retorna todo el objeto JSON recibido (incluye el ID generado).
                return response.json() 
            #Si hubo error.
            else:
                #Imprime detalles del error.
                print(f"Error API ({response.status_code}): {response.text}")
                return None
        #Captura errores de conexion.
        except Exception as e:
            #Imprime error.
            print(f"Error conexión: {e}")
            return None

# Instancia global para ser usada en toda la aplicacion.
api = APIClient()
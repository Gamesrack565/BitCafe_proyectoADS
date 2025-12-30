# BITCAFE - VERSION 3.6 (RESTAURACIÓN TOTAL + ESTABILIDAD DE BUSCADOR)
# By: Angel A. Higuera & Gemini Partner

import requests
import os
import io 
from typing import Optional, Dict, Any
from datetime import datetime

class APIClient:
    def __init__(self):
        self.BASE_URL = "http://127.0.0.1:8000"
        self.token = None
        self.session = requests.Session()
        # --- LÓGICA DE BLOQUEO LOCAL ---
        self._tienda_abierta_local = True 

    def set_token(self, token):
        """Guarda el token y configura los headers globales de la sesión"""
        self.token = token
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
        })

    # ==========================================
    # LECTURA (GET) - FUNCIONES DE ESTADO
    # ==========================================
    
    def obtener_estado_tienda(self) -> bool:
        """Consulta el estado manual del switch en el servidor."""
        try:
            url = f"{self.BASE_URL}/configuracion/estado-tienda"
            response = self.session.get(url, timeout=3)
            if response.status_code == 200:
                self._tienda_abierta_local = response.json().get("esta_abierto", True)
            return self._tienda_abierta_local
        except Exception as e:
            print(f"API: Fallo de red al obtener estado, usando local: {e}")
            return self._tienda_abierta_local

    def obtener_productos(self):
        """Obtiene productos y sincroniza campos de imagen y disponibilidad"""
        try:
            response = self.session.get(f"{self.BASE_URL}/productos/productos/", timeout=5)
            if response.status_code == 200:
                productos = response.json()
                for p in productos:
                    if "url_imagen" in p:
                        p["ruta_imagen"] = p["url_imagen"]
                    p["disponible"] = p.get("esta_disponible", True)
                return productos
            return []
        except: return []

    # ==========================================
    # LECTURA DE PEDIDOS (RESUMEN Y LISTAS)
    # ==========================================
    def obtener_pedidos_pendientes(self):
        try:
            response = self.session.get(f"{self.BASE_URL}/pedidos_caja/pendientes")
            return response.json() if response.status_code == 200 else []
        except: return []

    def obtener_resumen_dia(self):
        try:
            response = self.session.get(f"{self.BASE_URL}/pedidos_caja/resumen-dia")
            return response.json() if response.status_code == 200 else {}
        except: return {}
        
    def obtener_pedidos_listos(self):
        try:
            response = self.session.get(f"{self.BASE_URL}/pedidos_caja/listos")
            return response.json() if response.status_code == 200 else []
        except: return []

    # ==========================================
    # ESCRITURA Y CONFIGURACIÓN (PATCH/POST)
    # ==========================================
    
    def actualizar_estado_tienda(self, abierto: bool) -> bool:
        """Actualiza el estado manual en el servidor."""
        self._tienda_abierta_local = abierto
        url = f"{self.BASE_URL}/configuracion/cambiar-estado"
        params = {"nuevo_estado": abierto}
        
        try:
            response = self.session.post(url, params=params, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Error al sincronizar con servidor: {e}")
            return True
        
    def login(self, username, password):
        try:
            response = requests.post(f"{self.BASE_URL}/auth/token", data={
                "username": username, "password": password
            })
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.set_token(token) 
                return token
            return None
        except Exception as e:
            print(f"Error Login: {e}")
            return None

    def actualizar_estado_pedido(self, id_pedido, nuevo_estado):
        try:
            url = f"{self.BASE_URL}/pedidos_caja/{id_pedido}/status"
            response = self.session.patch(url, json={"estado_pedido": nuevo_estado})
            return response.status_code in [200, 204]
        except: return False

    def actualizar_producto(self, producto_id, datos_dict: Dict[str, Any], ruta_imagen: Optional[str] = None) -> Any:
        url = f"{self.BASE_URL}/productos/productos/{producto_id}"
        archivo = None
        payload_para_server = datos_dict.copy()
        
        if "disponible" in payload_para_server:
            payload_para_server["esta_disponible"] = payload_para_server.pop("disponible")

        headers = self.session.headers.copy()
        try:
            if 'Content-Type' in headers: del headers['Content-Type']
            payload_str = {k: ("true" if v is True else "false" if v is False else str(v)) for k, v in payload_para_server.items()}

            if ruta_imagen and os.path.exists(ruta_imagen):
                archivo = open(ruta_imagen, 'rb')
                files = {'imagen': (os.path.basename(ruta_imagen), archivo, 'image/jpeg')}
            else:
                files = {'imagen': ('', io.BytesIO(b""), 'application/octet-stream')}

            response = self.session.patch(url, data=payload_str, files=files, headers=headers, timeout=10)
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204: return True
                resultado = response.json()
                if "url_imagen" in resultado: resultado["ruta_imagen"] = resultado["url_imagen"]
                return resultado
            return None 
        except Exception as e:
            print(f"DEBUG API Actualizar: {e}")
            return None
        finally:
            if archivo: archivo.close()

    def eliminar_producto(self, producto_id):
        try:
            url = f"{self.BASE_URL}/productos/productos/{producto_id}"
            response = self.session.delete(url)
            return response.status_code in [200, 204]
        except: return False
    
    def crear_producto(self, datos_dict: Dict[str, Any], ruta_imagen: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/productos/productos/"
        data_payload = {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in datos_dict.items()}
        headers = self.session.headers.copy()
        if 'Content-Type' in headers: del headers['Content-Type']
        
        archivo = None
        try:
            files_payload = None
            if ruta_imagen and os.path.exists(ruta_imagen):
                archivo = open(ruta_imagen, 'rb')
                files_payload = {'imagen': (os.path.basename(ruta_imagen), archivo, 'image/jpeg')}
            
            response = self.session.post(url, data=data_payload, files=files_payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                resultado = response.json()
                if "url_imagen" in resultado: resultado["ruta_imagen"] = resultado["url_imagen"]
                return resultado
            return {"detail": response.text, "status_code": response.status_code}
        except Exception as e: return {"detail": str(e)}
        finally:
            if archivo: archivo.close()

    def obtener_link_mercadopago(self, pedido_id):
        url = f"{self.BASE_URL}/pagos/crear-preferencia/{pedido_id}"
        try:
            response = self.session.post(url)
            return response.json().get("init_point") if response.status_code == 200 else None
        except: return None

    def crear_pedido_manual_retorna_datos(self, lista_items, total, metodo_pago, referencia=""):
        # Verificación doble para seguridad antes de enviar
        if not self.verificar_horario_operacion():
            return None

        url = f"{self.BASE_URL}/pedidos_caja/manual"
        payload = {
            "items": lista_items, 
            "total": float(total), 
            "metodo_pago": metodo_pago, 
            "referencia_pago": referencia
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=7)
            return response.json() if response.status_code in [200, 201] else None
        except: return None
        
    # ==========================================
    # GESTIÓN DE HORARIOS (SOPORTE JSON LARGO)
    # ==========================================
    def obtener_horarios(self) -> dict:
        """Obtiene horarios con respaldo automático si falla la red."""
        try:
            url = f"{self.BASE_URL}/configuracion/horarios"
            response = self.session.get(url, timeout=3)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error red horarios: {e}")
            
        # RESPALDO: Evita que la app se trabe si no hay internet
        return {
            "Lunes": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
            "Martes": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
            "Miercoles": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
            "Jueves": {"inicio": "09:00", "fin": "18:00", "cerrado": False},
            "Viernes": {"inicio": "09:00", "fin": "18:00", "cerrado": False}
        }

    def guardar_horarios(self, tabla_horarios: dict) -> bool:
        """Envía el JSON de horarios al servidor."""
        try:
            url = f"{self.BASE_URL}/configuracion/horarios"
            # Enviamos como JSON puro
            response = self.session.post(url, json=tabla_horarios, timeout=5)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error al guardar horarios: {e}")
            return False
    
    def verificar_horario_operacion(self) -> bool:
        """Lógica centralizada de validación abierta/cerrado."""
        try:
            tienda_abierta_manual = self.obtener_estado_tienda()
            if not tienda_abierta_manual:
                return False
            
            horarios = self.obtener_horarios()
            ahora = datetime.now()
            
            # Mapeo universal por índice (0=Lunes... 6=Domingo)
            dias_ref = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
            dia_actual = dias_ref[ahora.weekday()]
            
            config = horarios.get(dia_actual)
            # Si el día no está en el JSON o está marcado como cerrado
            if not config or config.get("cerrado"):
                return False
                
            formato = "%H:%M"
            hora_actual = ahora.time()
            hora_inicio = datetime.strptime(config["inicio"].strip(), formato).time()
            hora_fin = datetime.strptime(config["fin"].strip(), formato).time()
            
            return hora_inicio <= hora_actual <= hora_fin
            
        except Exception as e:
            print(f"Error verificación técnica: {e}")
            return True # En caso de error técnico extremo, permitimos la venta

# Instancia global
api = APIClient()
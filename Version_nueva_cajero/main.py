# BITCAFE - MAIN APP 
# VERSION 2.3 - EXE COMPATIBILITY READY
# By: Angel A. Higuera & Gemini Partner

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import Qt

# --- 1. FUNCIÓN DE RUTAS PARA PYINSTALLER ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta para recursos, compatible con el empaquetado .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 2. IMPORTAR VISTAS ---
from Vista.vista_portada import VistaPortada
from Vista.vista_dashboard import VistaDashboard
from Vista.vista_pedido_manual import VistaPedidoManual
from Vista.vista_pedidos import VistaPedidos
from Vista.vista_menu import VistaMenu
from Vista.vista_ajustes import VistaAjustes

# --- 3. IMPORTAR CONTROLADORES ---
from Controlador.controlador_menu import ControladorMenu
from Controlador.controlador_dashboard import ControladorDashboard
from Controlador.controlador_pedidos import ControladorPedidos
from Controlador.controlador_pedido_manual import ControladorPedidoManual
from Controlador.controlador_ajustes import ControladorAjustes

# --- 4. IMPORTAR MODELO (API) ---
try:
    from Modelo.api_client import api
except ImportError:
    print("Error Crítico: No se encontró el módulo Modelo/api_client.py")
    api = None

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("BitCafe System - Gestión Integral")
        self.setMinimumSize(1200, 820)
        
        # Definimos la ruta del logo usando resource_path para el ejecutable
        self.ruta_logo = resource_path(os.path.join("Vista", "assets", "taza.png"))
        
        # Validar existencia del logo para depuración
        if not os.path.exists(self.ruta_logo):
            print(f"AVISO: El recurso no existe en: {self.ruta_logo}")

        # --- INICIO CON PORTADA ---
        self.vista_portada = VistaPortada(self.ruta_logo)
        self.addWidget(self.vista_portada) # Index 0
        
        # Conexiones de la Portada
        self.vista_portada.solicitar_conexion.connect(self.ejecutar_autologin)
        self.vista_portada.entrar_sistema.connect(self.cambiar_a_dashboard)

        self.show()

    def ejecutar_autologin(self):
        """ Lógica de conexión automática al iniciar """
        self.vista_portada.mostrar_mensaje("Estableciendo conexión con el servidor...")
        
        if api is None:
            self.vista_portada.mostrar_error("Fallo de Modelo: API Client no inicializado.")
            return

        # Credenciales predefinidas para el sistema local
        usuario = "admin"
        clave = "12345678"

        token = api.login(usuario, clave)

        if token:
            self.vista_portada.habilitar_entrada()
        else:
            self.vista_portada.mostrar_error("Error de autenticación. Verifique servidor API.")

    def cambiar_a_dashboard(self):
        """ Carga las vistas pesadas solo cuando el usuario entra al sistema """
        self.cargar_sistema_completo()

    def cargar_sistema_completo(self):
        """ Instancia el resto de la aplicación y conecta controladores """
        # --- INSTANCIAR VISTAS ---
        self.vista_dashboard = VistaDashboard(self.ruta_logo)      # Index 1
        self.vista_manual    = VistaPedidoManual(self.ruta_logo)   # Index 2
        self.vista_pedidos   = VistaPedidos(self.ruta_logo)        # Index 3
        self.vista_menu      = VistaMenu(self.ruta_logo)           # Index 4
        self.vista_ajustes   = VistaAjustes(self.ruta_logo)        # Index 5

        # Añadir al Stack
        self.addWidget(self.vista_dashboard)
        self.addWidget(self.vista_manual)
        self.addWidget(self.vista_pedidos)
        self.addWidget(self.vista_menu)
        self.addWidget(self.vista_ajustes)

        # --- INSTANCIAR CONTROLADORES ---
        if api is not None:
            self.ctrl_menu = ControladorMenu(api, self.vista_menu) 
            self.ctrl_dashboard = ControladorDashboard(api, self.vista_dashboard)
            self.ctrl_pedidos = ControladorPedidos(api, self.vista_pedidos)
            self.ctrl_caja = ControladorPedidoManual(api, self.vista_manual)
            self.ctrl_ajustes = ControladorAjustes(
                api=api, 
                vista_ajustes=self.vista_ajustes, 
                controlador_pedido=self.ctrl_caja
            )

            # Sincronización inicial de ajustes desde el servidor
            self.vista_ajustes.cargar_datos_iniciales(api)
        else:
            print("ERROR: Controladores no cargados por falta de API.")

        # Conectar botones de la barra lateral (Navegación)
        self.conectar_navegacion()
        
        # Mover la vista al Dashboard
        self.setCurrentIndex(1)

    def conectar_navegacion(self):
        """ Vincula los botones de todas las vistas con el QStackedWidget """
        vistas_con_sidebar = [
            self.vista_dashboard, self.vista_manual, 
            self.vista_pedidos, self.vista_menu, self.vista_ajustes
        ]
        
        # Mapeo de botones a índices del Stack
        mapa_navegacion = {
            "Dashboard": 1, 
            "Pedido Manual": 2, 
            "Pedidos": 3, 
            "Menú": 4, 
            "Ajustes": 5
        }

        for vista in vistas_con_sidebar:
            if hasattr(vista, 'botones_menu'):
                for nombre_btn, indice_destino in mapa_navegacion.items():
                    if nombre_btn in vista.botones_menu:
                        btn = vista.botones_menu[nombre_btn]
                        # Usamos lambda con default value para capturar el índice correcto
                        btn.clicked.connect(lambda checked=False, idx=indice_destino: self.cambiar_pagina(idx))

                # Botón de Salida
                if "Cerrar Sesión" in vista.botones_menu:
                    vista.botones_menu["Cerrar Sesión"].clicked.connect(self.close)
        
        # Conexiones rápidas del Dashboard
        self.vista_dashboard.btn_ver.clicked.connect(lambda: self.cambiar_pagina(3)) 
        self.vista_dashboard.btn_add.clicked.connect(lambda: self.cambiar_pagina(4)) 

    def cambiar_pagina(self, indice):
        """ Cambia la vista actual y refresca estados críticos """
        self.setCurrentIndex(indice)
        
        if hasattr(self, 'ctrl_caja'):
            self.ctrl_caja.verificar_estado_tienda_visual()

# --- BLOQUE DE EJECUCIÓN CON LOG DE ERRORES ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    try:
        ventana = MainApp()
        sys.exit(app.exec())
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("ERROR CRÍTICO. Detalles en error_log.txt")
        print(traceback.format_exc())   
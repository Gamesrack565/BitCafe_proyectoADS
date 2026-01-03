# BITCAFE - VERSION 2.2 (HORARIOS SYNC)
# By: Angel A. Higuera & Gemini Partner

import sys
import os
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import QTimer

# --- Importar Vistas ---
from Vista.vista_portada import VistaPortada
from Vista.vista_dashboard import VistaDashboard
from Vista.vista_pedido_manual import VistaPedidoManual
from Vista.vista_pedidos import VistaPedidos
from Vista.vista_menu import VistaMenu
from Vista.vista_ajustes import VistaAjustes

# --- Importar Controladores ---
from Controlador.controlador_menu import ControladorMenu
from Controlador.controlador_dashboard import ControladorDashboard
from Controlador.controlador_pedidos import ControladorPedidos
from Controlador.controlador_pedido_manual import ControladorPedidoManual
from Controlador.controlador_ajustes import ControladorAjustes

# --- Importar Modelo (API) ---
try:
    from Modelo.api_client import api
except ImportError:
    print("Error: No se encontró el módulo Modelo/api_client.py")
    api = None

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("BitCafe System")
        self.resize(1200, 820)
        
        # Ruta del logo
        self.ruta_logo = os.path.join(os.path.dirname(__file__), "Vista", "assets", "taza.png")
        
        if not os.path.exists(self.ruta_logo):
            print(f"AVISO: No se encontró la imagen en: {self.ruta_logo}")

        # 1. Cargar PORTADA
        self.vista_portada = VistaPortada(self.ruta_logo)
        self.addWidget(self.vista_portada)
        
        # --- CONEXIONES CLAVE ---
        self.vista_portada.solicitar_conexion.connect(self.ejecutar_autologin)
        self.vista_portada.entrar_sistema.connect(self.cambiar_a_dashboard)

        self.show()

    def ejecutar_autologin(self):
        """Intenta conectar con usuario Admin en segundo plano"""
        self.vista_portada.mostrar_mensaje("Autenticando credenciales...")
        
        if api is None:
            self.vista_portada.mostrar_error("No se encontró el cliente API.")
            return

        usuario = "admin"
        clave = "12345678"

        token = api.login(usuario, clave)

        if token:
            self.vista_portada.habilitar_entrada()
        else:
            self.vista_portada.mostrar_error("No se pudo conectar al servidor. Verifique la API.")

    def cambiar_a_dashboard(self):
        """Función ejecutada al presionar 'Entrar'"""
        self.cargar_sistema_completo()

    def cargar_sistema_completo(self):
        """Instancia el resto de la aplicación y conecta controladores"""
        # 2. Instanciar Vistas
        self.vista_dashboard = VistaDashboard(self.ruta_logo)       # Index 1
        self.vista_manual    = VistaPedidoManual(self.ruta_logo)    # Index 2
        self.vista_pedidos   = VistaPedidos(self.ruta_logo)         # Index 3
        self.vista_menu      = VistaMenu(self.ruta_logo)            # Index 4
        self.vista_ajustes   = VistaAjustes(self.ruta_logo)         # Index 5

        # 3. Añadir Vistas al Stack
        self.addWidget(self.vista_dashboard)
        self.addWidget(self.vista_manual)
        self.addWidget(self.vista_pedidos)
        self.addWidget(self.vista_menu)
        self.addWidget(self.vista_ajustes)

        # 4. Instanciar Controladores
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

            # --- SINCRONIZACIÓN INICIAL DE AJUSTES ---
            # Llamamos a la carga de datos para que los horarios y el switch 
            # se actualicen con lo que hay en el servidor desde el inicio.
            self.vista_ajustes.cargar_datos_iniciales(api)
            
        else:
            print("AVISO CRÍTICO: El API Client no está disponible. No se cargaron controladores.")

        # 5. Conectar navegación y mostrar Dashboard
        self.conectar_navegacion()
        self.setCurrentIndex(1)

    def conectar_navegacion(self):
        todas_las_vistas = [
            self.vista_dashboard, self.vista_manual, 
            self.vista_pedidos, self.vista_menu, self.vista_ajustes
        ]
        
        mapa_navegacion = {
            "Dashboard": 1, "Pedido Manual": 2, "Pedidos": 3, "Menú": 4, "Ajustes": 5
        }

        for vista in todas_las_vistas:
            if hasattr(vista, 'botones_menu'):
                for nombre_btn, indice_destino in mapa_navegacion.items():
                    if nombre_btn in vista.botones_menu:
                        btn = vista.botones_menu[nombre_btn]
                        btn.clicked.connect(lambda checked=False, idx=indice_destino: self.cambiar_pagina(idx))

                if "Cerrar Sesión" in vista.botones_menu:
                    vista.botones_menu["Cerrar Sesión"].clicked.connect(self.close)
        
        self.vista_dashboard.btn_ver.clicked.connect(lambda: self.cambiar_pagina(3)) 
        self.vista_dashboard.btn_add.clicked.connect(lambda: self.cambiar_pagina(4)) 

    def cambiar_pagina(self, indice):
        self.setCurrentIndex(indice)
        
        # Al entrar a cualquier página, refrescamos el estado de la tienda 
        # para que el banner de "CERRADO" aparezca si el tiempo expiró.
        if hasattr(self, 'ctrl_caja'):
            self.ctrl_caja.verificar_estado_tienda_visual()

# --- BLOQUE DE EJECUCIÓN ---
if __name__ == "__main__":
    import traceback
    app = QApplication(sys.argv)
    try:
        ventana = MainApp()
        sys.exit(app.exec())
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("EL PROGRAMA CRASHEÓ. Revisa error_log.txt")
        print(traceback.format_exc())
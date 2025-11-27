#BITCAFE
#VERSION 2
#By: Angel A. Higuera

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

# --- Importar Controlador Menu ---
from Controlador.controlador_menu import ControladorMenu
from Controlador.controlador_dashboard import ControladorDashboard
from Controlador.controlador_pedidos import ControladorPedidos
from Controlador.controlador_pedido_manual import ControladorPedidoManual

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
        
        self.ruta_logo = os.path.join(os.path.dirname(__file__), "Vista", "assets", "taza.png")
        
        if not os.path.exists(self.ruta_logo):
            print(f"AVISO: No se encontró la imagen en: {self.ruta_logo}")

        # 1. Cargar PORTADA
        self.vista_portada = VistaPortada(self.ruta_logo)
        self.addWidget(self.vista_portada)
        
        # --- CONEXIONES CLAVE ---
        # A) Al iniciar, intentamos autologin
        self.vista_portada.solicitar_conexion.connect(self.ejecutar_autologin)
        # B) Cuando el usuario da clic en "Entrar" -> Cambiamos de pantalla
        # (Esto soluciona tu problema: ahora esperamos el clic)
        self.vista_portada.entrar_sistema.connect(self.cambiar_a_dashboard)

        self.show()

    def ejecutar_autologin(self):
        """Intenta conectar con usuario Admin en segundo plano"""
        self.vista_portada.mostrar_mensaje("Autenticando credenciales...")
        
        if api is None:
            self.vista_portada.mostrar_error("No se encontró el cliente API.")
            return

        # Credenciales
        usuario = "Angel"
        clave = "12345678"

        # Llamada API
        token = api.login(usuario, clave)

        if token:
            self.vista_portada.habilitar_entrada()
        else:
            self.vista_portada.mostrar_error("No se pudo conectar al servidor.")

    def cambiar_a_dashboard(self):
        """
        Esta función se ejecuta SOLO cuando el usuario presiona 'Entrar'.
        Aquí cargamos el resto del sistema.
        """
        self.cargar_sistema_completo()

    def cargar_sistema_completo(self):
        """Instancia el resto de la aplicación"""
        self.vista_dashboard = VistaDashboard(self.ruta_logo)      # Index 1
        self.vista_manual    = VistaPedidoManual(self.ruta_logo)   # Index 2
        self.vista_pedidos   = VistaPedidos(self.ruta_logo)        # Index 3
        self.vista_menu      = VistaMenu(self.ruta_logo)           # Index 4
        self.vista_ajustes   = VistaAjustes(self.ruta_logo)        # Index 5

        self.addWidget(self.vista_dashboard)
        self.addWidget(self.vista_manual)
        self.addWidget(self.vista_pedidos)
        self.addWidget(self.vista_menu)
        self.addWidget(self.vista_ajustes)

        self.ctrl_menu = ControladorMenu(self.vista_menu)
        self.ctrl_dashboard = ControladorDashboard(self.vista_dashboard)
        self.ctrl_pedidos = ControladorPedidos(self.vista_pedidos)
        self.ctrl_caja = ControladorPedidoManual(self.vista_manual)

        self.conectar_navegacion()
        self.setCurrentIndex(1)

    def conectar_navegacion(self):
        todas_las_vistas = [
            self.vista_dashboard, self.vista_manual, 
            self.vista_pedidos, self.vista_menu, self.vista_ajustes
        ]
        # Mapa de índices (Portada es 0)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainApp()
    sys.exit(app.exec())
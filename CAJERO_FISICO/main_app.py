# main_app.py
from PyQt6.QtWidgets import QApplication, QStackedWidget, QPushButton
from CAJERO_FISICO.Vista.vista_pago import VentanaPago
from CAJERO_FISICO.Vista.vista_pedidos import VentanaPedidos
from CAJERO_FISICO.Vista.vista_principal import VentanaPrincipal
import sys

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Inicializamos las vistas
        self.principal_view = VentanaPrincipal()
        self.pago_view = VentanaPago()
        self.pedidos_view = VentanaPedidos()

        # Agregamos las vistas al "stack"
        self.addWidget(self.principal_view)  # index 0
        self.addWidget(self.pago_view)       # index 1
        self.addWidget(self.pedidos_view)    # index 2

        # Conexiones de botones de la ventana principal
        self.principal_view.findChild(QPushButton, "btn_pagos").clicked.connect(self.ir_a_pago)
        self.principal_view.findChild(QPushButton, "btn_pedidos").clicked.connect(self.ir_a_pedidos)

        # Conexiones de botones de otras vistas
        self.pago_view.btn_pagar.clicked.connect(self.ir_a_pedidos)
        self.pedidos_view.btn_actualizar.clicked.connect(self.ir_a_principal)

        self.setFixedSize(800, 600)
        self.setWindowTitle("BitCafé - Interfaz")
        self.show()

    # Métodos para navegar entre vistas
    def ir_a_principal(self):
        self.setCurrentIndex(0)

    def ir_a_pago(self):
        self.setCurrentIndex(1)

    def ir_a_pedidos(self):
        self.setCurrentIndex(2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainApp()
    sys.exit(app.exec())
